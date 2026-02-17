#!/usr/bin/env python3
"""
Interview Transcription Script
Transkriberer audio-filer til dansk tekst ved hjælp af OpenAI Whisper API

Installation:
    pip install openai

Brug:
    python3 transcript_interview.py <audiofile.wav> [openai_api_key]

Eksempel:
    python3 transcript_interview.py interview.wav
    python3 transcript_interview.py interview.mp3 sk-...
"""

import sys
import os
from pathlib import Path

def transcribe_with_whisper(audio_file, api_key=None):
    """
    Transkriberer audio til dansk tekst ved hjælp af OpenAI Whisper API.
    
    Args:
        audio_file: Path til audio-fil (MP3, WAV, FLAC, OGG, M4A)
        api_key: OpenAI API key (eller fra OPENAI_API_KEY env var)
    
    Returns:
        Transkriberet tekst
    """
    
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package ikke installeret.")
        print("   Installer: pip install openai")
        sys.exit(1)
    
    # Check fil
    if not os.path.exists(audio_file):
        print(f"❌ Fejl: Filen '{audio_file}' findes ikke.")
        sys.exit(1)
    
    # Get API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key ikke fundet.")
        print("   Angiv via argument: python3 transcript_interview.py <file> <api_key>")
        print("   Eller env var: export OPENAI_API_KEY=sk-...")
        print("\n   Få en gratis API key på: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print(f"🎙️  Transkriberer '{audio_file}' til dansk...")
    print("   (Dette kan tage lidt tid afhængig af audio-længde)")
    
    try:
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="da",  # Dansk
                response_format="text"
            )
        return transcript
    except Exception as e:
        print(f"❌ Fejl fra OpenAI API: {e}")
        sys.exit(1)

def save_transcript(text, audio_file):
    """Gemmer transkription til en tekstfil."""
    output_file = str(Path(audio_file).stem) + "_transcript.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return output_file

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        text = transcribe_with_whisper(audio_file, api_key)
        output_file = save_transcript(text, audio_file)
        
        print(f"\n✓ Transkription færdig!")
        print(f"📄 Tekst gemt til: {output_file}")
        print(f"\n--- TRANSSKRIPTION ({len(text)} tegn) ---\n")
        print(text)
        print("\n--- SLUT ---")
        
    except KeyboardInterrupt:
        print("\n⚠️  Aflyst af brugeren.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Uventet fejl: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
