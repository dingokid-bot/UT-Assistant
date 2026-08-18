"""Extraction de la piste audio d'une vidéo via ffmpeg."""

import subprocess
from pathlib import Path


def extract_audio(video_path: Path, output_path: Path) -> Path:
    """Extrait l'audio de `video_path` en wav mono 16kHz dans `output_path`."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Échec de l'extraction audio (ffmpeg) :\n{result.stderr}")

    return output_path
