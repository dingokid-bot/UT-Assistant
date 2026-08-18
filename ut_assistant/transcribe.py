"""Transcription audio locale via faster-whisper."""

from dataclasses import dataclass, field
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    language: str
    duration: float
    segments: list[TranscriptSegment] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(segment.text.strip() for segment in self.segments)


def transcribe(audio_path: Path, model_size: str = "small", language: str | None = None) -> Transcript:
    """Transcrit `audio_path` en local avec faster-whisper.

    model_size : tiny | base | small | medium | large-v3 (compromis vitesse/qualité).
    language   : code langue (ex. "fr"). None = détection automatique.
    """
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=True,
    )

    segments = [
        TranscriptSegment(start=s.start, end=s.end, text=s.text)
        for s in segments_iter
    ]

    return Transcript(
        language=info.language,
        duration=info.duration,
        segments=segments,
    )
