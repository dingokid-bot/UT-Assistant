"""Rapport cross-sessions : agrège plusieurs sessions déjà analysées pour en tirer des patterns communs."""

from pathlib import Path

import anthropic

DEFAULT_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Tu es un analyste UX qui synthétise plusieurs sessions de test utilisateur déjà résumées \
individuellement, pour en tirer un rapport consolidé.

Pour chaque session fournie, tu disposes de son résumé et de ses moments clés (frustrations, insights, citations).

Produis un rapport en Markdown avec les sections suivantes :

## Patterns récurrents
Les frictions ou comportements qui reviennent dans plusieurs sessions (précise combien de sessions sur le total \
et lesquelles).

## Points positifs partagés
Ce qui a bien fonctionné de façon cohérente entre les sessions.

## Divergences notables
Les cas où les sessions se contredisent, ou où une session se distingue nettement des autres.

## Citations représentatives
2 à 5 citations, si possible de sessions différentes, qui illustrent les patterns identifiés.

Reste factuel et ancré dans le contenu fourni : ne pas halluciner d'éléments qui n'y figurent pas. \
Précise toujours de quelle(s) session(s) provient chaque observation."""


def _load_session(session_dir: Path) -> str | None:
    summary_path = session_dir / "summary.md"
    moments_path = session_dir / "moments.json"
    if not summary_path.exists():
        return None

    parts = [f"# Session : {session_dir.name}", "", "## Résumé", summary_path.read_text(encoding="utf-8")]
    if moments_path.exists():
        parts += ["", "## Moments clés (JSON)", moments_path.read_text(encoding="utf-8")]
    return "\n".join(parts)


def collect_sessions(output_dir: Path) -> list[str]:
    """Retourne le contenu formaté de chaque session analysée trouvée dans output_dir."""
    if not output_dir.is_dir():
        return []

    sessions = []
    for session_dir in sorted(output_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        content = _load_session(session_dir)
        if content:
            sessions.append(content)
    return sessions


def generate_cross_report(sessions: list[str], model: str = DEFAULT_MODEL) -> str:
    """Envoie les sessions agrégées à Claude et retourne le rapport cross-sessions en Markdown."""
    client = anthropic.Anthropic()

    combined = "\n\n---\n\n".join(sessions)
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Voici les sessions à comparer ({len(sessions)} au total) :\n\n{combined}",
        }],
    )

    return next(block.text for block in response.content if block.type == "text")
