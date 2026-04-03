#!/usr/bin/env python3
"""
osno-charconv: gerador de vídeos de diálogo entre personagens.
Usa Fish Audio API para vozes realistas de Peter/Stewie.

Formato: Peter Griffin / Stewie Griffin debatem um tópico random/viral.
Imagem do personagem aparece enquanto fala. Fundo = gameplay footage.
"""
import json
import random
import asyncio
import subprocess
import os
import requests
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

FISH_API_URL = "https://api.fish.audio/v1/tts"
FISH_KEY_PATH = Path.home() / "mind/credentials/fish_audio_api_key.txt"

CHARACTERS = {
    "peter": {
        "name": "Peter Griffin",
        "image": "characters/peter.png",
        "voice": "en-US-GuyNeural",        # fallback edge-tts
        "rate": "-5%",
        "fish_voice_id": "e34b4e061b874623a08f41e5c4fecfb9",  # Peter Griffin Fish Audio
        "color": (70, 130, 180),
    },
    "stewie": {
        "name": "Stewie Griffin",
        "image": "characters/stewie.png",
        "voice": "en-US-ChristopherNeural",  # fallback edge-tts (Stewie)
        "rate": "+10%",
        "fish_voice_id": "e91c4f5974f149478a35affe820d02ac",  # Stewie Griffin Fish Audio
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
    """Gera diálogo Peter/Stewie sobre um tópico usando claude CLI."""
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

    result = subprocess.run(
        ["claude", "--print", "-p", prompt],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr[:200]}")

    text = result.stdout.strip()
    # limpar markdown se necessário
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    return json.loads(text)


# ── TTS ──────────────────────────────────────────────────────────────────────

def generate_tts_fish(text: str, character: str, output_path: str):
    """Gera áudio para uma linha usando Fish Audio API."""
    cfg = CHARACTERS[character]
    ref_id = cfg["fish_voice_id"]
    key = FISH_KEY_PATH.read_text().strip()

    resp = requests.post(
        FISH_API_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "reference_id": ref_id,
            "format": "mp3",
            "latency": "normal",
        },
        timeout=60,
    )

    if resp.status_code == 402:
        raise RuntimeError("Fish Audio: créditos esgotados. Recarregar em fish.audio/app/billing")
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(resp.content)


async def generate_tts_edge(text: str, character: str, output_path: str):
    """Fallback: gera áudio usando edge-tts (vozes genéricas)."""
    import edge_tts
    cfg = CHARACTERS[character]
    communicate = edge_tts.Communicate(text, voice=cfg["voice"], rate=cfg["rate"])
    await communicate.save(output_path)


def generate_all_tts(dialogue: list[dict], cache_dir: Path, engine: str = "fish"):
    """Gera TTS para todas as linhas. engine: 'fish' ou 'edge'."""
    for i, turn in enumerate(dialogue):
        out = str(cache_dir / f"line_{i:02d}.mp3")
        turn["audio"] = out
        char = turn["character"]
        text = turn["line"]
        print(f"    [{char.upper()}] {text[:50]}...")

        if engine == "fish":
            generate_tts_fish(text, char, out)
        else:
            asyncio.run(generate_tts_edge(text, char, out))

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

        audio_dur = get_audio_duration(audio_path)
        duration = audio_dur  # usar duração exacta do áudio (sem buffer que causa OSError)

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
                font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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
                font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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
    import argparse
    import time

    parser = argparse.ArgumentParser(description="osno-charconv: gera vídeo de diálogo Peter/Stewie")
    parser.add_argument("--topic", "-t", type=str, default=None, help="Tópico do diálogo (default: random)")
    parser.add_argument("--engine", choices=["fish", "edge"], default="fish", help="Motor TTS (default: fish)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Caminho do ficheiro de saída")
    args = parser.parse_args()

    topic = args.topic or random.choice(TOPICS)
    print(f"\n🎬 osno-charconv")
    print(f"   Tópico: {topic}")
    print(f"   Engine TTS: {args.engine}")

    # Gerar script
    print("  Gerando script com Claude...")
    dialogue = generate_script(topic)
    print(f"  {len(dialogue)} linhas geradas")

    # Cache dir
    cache_dir = BASE_DIR / "cache" / f"v01_{int(time.time())}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Guardar script
    with open(cache_dir / "script.json", "w") as f:
        json.dump({"topic": topic, "dialogue": dialogue}, f, indent=2)

    # TTS
    print(f"  Gerando TTS ({args.engine})...")
    dialogue = generate_all_tts(dialogue, cache_dir, engine=args.engine)
    print("  TTS completo")

    # Output path
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_path = args.output or str(BASE_DIR / "output" / f"charconv_{ts}.mp4")
    os.makedirs(Path(output_path).parent, exist_ok=True)

    # Background
    bg_files = list((BASE_DIR / "backgrounds").glob("*.mp4")) + list((BASE_DIR / "backgrounds").glob("*.webm"))
    if not bg_files:
        raise FileNotFoundError("Nenhum background encontrado em backgrounds/")
    bg_path = str(random.choice(bg_files))
    print(f"  Background: {Path(bg_path).name}")

    # Assemblar vídeo
    print("  Assemblando vídeo...")
    assemble_video(dialogue, output_path, bg_path)

    print(f"\n✅ Vídeo completo: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
