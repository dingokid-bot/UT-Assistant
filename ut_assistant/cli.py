"""CLI : transcrit une vidéo de session user test et en génère un résumé."""

import argparse
import dataclasses
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from ut_assistant.audio import extract_audio
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


def run(video_path: Path, output_dir: Path, model_size: str, language: str | None, claude_model: str) -> None:
    session_dir = output_dir / video_path.stem
    session_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] Extraction audio ({video_path.name})...")
    audio_path = extract_audio(video_path, session_dir / "audio.wav")

    print(f"[2/4] Transcription locale (faster-whisper, modèle '{model_size}')...")
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
        f"[3/4] Résumé (Claude, modèle '{claude_model}')...",
        summarize_session, transcript.text, model=claude_model,
    )
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"      -> {summary_path}")

    key_moments = _call_claude(
        f"[4/4] Détection des moments clés (Claude, modèle '{claude_model}')...",
        detect_key_moments, transcript, model=claude_model,
    )
    moments_path = session_dir / "moments.json"
    moments_path.write_text(key_moments.model_dump_json(indent=2), encoding="utf-8")
    print(f"      -> {moments_path}")

    print("\n" + "=" * 60)
    print(summary)

    print("\n" + "=" * 60)
    print(f"Moments clés ({len(key_moments.moments)}) :\n")
    for m in key_moments.moments:
        print(f"[{_mmss(m.timestamp_start)} - {_mmss(m.timestamp_end)}] ({m.type}) {m.description}")
        print(f'    « {m.citation} »\n')


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Transcrit et résume une session de user test.")
    parser.add_argument("video", type=Path, help="Chemin vers le fichier vidéo de la session")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Dossier de sortie (défaut: output/)")
    parser.add_argument(
        "--model-size",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Taille du modèle Whisper local (défaut: small)",
    )
    parser.add_argument("--language", default=None, help="Code langue du transcript (ex: fr). Défaut: auto-détection")
    parser.add_argument("--claude-model", default=DEFAULT_MODEL, help=f"Modèle Claude pour le résumé (défaut: {DEFAULT_MODEL})")
    args = parser.parse_args()

    if not args.video.exists():
        print(f"Erreur : fichier introuvable : {args.video}", file=sys.stderr)
        sys.exit(1)

    run(args.video, args.output_dir, args.model_size, args.language, args.claude_model)


if __name__ == "__main__":
    main()
