#!/usr/bin/env python3
"""
osno-charconv: gerador de vídeos de diálogo entre personagens.
Protótipo com edge-tts (vozes genéricas) — upgrade para Fish Audio API later.

Formato: Peter Griffin / Stewie Griffin debatem um tópico random/viral.
Imagem do personagem aparece enquanto fala. Fundo = gameplay footage.
"""
import json
import random
import asyncio
import subprocess
import os
from pathlib import Path

import anthropic

# ── Config ──────────────────────────────────────────────────────────────────

CHARACTERS = {
    "peter": {
        "name": "Peter Griffin",
        "image": "characters/peter.png",
        "voice": "en-US-GuyNeural",   # voz masculina grave
        "rate": "-5%",                 # mais lento, mais estúpido
        "color": (70, 130, 180),
    },
    "stewie": {
        "name": "Stewie Griffin",
        "image": "characters/stewie.png",
        "voice": "en-US-RyanMultilingualNeural",  # voz mais articulada
        "rate": "+10%",                             # ligeiramente mais rápido
        "color": (200, 60, 60),
    },
}

TOPICS = [
    "Why Peter thinks the moon landing was staged",
    "Stewie explains why gym culture is cringe",
    "Peter's terrible investment advice vs Stewie's actual finance knowledge",
    "Why Peter thinks remote work is cheating",
    "Stewie roasts Peter's diet",
    "Peter discovers crypto, Stewie has seen it all before",
    "Why Peter thinks AI will never replace him (Stewie disagrees)",
    "Peter's hot take on why fast food is a constitutional right",
]

BASE_DIR = Path(__file__).parent

# ── Script Generation ────────────────────────────────────────────────────────

