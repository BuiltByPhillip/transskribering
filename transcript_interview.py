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

Understøttede formater: MP3, WAV, FLAC, OGG, M4A, WEBM
Max filstørrelse: 25MB
"""

import sys
import os
from pathlib import Path

MAX_FILE_SIZE_MB = 25

def check_file(audio_file):
    """Tjekker om filen eksisterer og er inden for størrelsesbegrænsning."""
    if not os.path.exists(audio_file):
        print(f"❌ Fejl: Filen '{audio_file}' findes ikke.")
        print(f"   Tip: Brug fuldt path, fx: python3 transcript_interview.py /Users/dig/Desktop/interview.mp3")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"❌ Fejl: Filen er for stor ({file_size_mb:.1f}MB).")
        print(f"   OpenAI Whisper API understøtter max {MAX_FILE_SIZE_MB}MB.")
        print(f"   Tip: Komprimer filen eller split den i mindre dele.")
        sys.exit(1)
    
    return file_size_mb

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
        print("   Installer med: pip install openai")
        print("   Eller på Mac: pip3 install openai")
        sys.exit(1)
    
    # Hent filstørrelse (fil er allerede tjekket i main)
    file_size = os.path.getsize(audio_file) / (1024 * 1024)
    
    # Hent API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key ikke fundet.")
        print()
        print("   Metode 1 - Som argument:")
        print(f"     python3 transcript_interview.py \"{audio_file}\" sk-DIN_KEY_HER")
        print()
        print("   Metode 2 - Som environment variable:")
        print("     export OPENAI_API_KEY=sk-DIN_KEY_HER")
        print(f"     python3 transcript_interview.py \"{audio_file}\"")
        print()
        print("   Få en API key på: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print(f"🎙️  Transkriberer '{Path(audio_file).name}' til dansk...")
    print(f"   Filstørrelse: {file_size:.1f}MB")
    print(f"   Estimeret tid: {max(1, int(file_size * 2))} sekunder")
    print()
    
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
        error_msg = str(e)
        print(f"❌ Fejl fra OpenAI API: {error_msg}")
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            print("   → Din API key er ugyldig. Tjek at den er korrekt.")
        elif "insufficient_quota" in error_msg.lower() or "429" in error_msg:
            print("   → Du har brugt din gratis kvote. Tilføj betalingsmetode på OpenAI.")
        elif "file" in error_msg.lower() and "format" in error_msg.lower():
            print("   → Filformatet understøttes ikke. Prøv at konvertere til MP3.")
        sys.exit(1)

def save_transcript(text, audio_file):
    """Gemmer transkription til en tekstfil i samme mappe som audio-filen."""
    audio_path = Path(audio_file).resolve()
    output_file = audio_path.parent / (audio_path.stem + "_transcript.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return str(output_file)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Tjek fil først (før vi prøver at importere openai)
    check_file(audio_file)
    
    try:
        text = transcribe_with_whisper(audio_file, api_key)
        output_file = save_transcript(text, audio_file)
        
        print(f"✅ Transkription færdig!")
        print(f"📄 Tekst gemt til: {output_file}")
        print(f"📊 Længde: {len(text)} tegn, ~{len(text.split())} ord")
        print()
        print("--- TRANSSKRIPTION ---")
        print()
        print(text)
        print()
        print("--- SLUT ---")
        
    except KeyboardInterrupt:
        print("\n⚠️  Afbrudt af brugeren.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Uventet fejl: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
