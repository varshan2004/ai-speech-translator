import os
import uuid
import subprocess

def download_youtube_audio(url: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")

    subprocess.run(
        [
            "yt-dlp",
            "-x",
            "--audio-format", "wav",
            "-o", output_path,
            url
        ],
        check=True
    )

    return output_path
