#!/usr/bin/env python3
import os
import glob
from multiprocessing import Pool, cpu_count


def process_file(audio_file):
    base_name = os.path.splitext(audio_file)[0]
    name = os.path.basename(base_name)
    jpeg_file = f"{base_name}.jpg"

    if not os.path.exists(jpeg_file):
        return f"SKIP: No jpg found for {name}"

    output_file = f"{name}.mp4"

    if os.path.exists(output_file):
        return f"SKIP: Output exists: {name}.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        jpeg_file,
        "-i",
        audio_file,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        output_file,
    ]

    import subprocess

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return f"OK: {name}.mp4"
    else:
        return f"FAIL: {name} - {result.stderr[:200]}"


def main():
    audio_patterns = ["*.mp3", "*.flac", "*.MP3", "*.FLAC"]
    audio_files = []
    for pattern in audio_patterns:
        audio_files.extend(glob.glob(pattern))

    if not audio_files:
        print("No audio files found")
        return

    with Pool(cpu_count()) as pool:
        results = pool.map(process_file, audio_files)

    for r in results:
        print(r)


if __name__ == "__main__":
    main()