def generate_script(topic: str, num_lines: int = 12) -> list[dict]:
    """Gera diálogo Peter/Stewie sobre um tópico usando Claude."""
    client = anthropic.Anthropic()

    prompt = f"""Generate a funny back-and-forth dialogue between Peter Griffin and Stewie Griffin about: "{topic}"

Rules:
- Exactly {num_lines} lines total, alternating between Peter and Stewie
- Start with Peter
- Peter speaks like a dumb, confident idiot (short sentences, bad reasoning, pop culture refs)
- Stewie speaks like a condescending genius baby (sophisticated vocabulary, sharp wit, slight British accent)
- Each line max 20 words. Short and punchy.
- No stage directions, just dialogue
- Make it funny and slightly controversial/edgy

Return ONLY valid JSON array, no other text:
[
  {{"character": "peter", "line": "..."}},
  {{"character": "stewie", "line": "..."}},
  ...
]"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    # limpar markdown se necessário
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    return json.loads(text)


# ── TTS ──────────────────────────────────────────────────────────────────────

async def generate_tts_line(text: str, character: str, output_path: str):
    """Gera áudio para uma linha usando edge-tts."""
    import edge_tts

    cfg = CHARACTERS[character]
    communicate = edge_tts.Communicate(
        text,
        voice=cfg["voice"],
        rate=cfg["rate"],
    )
    await communicate.save(output_path)


async def generate_all_tts(dialogue: list[dict], cache_dir: Path):
    """Gera TTS para todas as linhas."""
    tasks = []
    for i, turn in enumerate(dialogue):
        out = str(cache_dir / f"line_{i:02d}.mp3")
        turn["audio"] = out
        tasks.append(generate_tts_line(turn["line"], turn["character"], out))

    await asyncio.gather(*tasks)
    return dialogue


# ── Video Assembly ────────────────────────────────────────────────────────────

def get_audio_duration(path: str) -> float:
    """Duração do áudio em segundos via ffprobe."""
    ffmpeg = Path.home() / ".local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
    result = subprocess.run(
        [str(ffmpeg), "-i", path, "-f", "null", "-"],
        capture_output=True, text=True
    )
    # parse duration from stderr
    for line in result.stderr.split("\n"):
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 3.0


def assemble_video(dialogue: list[dict], output_path: str, bg_path: str):
    """Monta o vídeo final com moviepy."""
    from moviepy import (
        VideoFileClip, ImageClip, AudioFileClip,
        CompositeVideoClip, TextClip, concatenate_videoclips,
        ColorClip,
    )
    from PIL import Image
    import numpy as np

    VIDEO_W, VIDEO_H = 1080, 1920
    FPS = 30

    # Carregar background
    bg_full = VideoFileClip(bg_path).resized((VIDEO_W, VIDEO_H))
    bg_duration = bg_full.duration

    segments = []
    current_time = 0.0

    for i, turn in enumerate(dialogue):
        char = turn["character"]
        cfg = CHARACTERS[char]
        audio_path = turn["audio"]
        text = turn["line"]

        duration = get_audio_duration(audio_path) + 0.3  # pequeno buffer

        # Clip de background (loop se necessário)
        start = current_time % (bg_duration - duration) if bg_duration > duration else 0
        bg_clip = bg_full.subclipped(start, start + duration)

        # Imagem do personagem
        char_img_path = str(BASE_DIR / cfg["image"])
        char_img = (
            ImageClip(char_img_path)
            .resized(height=500)
            .with_position(("center", VIDEO_H - 600))
            .with_duration(duration)
        )

        # Texto (legenda)
        # Dividir em linhas de max 30 chars
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 28:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        display_text = "\n".join(lines)

        txt_clip = (
            TextClip(
                text=display_text,
                font_size=60,
                color="white",
                stroke_color="black",
                stroke_width=3,
                font="Arial-Bold",
                method="caption",
                size=(VIDEO_W - 80, None),
            )
            .with_position(("center", 200))
            .with_duration(duration)
        )

        # Nome do personagem
        name_clip = (
            TextClip(
                text=cfg["name"].upper(),
                font_size=45,
                color="yellow",
                stroke_color="black",
                stroke_width=2,
                font="Arial-Bold",
            )
            .with_position(("center", VIDEO_H - 650))
            .with_duration(duration)
        )

        # Audio
        audio_clip = AudioFileClip(audio_path)

        # Composição
        segment = CompositeVideoClip(
            [bg_clip, char_img, txt_clip, name_clip],
            size=(VIDEO_W, VIDEO_H)
        ).with_audio(audio_clip).with_duration(duration)

        segments.append(segment)
        current_time += duration

    # Concatenar tudo
    final = concatenate_videoclips(segments, method="compose")

    print(f"  Renderizando {final.duration:.1f}s para {output_path}...")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        logger=None,
    )
    print(f"  ✓ Feito: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    topic = random.choice(TOPICS)
    print(f"\n🎬 osno-charconv")
    print(f"   Tópico: {topic}")

    # Gerar script
    print("  Gerando script...")
    dialogue = generate_script(topic)
    print(f"  {len(dialogue)} linhas geradas")
    for turn in dialogue:
        print(f"    [{turn['character'].upper()}] {turn['line'][:60]}")

    # Cache dir
    import time
    cache_dir = BASE_DIR / "cache" / f"v01_{int(time.time())}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Guardar script
    with open(cache_dir / "script.json", "w") as f:
        json.dump({"topic": topic, "dialogue": dialogue}, f, indent=2)

    # TTS
    print("  Gerando TTS...")
    dialogue = asyncio.run(generate_all_tts(dialogue, cache_dir))
    print("  TTS completo")

    # Assemblar vídeo
    output_path = str(BASE_DIR / "output" / "charconv_01.mp4")
    os.makedirs(BASE_DIR / "output", exist_ok=True)
    bg_path = str(BASE_DIR / "backgrounds" / "minecraft_bg.mp4")

    print("  Assemblando vídeo...")
    assemble_video(dialogue, output_path, bg_path)

    print(f"\n✅ Vídeo completo: {output_path}")


if __name__ == "__main__":
    main()
