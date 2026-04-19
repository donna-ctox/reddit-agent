#!/usr/bin/env python3
"""Transcribe an audio file to WebVTT format using OpenAI Whisper."""

import sys
import argparse
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def transcribe_to_vtt(audio_path: str, model_size: str = "base", output_path: str = None, word_level: bool = False) -> str:
    try:
        import whisper
    except ImportError:
        print("Error: whisper not installed. Run: pip install openai-whisper")
        sys.exit(1)

    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    if output_path is None:
        output_path = audio_path.with_suffix(".vtt")
    else:
        output_path = Path(output_path)

    print(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    print(f"Transcribing {audio_path.name}...")
    result = model.transcribe(str(audio_path), word_timestamps=True, verbose=False)

    lines = ["WEBVTT", ""]
    cue_index = 1

    for segment in result["segments"]:
        if word_level:
            for word in segment.get("words", []):
                start = format_timestamp(word["start"])
                end = format_timestamp(word["end"])
                text = word["word"].strip()
                if text:
                    lines.append(str(cue_index))
                    lines.append(f"{start} --> {end}")
                    lines.append(text)
                    lines.append("")
                    cue_index += 1
        else:
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            if text:
                lines.append(str(cue_index))
                lines.append(f"{start} --> {end}")
                lines.append(text)
                lines.append("")
                cue_index += 1

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio to WebVTT using Whisper")
    parser.add_argument("audio", help="Path to audio file (mp3, wav, m4a, mp4, etc.)")
    parser.add_argument(
        "--model", default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size — larger = more accurate but slower (default: base)"
    )
    parser.add_argument("--output", "-o", help="Output .vtt path (default: same name as audio)")
    parser.add_argument(
        "--words", action="store_true",
        help="One cue per word instead of per segment"
    )
    args = parser.parse_args()

    transcribe_to_vtt(args.audio, args.model, args.output, args.words)


if __name__ == "__main__":
    main()
