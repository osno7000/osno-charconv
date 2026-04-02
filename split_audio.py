#!/usr/bin/env python3
"""
Utilitário para dividir o audio do VibeVoice em segmentos por linha de diálogo.

Estratégia: silence detection com librosa para encontrar pausas naturais entre linhas.
"""
import os
import sys
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path


def detect_speech_segments(
    audio_path: str,
    expected_n_segments: int,
    top_db: float = 30,
    min_silence_len: float = 0.15,
    hop_length: int = 512,
) -> list[tuple[float, float]]:
    """
    Detecta segmentos de fala num ficheiro de audio.

    Retorna lista de (start_sec, end_sec) para cada segmento.
    """
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    # Detectar intervalos de não-silêncio
    intervals = librosa.effects.split(
        y,
        top_db=top_db,
        frame_length=2048,
        hop_length=hop_length,
    )

    # Converter de frames para segundos
    segments = [(start / sr, end / sr) for start, end in intervals]

    print(f"  Encontrados {len(segments)} segmentos de fala (esperados: {expected_n_segments})")
    for i, (s, e) in enumerate(segments):
        print(f"    Segmento {i+1}: {s:.2f}s → {e:.2f}s (duração: {e-s:.2f}s)")

    return segments


def merge_close_segments(
    segments: list[tuple[float, float]],
    max_gap: float = 0.3,
) -> list[tuple[float, float]]:
    """
    Funde segmentos separados por menos de max_gap segundos.
    Útil quando uma linha tem várias pausas internas pequenas.
    """
    if not segments:
        return []

    merged = [segments[0]]
    for start, end in segments[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end <= max_gap:
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    return merged


def split_audio_by_segments(
    audio_path: str,
    segments: list[tuple[float, float]],
    output_dir: str,
    padding_sec: float = 0.05,
) -> list[str]:
    """
    Divide o audio em ficheiros separados por segmento.

    Adiciona padding_sec de silêncio antes e depois de cada segmento
    para evitar cortes abruptos.
    """
    y, sr = librosa.load(audio_path, sr=None, mono=True)
    duration = len(y) / sr

    os.makedirs(output_dir, exist_ok=True)
    output_files = []

    for i, (start, end) in enumerate(segments):
        # Adicionar padding
        start_padded = max(0.0, start - padding_sec)
        end_padded = min(duration, end + padding_sec)

        start_sample = int(start_padded * sr)
        end_sample = int(end_padded * sr)

        segment_audio = y[start_sample:end_sample]

        out_path = os.path.join(output_dir, f"segment_{i:02d}.wav")
        sf.write(out_path, segment_audio, sr)
        output_files.append(out_path)

        print(f"  Guardado: {out_path} ({end_padded - start_padded:.2f}s)")

    return output_files


def split_vibevoice_output(
    audio_path: str,
    n_lines: int,
    output_dir: str,
    top_db: float = 28,
    max_gap: float = 0.4,
) -> list[str]:
    """
    Pipeline completo: lê audio do VibeVoice, detecta segmentos, divide.

    Parâmetros:
        audio_path: caminho para o WAV gerado pelo VibeVoice
        n_lines: número de linhas de diálogo esperadas
        output_dir: directório para guardar os segmentos
        top_db: threshold de silêncio (dB abaixo do pico = silêncio)
        max_gap: gap máximo (segundos) para fundir segmentos próximos
    """
    print(f"\n Dividindo audio VibeVoice em {n_lines} segmentos...")
    print(f"  Input: {audio_path}")

    # Detectar segmentos raw
    raw_segments = detect_speech_segments(audio_path, n_lines, top_db=top_db)

    # Fundir segmentos muito próximos (pausas internas de respiração)
    merged = merge_close_segments(raw_segments, max_gap=max_gap)
    print(f"\n  Após merge: {len(merged)} segmentos")
    for i, (s, e) in enumerate(merged):
        print(f"    {i+1}: {s:.2f}s → {e:.2f}s")

    # Se o número não bate, tentar ajustar parâmetros
    if len(merged) != n_lines:
        print(f"\n  ⚠️  {len(merged)} segmentos encontrados, esperados {n_lines}")
        print(f"  Tenta ajustar top_db ou max_gap")
        # Continuar com o que temos

    # Dividir e guardar
    print(f"\n  Guardando segmentos em {output_dir}...")
    output_files = split_audio_by_segments(audio_path, merged, output_dir)

    print(f"\n  ✓ {len(output_files)} segmentos guardados")
    return output_files


if __name__ == "__main__":
    # Teste rápido com o output do VibeVoice
    audio = "/tmp/vibevoice_output/peter_stewie_test_generated.wav"
    out_dir = "/tmp/vibevoice_output/segments"

    if not os.path.exists(audio):
        print(f"Ficheiro não encontrado: {audio}")
        sys.exit(1)

    # 8 linhas de diálogo no teste
    files = split_vibevoice_output(
        audio_path=audio,
        n_lines=8,
        output_dir=out_dir,
        top_db=28,
        max_gap=0.4,
    )

    print(f"\nResultado: {len(files)} segmentos")
    for f in files:
        import soundfile as sf
        info = sf.info(f)
        print(f"  {os.path.basename(f)}: {info.duration:.2f}s")
