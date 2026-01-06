import os
import uuid
import subprocess

def download_youtube_audio(url: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    uid = str(uuid.uuid4())

    temp_audio = os.path.join(output_dir, uid + ".webm")
    final_wav = os.path.join(output_dir, uid + ".wav")

    # Step 1: Download bestaudio WITHOUT conversion
    subprocess.run(
        [
            "yt-dlp",
            "-f", "bestaudio",
            "-o", temp_audio,
            url
        ],
        check=True
    )

    # Step 2: Explicit FFmpeg conversion (robust)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", temp_audio,
            "-ar", "16000",
            "-ac", "1",
            final_wav
        ],
        check=True
    )

    # Step 3: Cleanup temp file
    os.remove(temp_audio)

    return final_wav
