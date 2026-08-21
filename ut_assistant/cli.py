"""CLI : transcrit une vidéo de session user test et en génère un résumé."""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from ut_assistant.audio import extract_audio
from ut_assistant.clips import DEFAULT_PADDING_SECONDS, extract_clips
from ut_assistant.cross_report import collect_sessions, generate_cross_report
from ut_assistant.moments import detect_key_moments
from ut_assistant.summarize import DEFAULT_MODEL, summarize_session
from ut_assistant.transcribe import transcribe


def _call_claude(step_label: str, fn, *args, **kwargs):
    print(step_label)
    try:
        return fn(*args, **kwargs)
    except (anthropic.AuthenticationError, TypeError) as e:
        if isinstance(e, TypeError) and "authentication" not in str(e).lower():
            raise
        print(
            "\nErreur : clé API Anthropic invalide ou absente. "
            "Définis la variable d'environnement ANTHROPIC_API_KEY (ou un fichier .env, voir .env.example).",
            file=sys.stderr,
        )
        sys.exit(1)


def _mmss(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def run(
    video_path: Path,
    output_dir: Path,
    model_size: str,
    language: str | None,
    claude_model: str,
    clip_padding: float,
    no_clips: bool,
) -> None:
    session_dir = output_dir / video_path.stem
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] Extraction audio ({video_path.name})...")
    audio_path = extract_audio(video_path, session_dir / "audio.wav")

    print(f"[2/5] Transcription locale (faster-whisper, modèle '{model_size}')...")
    transcript = transcribe(audio_path, model_size=model_size, language=language)

    transcript_json_path = session_dir / "transcript.json"
    transcript_json_path.write_text(
        json.dumps(dataclasses.asdict(transcript), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    transcript_txt_path = session_dir / "transcript.txt"
    transcript_txt_path.write_text(transcript.text, encoding="utf-8")
    print(f"      -> {transcript_json_path}")
    print(f"      -> {transcript_txt_path}")

    summary = _call_claude(
        f"[3/5] Résumé (Claude, modèle '{claude_model}')...",
        summarize_session, transcript.text, model=claude_model,
    )
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"      -> {summary_path}")

    key_moments = _call_claude(
        f"[4/5] Détection des moments clés (Claude, modèle '{claude_model}')...",
        detect_key_moments, transcript, model=claude_model,
    )
    moments_path = session_dir / "moments.json"
    moments_path.write_text(key_moments.model_dump_json(indent=2), encoding="utf-8")
    print(f"      -> {moments_path}")

    if no_clips:
        print("[5/5] Extraction de clips vidéo... ignorée (--no-clips)")
    else:
        print(f"[5/5] Extraction de clips vidéo (marge {clip_padding}s)...")
        clip_paths = extract_clips(video_path, key_moments, session_dir / "clips", padding=clip_padding)
        for clip_path in clip_paths:
            print(f"      -> {clip_path}")

    print("\n" + "=" * 60)
    print(summary)

    print("\n" + "=" * 60)
    print(f"Moments clés ({len(key_moments.moments)}) :\n")
    for m in key_moments.moments:
        print(f"[{_mmss(m.timestamp_start)} - {_mmss(m.timestamp_end)}] ({m.type}) {m.description}")
        print(f'    « {m.citation} »\n')


def run_cross_report(output_dir: Path, claude_model: str) -> None:
    sessions = collect_sessions(output_dir)
    if len(sessions) < 2:
        print(
            f"Erreur : il faut au moins 2 sessions déjà analysées dans '{output_dir}' pour générer un rapport "
            f"cross-sessions (trouvé : {len(sessions)}). Lance d'abord 'analyze' sur plusieurs vidéos.",
            file=sys.stderr,
        )
        sys.exit(1)

    report = _call_claude(
        f"Génération du rapport cross-sessions ({len(sessions)} sessions, Claude modèle '{claude_model}')...",
        generate_cross_report, sessions, model=claude_model,
    )

    report_path = output_dir / "cross_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"      -> {report_path}")

    print("\n" + "=" * 60)
    print(report)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Analyse des sessions de user test.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Transcrit et analyse une session (vidéo unique)")
    analyze_parser.add_argument("video", type=Path, help="Chemin vers le fichier vidéo de la session")
    analyze_parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Dossier de sortie (défaut: output/)")
    analyze_parser.add_argument(
        "--model-size",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Taille du modèle Whisper local (défaut: small)",
    )
    analyze_parser.add_argument("--language", default=None, help="Code langue du transcript (ex: fr). Défaut: auto-détection")
    analyze_parser.add_argument("--claude-model", default=DEFAULT_MODEL, help=f"Modèle Claude pour le résumé (défaut: {DEFAULT_MODEL})")
    analyze_parser.add_argument(
        "--clip-padding",
        type=float,
        default=DEFAULT_PADDING_SECONDS,
        help=f"Marge en secondes ajoutée avant/après chaque clip (défaut: {DEFAULT_PADDING_SECONDS})",
    )
    analyze_parser.add_argument("--no-clips", action="store_true", help="Ne pas extraire de clips vidéo")

    cross_parser = subparsers.add_parser(
        "cross-report", help="Génère un rapport consolidé à partir des sessions déjà analysées"
    )
    cross_parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Dossier contenant les sessions analysées (défaut: output/)")
    cross_parser.add_argument("--claude-model", default=DEFAULT_MODEL, help=f"Modèle Claude pour le rapport (défaut: {DEFAULT_MODEL})")

    args = parser.parse_args()

    if args.command == "analyze":
        if not args.video.exists():
            print(f"Erreur : fichier introuvable : {args.video}", file=sys.stderr)
            sys.exit(1)
        run(
            args.video, args.output_dir, args.model_size, args.language, args.claude_model,
            args.clip_padding, args.no_clips,
        )
    elif args.command == "cross-report":
        run_cross_report(args.output_dir, args.claude_model)


if __name__ == "__main__":
    main()
