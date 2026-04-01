#!/usr/bin/env python3
"""
Teste de montagem de vídeo com diálogo hardcoded.
Valida que a lógica de vídeo funciona antes de integrar a API.
"""
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).parent

CHARACTERS = {
    "peter": {
        "name": "Peter Griffin",
        "image": str(BASE_DIR / "characters/peter.png"),
        "voice": "en-US-GuyNeural",
        "rate": "-10%",
    },
    "stewie": {
        "name": "Stewie Griffin",
        "image": str(BASE_DIR / "characters/stewie.png"),
        "voice": "en-US-ChristopherNeural",
        "rate": "+8%",
    },
}

# Script de teste hardcoded
TEST_DIALOGUE = [
    {"character": "peter", "line": "Remote work? That's basically stealing from your boss, Stewie."},
    {"character": "stewie", "line": "Fascinating. You've somehow made telecommuting a moral issue."},
    {"character": "peter", "line": "If you're home, you're watching TV. Everyone knows that."},
    {"character": "stewie", "line": "I produce more in two hours remotely than you do in a week."},
    {"character": "peter", "line": "That's because you cheat. You use your baby brain."},
    {"character": "stewie", "line": "My baby brain outperforms your adult brain by every metric."},
    {"character": "peter", "line": "See? This is why they should make everyone go back to the office."},
    {"character": "stewie", "line": "So you can micromanage incompetence in person? Riveting strategy."},
]


async def generate_tts(dialogue, cache_dir):
    import edge_tts

    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    tasks = []
    for i, turn in enumerate(dialogue):
        out = str(Path(cache_dir) / f"line_{i:02d}.mp3")
        turn["audio"] = out
        cfg = CHARACTERS[turn["character"]]
        communicate = edge_tts.Communicate(
            turn["line"],
            voice=cfg["voice"],
            rate=cfg["rate"],
        )
        tasks.append(communicate.save(out))

    await asyncio.gather(*tasks)
    print(f"  ✓ {len(dialogue)} ficheiros de áudio gerados")
    return dialogue


def get_audio_duration(path):
    import subprocess
    ffmpeg = Path.home() / ".local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
    result = subprocess.run(
        [str(ffmpeg), "-i", path, "-f", "null", "-"],
        capture_output=True, text=True
    )
    for line in result.stderr.split("\n"):
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = dur_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 3.0


def assemble_video(dialogue, output_path, bg_path):
    from moviepy import (
        VideoFileClip, ImageClip, AudioFileClip,
        CompositeVideoClip, TextClip, concatenate_videoclips,
    )

    VIDEO_W, VIDEO_H = 1080, 1920
    FPS = 30

    bg_full = VideoFileClip(bg_path).resized((VIDEO_W, VIDEO_H))
    bg_duration = bg_full.duration

    segments = []
    current_time = 0.0

    for i, turn in enumerate(dialogue):
        char = turn["character"]
        cfg = CHARACTERS[char]
        audio_clip = AudioFileClip(turn["audio"])
        duration = audio_clip.duration  # usar duração real do ficheiro de áudio

        # Background
        bg_start = current_time % max(bg_duration - duration, 1)
        bg_clip = bg_full.subclipped(bg_start, bg_start + duration)

        # Personagem
        char_clip = (
            ImageClip(cfg["image"])
            .resized(height=450)
            .with_position(("center", VIDEO_H - 580))
            .with_duration(duration)
        )

        # Nome
        name_clip = (
            TextClip(
                text=cfg["name"].upper(),
                font_size=50,
                color="yellow",
                stroke_color="black",
                stroke_width=3,
                font="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            )
            .with_position(("center", VIDEO_H - 620))
            .with_duration(duration)
        )

        # Texto da linha — wrap manual
        words = turn["line"].split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 30:
                lines.append(" ".join(cur[:-1]))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))

        txt_clip = (
            TextClip(
                text="\n".join(lines),
                font_size=62,
                color="white",
                stroke_color="black",
                stroke_width=4,
                font="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                method="caption",
                size=(VIDEO_W - 60, None),
            )
            .with_position(("center", 150))
            .with_duration(duration)
        )

        segment = CompositeVideoClip(
            [bg_clip, char_clip, name_clip, txt_clip],
            size=(VIDEO_W, VIDEO_H)
        ).with_audio(audio_clip).with_duration(duration)

        segments.append(segment)
        current_time += duration
        print(f"    [{char.upper():7}] {duration:.1f}s — {turn['line'][:40]}")

    print(f"  Concatenando {len(segments)} segmentos ({current_time:.1f}s total)...")
    final = concatenate_videoclips(segments, method="compose")

    print(f"  Renderizando para {output_path}...")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        logger=None,
    )
    print(f"  ✓ Feito!")


def main():
    print("\n🎬 osno-charconv — teste de montagem")
    print(f"   {len(TEST_DIALOGUE)} linhas de diálogo")

    cache_dir = str(BASE_DIR / "cache" / "test_01")

    print("  Gerando TTS...")
    dialogue = asyncio.run(generate_tts(TEST_DIALOGUE, cache_dir))

    output = str(BASE_DIR / "output" / "test_charconv.mp4")
    Path(output).parent.mkdir(exist_ok=True)
    bg = str(BASE_DIR / "backgrounds" / "minecraft_bg.mp4")

    print("  Assemblando vídeo:")
    assemble_video(dialogue, output, bg)

    import os
    size = os.path.getsize(output) / 1024 / 1024
    print(f"\n✅ Sucesso! {output} ({size:.1f}MB)")


if __name__ == "__main__":
    main()
