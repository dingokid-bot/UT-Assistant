"""Résumé d'une session de user test via l'API Claude."""

import anthropic

DEFAULT_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Tu es un analyste UX qui aide à synthétiser des sessions de tests utilisateurs \
à partir de leur transcript brut (voix modérateur + participant non distinguées).

Produis un résumé structuré en Markdown avec les sections suivantes :

## Objectif de la session
Ce que le test semble chercher à évaluer, déduit du contenu.

## Déroulé
Un résumé chronologique bref des tâches/étapes observées.

## Points de friction
Les moments où le participant a semblé bloqué, confus, ou a exprimé une difficulté.

## Points positifs
Ce qui a bien fonctionné ou suscité une réaction positive.

## Citations marquantes
2 à 5 citations directes et représentatives extraites du transcript (verbatim).

Reste factuel et ancré dans le transcript : ne pas halluciner d'éléments qui n'y figurent pas. \
Si une section n'a pas de contenu identifiable, indique "Rien d'identifiable" plutôt que d'inventer."""


def summarize_session(transcript_text: str, model: str = DEFAULT_MODEL) -> str:
    """Envoie le transcript à Claude et retourne un résumé structuré en Markdown."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Voici le transcript à résumer :\n\n{transcript_text}"}],
    )

    return next(block.text for block in response.content if block.type == "text")
