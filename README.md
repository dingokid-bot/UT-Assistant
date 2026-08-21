# UT-Assistant

# User Test Insight Agent

Agent qui aide à analyser des sessions de user test à partir d'extraits vidéo uploadés, pour en tirer automatiquement des insights exploitables.

## 🚧 Statut du projet

**Prototype / phase de cadrage.** Aucun code n'est encore implémenté — ce README pose les bases du projet et servira de référence au fur et à mesure de son développement.

## Contexte

Analyser des user tests manuellement (revisionner des heures de vidéo, repérer les moments clés, croiser les observations entre plusieurs sessions) prend beaucoup de temps. Cet agent vise à automatiser une partie de ce travail en s'appuyant sur des extraits vidéo de sessions de test utilisateur.

## Fonctionnalités visées

- **Résumé automatique des sessions** — générer une synthèse lisible de chaque session de user test uploadée.
- **Détection des moments clés** — repérer automatiquement les frustrations, insights et verbatims marquants dans les vidéos.
- **Rapport cross-sessions** — agréger les observations de plusieurs tests pour faire ressortir des patterns communs.
- **Extraction de clips vidéo** — isoler et exporter les extraits vidéo correspondant aux moments clés identifiés.

## Comment ça fonctionne (grandes lignes)

> À affiner au fur et à mesure du développement.

1. L'utilisateur uploade un ou plusieurs extraits vidéo de sessions de user test.
2. L'agent analyse le contenu (audio/visuel) pour identifier les moments significatifs.
3. Il génère une synthèse par session, puis un rapport consolidé si plusieurs sessions sont fournies.
4. Les clips vidéo correspondant aux moments clés peuvent être extraits individuellement.

## Stack technique

| Composant | Choix | Pourquoi |
|---|---|---|
| Langage | Python | Écosystème mature pour l'audio/vidéo et les appels API |
| Transcription | [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) | Local, gratuit, timestamps par mot (nécessaires pour les moments clés et les clips) |
| Extraction/découpe vidéo | `ffmpeg` | Standard, local, gratuit |
| Résumé / détection de moments clés | API Claude (`claude-sonnet-5`) | Raisonnement sur texte (le transcript), coût marginal car pas de vidéo envoyée |
| Stockage | Filesystem + JSON (SQLite à l'étape cross-sessions) | Pas besoin de plus pour un prototype |

Transcription 100% locale et gratuite ; seule l'étape de résumé/analyse passe par l'API Claude (clé perso, coût à l'usage sur du texte uniquement — quelques centimes par session).

## Installation / Usage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # puis renseigner ANTHROPIC_API_KEY

python -m ut_assistant analyze chemin/vers/session.mp4

# Plusieurs vidéos d'un coup :
python -m ut_assistant analyze video1.mp4 video2.mp4 video3.mp4

# Ou tout un dossier :
python -m ut_assistant analyze --dir chemin/vers/dossier
```

Sorties générées dans `output/<nom_de_la_vidéo>/` : `transcript.json` (avec timestamps), `transcript.txt`, `summary.md`, `moments.json` (moments clés horodatés : frustrations, insights, citations), et un dossier `clips/` avec un extrait vidéo par moment clé.

Options utiles de `analyze` : `--dir` (traiter tout un dossier de vidéos), `--model-size` (taille du modèle Whisper local, défaut `small`), `--language` (défaut : auto-détection), `--claude-model`, `--output-dir`, `--clip-padding` (marge en secondes autour de chaque clip, défaut 2s), `--no-clips` (désactive la découpe vidéo).

En cas de plusieurs vidéos, chaque échec (fichier corrompu, etc.) est signalé mais n'interrompt pas le traitement des suivantes — sauf une erreur de clé API, qui arrête tout de suite puisqu'elle affecterait toutes les vidéos restantes.

Une fois au moins deux sessions analysées avec `analyze`, génère un rapport consolidé qui fait ressortir les patterns communs :

```bash
python -m ut_assistant cross-report
```

Sortie : `output/cross_report.md` (patterns récurrents, points positifs partagés, divergences, citations représentatives).

## Roadmap

- [x] Définir le stack technique (langage, framework, outils de traitement vidéo/audio)
- [ ] Définir le format d'input (formats vidéo supportés, taille max, etc.)
- [x] Premier prototype : transcription + résumé d'une session unique
- [x] Détection des moments clés (frustrations, insights, quotes)
- [x] Extraction de clips vidéo
- [x] Rapport cross-sessions
- [x] Interface / mode d'interaction : CLI pour le prototype

## Contribuer

*Section à compléter selon l'audience finale du projet (usage perso, équipe, ou open source).*
