#!/usr/bin/env python3
"""
Interview Transcription Script
Transkriberer audio-filer til dansk tekst ved hjælp af OpenAI Whisper API

Installation:
    pip install openai

Brug:
    python3 transcript_interview.py <audiofile.mp3> [openai_api_key]
    
Eksempel:
    python3 transcript_interview.py interview.mp3
    python3 transcript_interview.py huge_100mb_recording.mp3  # Auto-split hvis >25MB

Understøttede formater: MP3, WAV, FLAC, OGG, M4A, WEBM
Virker med filer af hvilken som helst størrelse.
"""

import sys
import os
from pathlib import Path

MAX_FILE_SIZE_MB = 25

def check_file(audio_file):
    """Tjekker om filen eksisterer."""
    if not os.path.exists(audio_file):
        print(f"❌ Fejl: Filen '{audio_file}' findes ikke.")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    return file_size_mb

def split_audio_file(audio_file, max_size_mb=MAX_FILE_SIZE_MB):
    """
    Splitter audio-fil i byte-chunks hvis den er større end max_size_mb.
    Handler filen som binary - ingen dekoding nødvendig.
    
    Returns:
        Liste af byte-chunks, eller None hvis filen er lille nok
    """
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        return None
    
    chunk_size_bytes = max_size_mb * 1024 * 1024
    chunks = []
    
    print(f"📊 Fil er {file_size_mb:.1f}MB - splitter i {max_size_mb}MB chunks...")
    
    with open(audio_file, 'rb') as f:
        chunk_num = 1
        while True:
            chunk = f.read(chunk_size_bytes)
            if not chunk:
                break
            chunks.append(chunk)
            print(f"   Chunk {chunk_num}: {len(chunk) / (1024 * 1024):.1f}MB")
            chunk_num += 1
    
    print(f"✅ Split i {len(chunks)} chunks\n")
    return chunks

def transcribe_with_whisper(audio_data, filename, api_key=None):
    """
    Transkriberer audio til dansk tekst ved hjælp af OpenAI Whisper API.
    
    Args:
        audio_data: Enten filpath (str) eller byte-data
        filename: Navn på filen (for display + Whisper format detection)
        api_key: OpenAI API key (eller fra OPENAI_API_KEY env var)
    
    Returns:
        Transkriberet tekst
    """
    
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package ikke installeret.")
        print("   Installer med: pip install openai")
        sys.exit(1)
    
    # Hent API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key ikke fundet.")
        print()
        print("   Metode 1 - Som argument:")
        print(f"     python3 transcript_interview.py interview.mp3 sk-DIN_KEY_HER")
        print()
        print("   Metode 2 - Som environment variable:")
        print("     export OPENAI_API_KEY=sk-DIN_KEY_HER")
        print(f"     python3 transcript_interview.py interview.mp3")
        print()
        print("   Få en API key på: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print(f"🎙️  Transkriberer '{filename}'...")
    
    try:
        # Hvis audio_data er bytes, skal vi luge den ind som BytesIO
        if isinstance(audio_data, bytes):
            from io import BytesIO
            audio_file = BytesIO(audio_data)
            audio_file.name = filename  # Whisper bruger filnavnet til format detection
        else:
            audio_file = open(audio_data, 'rb')
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="da",  # Dansk
            response_format="text"
        )
        
        if isinstance(audio_data, bytes):
            audio_file.close()
        else:
            audio_file.close()
        
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
        raise

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
    
    # Tjek fil først
    file_size_mb = check_file(audio_file)
    print(f"📁 Fil: {Path(audio_file).name} ({file_size_mb:.1f}MB)")
    
    try:
        # Check if file needs splitting
        chunks = split_audio_file(audio_file)
        
        if chunks is not None:
            # Fil var for stor - transcriber chunks
            all_transcripts = []
            for i, chunk_data in enumerate(chunks, 1):
                print(f"Transkriberer chunk {i}/{len(chunks)}...")
                text = transcribe_with_whisper(chunk_data, Path(audio_file).name, api_key)
                all_transcripts.append(text)
                print(f"  ✓ Chunk {i} færdig\n")
            
            # Kombinér transskriptioner med mellemrum
            full_text = "\n\n".join(all_transcripts)
        else:
            # Fil var lille nok - transcriber direkte
            print()
            full_text = transcribe_with_whisper(audio_file, Path(audio_file).name, api_key)
        
        output_file = save_transcript(full_text, audio_file)
        
        print(f"✅ Transkription færdig!")
        print(f"📄 Tekst gemt til: {output_file}")
        print(f"📊 Længde: {len(full_text)} tegn, ~{len(full_text.split())} ord")
        print()
        print("--- TRANSSKRIPTION ---")
        print()
        print(full_text)
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
