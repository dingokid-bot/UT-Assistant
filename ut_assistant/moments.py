"""Détection des moments clés (frustrations, insights, citations) via l'API Claude."""

from typing import Literal

import anthropic
from pydantic import BaseModel

from ut_assistant.transcribe import Transcript

DEFAULT_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Tu es un analyste UX qui repère les moments clés dans le transcript d'une session \
de test utilisateur. Le transcript est fourni segment par segment, chaque segment étant précédé de son \
horodatage au format [début s -> fin s].

Identifie les moments significatifs : frustrations, insights (compréhension ou incompréhension notable), \
et citations marquantes. Pour chaque moment, utilise les horodatages du ou des segments concernés — \
ne les invente pas, reprends exactement ceux fournis dans le transcript.

Reste sélectif : ne remonte que des moments réellement significatifs, pas chaque phrase. \
Une session de quelques minutes contient typiquement entre 3 et 10 moments clés."""


class Moment(BaseModel):
    timestamp_start: float
    timestamp_end: float
    type: Literal["frustration", "insight", "quote"]
    description: str
    citation: str


class KeyMoments(BaseModel):
    moments: list[Moment]


def _timestamped_transcript(transcript: Transcript) -> str:
    return "\n".join(
        f"[{s.start:.1f}s -> {s.end:.1f}s] {s.text.strip()}" for s in transcript.segments
    )


def detect_key_moments(transcript: Transcript, model: str = DEFAULT_MODEL) -> KeyMoments:
    """Analyse le transcript horodaté et retourne la liste des moments clés détectés."""
    client = anthropic.Anthropic()

    response = client.messages.parse(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Voici le transcript horodaté :\n\n{_timestamped_transcript(transcript)}",
        }],
        output_format=KeyMoments,
    )

    return response.parsed_output
