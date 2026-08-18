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

1. L'utilisateur uploade un ou plusieurs extraits vidéo de sessions de user test via la CLI.
2. `faster-whisper` transcrit l'audio en local, `pyannote.audio` effectue la diarisation (identification des locuteurs).
3. La transcription est envoyée à l'API Claude pour générer le résumé de session, détecter les moments clés (frustrations, insights, quotes) et produire le rapport cross-sessions.
4. `ffmpeg` extrait les clips vidéo correspondant aux moments clés identifiés.

## Stack technique

- **`faster-whisper`** — transcription audio, en local
- **`pyannote.audio`** — diarisation (identification des locuteurs), en local
- **API Claude (Anthropic)** — génération du résumé, détection des moments clés, rapport cross-sessions
- **`ffmpeg`** — extraction des clips vidéo
- **Python** — langage principal

> Note confidentialité : la transcription et la diarisation tournent 100% en local (gratuit, pas d'appel cloud). Le texte transcrit (pas la vidéo brute) est envoyé à l'API Claude pour l'analyse.

## Installation / Usage

*À compléter une fois la première version du code disponible.*

### Configuration

Une clé API Anthropic est nécessaire, à fournir via une variable d'environnement (ex. `ANTHROPIC_API_KEY`).

## Roadmap

- [x] Définir le stack technique
- [ ] Définir le format d'input (formats vidéo supportés, taille max, etc.)
- [ ] (1) Prototype : transcription + résumé d'une session unique
- [ ] (2) Détection des moments clés (frustrations, insights, quotes)
- [ ] (3) Extraction de clips vidéo
- [ ] (4) Rapport cross-sessions
- [ ] Interface : CLI pour le prototype ; UI web ou skill Claude envisageables ensuite

## Contribuer

*Section à compléter selon l'audience finale du projet (usage perso, équipe, ou open source).*
