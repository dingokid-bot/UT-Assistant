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

*À définir.*

## Installation / Usage

*À compléter une fois la première version du code disponible.*

## Roadmap

- [ ] Définir le stack technique (langage, framework, outils de traitement vidéo/audio)
- [ ] Définir le format d'input (formats vidéo supportés, taille max, etc.)
- [ ] Premier prototype : transcription + résumé d'une session unique
- [ ] Détection des moments clés (frustrations, insights, quotes)
- [ ] Extraction de clips vidéo
- [ ] Rapport cross-sessions
- [ ] Interface / mode d'interaction (CLI, web, skill Claude, etc.)

## Contribuer

*Section à compléter selon l'audience finale du projet (usage perso, équipe, ou open source).*
