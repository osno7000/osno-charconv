"""
VibeVoice inference via Modal GPU
Run: python3 modal_vibevoice.py

Generates Peter/Stewie dialogue with GPU voice cloning.
Output saved to /tmp/vibevoice_modal_output.wav
"""
import modal
import os
import sys

app = modal.App("vibevoice-charconv")

# Build image with VibeVoice + flash-attn for max quality
vibevoice_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "wget")
    .run_commands(
        # Clone VibeVoice repo
        "cd /opt && git clone https://github.com/vibevoice-community/VibeVoice.git",
        # Install package
        "cd /opt/VibeVoice && pip install -e . --quiet",
        # Install extra audio libs
        "pip install soundfile librosa noisereduce --quiet",
    )
    # Mount voice files from GitHub
)

SCRIPT_TEXT = """Speaker 1: Remote work? That's basically stealing from your boss, Stewie.
Speaker 2: Fascinating. You've somehow managed to make telecommuting a moral issue.
Speaker 1: If you're home, you're watching TV. Everyone knows that.
Speaker 2: I produce more in two hours remotely than you manage in an entire week.
Speaker 1: That's because you cheat. You use your baby brain.
Speaker 2: My baby brain outperforms your adult brain by every measurable metric.
Speaker 1: See? This is why they should make everyone go back to the office.
Speaker 2: So you can micromanage incompetence in person? Riveting strategy, Peter."""


@app.function(
    gpu="A10G",
    image=vibevoice_image,
    timeout=600,
    secrets=[],
)
def run_vibevoice(
    script_text: str,
    peter_wav: bytes,
    stewie_wav: bytes,
) -> bytes:
    import os
    import sys
    import tempfile
    import subprocess
    import shutil

    tmpdir = tempfile.mkdtemp()
    print(f"Working in {tmpdir}")

    # Write voice files
    peter_path = os.path.join(tmpdir, "peter_clean.wav")
    stewie_path = os.path.join(tmpdir, "stewie_clean.wav")
    with open(peter_path, "wb") as f:
        f.write(peter_wav)
    with open(stewie_path, "wb") as f:
        f.write(stewie_wav)

    # Copy voices to VibeVoice voices dir
    voices_dir = "/opt/VibeVoice/demo/voices"
    os.makedirs(voices_dir, exist_ok=True)
    shutil.copy(peter_path, os.path.join(voices_dir, "peter_clean.wav"))
    shutil.copy(stewie_path, os.path.join(voices_dir, "stewie_clean.wav"))
    print(f"Voices installed to {voices_dir}")

    # Write script
    script_path = os.path.join(tmpdir, "script.txt")
    with open(script_path, "w") as f:
        f.write(script_text)

    # Output dir
    output_dir = os.path.join(tmpdir, "output")
    os.makedirs(output_dir)

    # Run inference
    cmd = [
        sys.executable,
        "/opt/VibeVoice/demo/inference_from_file.py",
        "--model_path", "microsoft/VibeVoice-1.5b",
        "--txt_path", script_path,
        "--speaker_names", "peter_clean", "stewie_clean",
        "--output_dir", output_dir,
        "--device", "cuda",
        "--cfg_scale", "1.3",
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:", result.stdout[-3000:])
    if result.stderr:
        print("STDERR:", result.stderr[-1000:])

    if result.returncode != 0:
        raise RuntimeError(f"VibeVoice failed with code {result.returncode}")

    # Find output WAV
    wav_files = [f for f in os.listdir(output_dir) if f.endswith(".wav")]
    if not wav_files:
        raise RuntimeError(f"No WAV in output dir. Contents: {os.listdir(output_dir)}")

    out_path = os.path.join(output_dir, wav_files[0])
    print(f"Output: {out_path} ({os.path.getsize(out_path)} bytes)")

    with open(out_path, "rb") as f:
        return f.read()


@app.local_entrypoint()
def main():
    # Load voice files from local disk
    voices_dir = "/home/osno/projects/VibeVoice/demo/voices"
    peter_path = os.path.join(voices_dir, "peter_clean.wav")
    stewie_path = os.path.join(voices_dir, "stewie_clean.wav")

    print(f"Loading voices from {voices_dir}")
    with open(peter_path, "rb") as f:
        peter_wav = f.read()
    with open(stewie_path, "rb") as f:
        stewie_wav = f.read()

    print(f"Peter: {len(peter_wav)/1024:.0f} KB | Stewie: {len(stewie_wav)/1024:.0f} KB")
    print("Sending to Modal GPU (A10G)...")

    audio_bytes = run_vibevoice.remote(
        script_text=SCRIPT_TEXT,
        peter_wav=peter_wav,
        stewie_wav=stewie_wav,
    )

    # Save output
    out_path = "/tmp/vibevoice_modal_output.wav"
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    size_mb = len(audio_bytes) / 1024 / 1024
    print(f"\n✓ Output saved: {out_path} ({size_mb:.1f} MB)")
    print("Done!")
