"""Extraction de clips vidéo aux moments clés identifiés, via ffmpeg."""

import subprocess
from pathlib import Path

from ut_assistant.moments import KeyMoments

DEFAULT_PADDING_SECONDS = 2.0


def extract_clips(
    video_path: Path,
    key_moments: KeyMoments,
    output_dir: Path,
    padding: float = DEFAULT_PADDING_SECONDS,
) -> list[Path]:
    """Découpe un clip par moment clé, avec une marge avant/après pour garder le contexte."""
    output_dir.mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for i, moment in enumerate(key_moments.moments, start=1):
        start = max(0.0, moment.timestamp_start - padding)
        duration = (moment.timestamp_end - moment.timestamp_start) + 2 * padding

        clip_path = output_dir / f"clip_{i:02d}_{moment.type}.mp4"
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", str(video_path),
                "-t", str(duration),
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac",
                str(clip_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Échec de l'extraction du clip {i} (ffmpeg) :\n{result.stderr}")

        clip_paths.append(clip_path)

    return clip_paths
