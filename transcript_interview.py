#!/usr/bin/env python3
"""
Interview Transcription Script
Transkriberer audio-filer til dansk tekst ved hjælp af OpenAI Whisper API

Installation:
    pip install openai pydub

Brug:
    python3 transcript_interview.py <audiofile.wav> [openai_api_key]

Eksempel:
    python3 transcript_interview.py interview.wav
    python3 transcript_interview.py interview.mp3 sk-...
    python3 transcript_interview.py huge_recording.mp3  # Auto-split hvis >25MB

Understøttede formater: MP3, WAV, FLAC, OGG, M4A, WEBM
Støtter nu automatisk splitting af filer >25MB
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

MAX_FILE_SIZE_MB = 25

def check_file(audio_file):
    """Tjekker om filen eksisterer."""
    if not os.path.exists(audio_file):
        print(f"❌ Fejl: Filen '{audio_file}' findes ikke.")
        print(f"   Tip: Brug fuldt path, fx: python3 transcript_interview.py /Users/dig/Desktop/interview.mp3")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    return file_size_mb

def split_audio(audio_file, max_size_mb=MAX_FILE_SIZE_MB):
    """
    Splitter audio-fil i mindre chunks hvis den er større end max_size_mb.
    Bruger pydub til at læse filen og dele den op.
    
    Returns:
        Liste af chunk-filer (stier), eller None hvis filen er lille nok
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        print("❌ pydub ikke installeret. Kan ikke splitte store filer.")
        print("   Installer med: pip install pydub")
        print("   (Kræver også ffmpeg: brew install ffmpeg på Mac, apt install ffmpeg på Linux)")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        print(f"✓ Filstørrelse OK ({file_size_mb:.1f}MB)")
        return None
    
    print(f"📊 Fil er {file_size_mb:.1f}MB - splitter i {max_size_mb}MB chunks...")
    
    try:
        # Detektér format baseret på filendelse
        audio = AudioSegment.from_file(audio_file)
        total_duration_ms = len(audio)
        
        # Beregn hvor meget vi kan have per chunk (baseret på filstørrelse)
        bytes_per_chunk = max_size_mb * 1024 * 1024
        chunk_duration_ms = int((total_duration_ms / os.path.getsize(audio_file)) * bytes_per_chunk)
        
        chunks = []
        temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
        
        print(f"   Samlet længde: {total_duration_ms // 1000} sekunder")
        print(f"   Chunk længde: ~{chunk_duration_ms // 1000} sekunder")
        
        chunk_num = 1
        start_ms = 0
        
        while start_ms < total_duration_ms:
            end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
            chunk = audio[start_ms:end_ms]
            
            # Bestem output-format baseret på input
            ext = Path(audio_file).suffix.lower()
            if ext in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.webm']:
                output_format = ext[1:]  # Fjern punktum
            else:
                output_format = 'mp3'
            
            chunk_file = os.path.join(temp_dir, f"chunk_{chunk_num:03d}{ext}")
            chunk.export(chunk_file, format=output_format)
            chunks.append(chunk_file)
            
            chunk_size_mb = os.path.getsize(chunk_file) / (1024 * 1024)
            print(f"   Chunk {chunk_num}: {chunk_size_mb:.1f}MB ({(end_ms - start_ms) // 1000}s)")
            
            start_ms = end_ms
            chunk_num += 1
        
        return chunks, temp_dir
        
    except Exception as e:
        print(f"❌ Fejl ved splitting: {e}")
        print("   Sørg for at ffmpeg er installeret:")
        print("   - Mac: brew install ffmpeg")
        print("   - Linux: apt install ffmpeg")
        sys.exit(1)

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
    
    print(f"🎙️  Transkriberer '{Path(audio_file).name}'...")
    print(f"   Filstørrelse: {file_size:.1f}MB")
    
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
    
    temp_dir = None
    chunks = None
    
    try:
        # Check if file needs splitting
        split_result = split_audio(audio_file)
        
        if split_result is not None:
            chunks, temp_dir = split_result
            print(f"✅ Split i {len(chunks)} chunks\n")
            
            # Transcribe each chunk
            all_transcripts = []
            for i, chunk_file in enumerate(chunks, 1):
                print(f"Transkriberer chunk {i}/{len(chunks)}...")
                text = transcribe_with_whisper(chunk_file, api_key)
                all_transcripts.append(text)
                print(f"  ✓ Chunk {i} færdig\n")
            
            # Combine transcripts with spacing
            full_text = "\n\n".join(all_transcripts)
        else:
            # File is small enough, transcribe directly
            print()
            full_text = transcribe_with_whisper(audio_file, api_key)
        
        output_file = save_transcript(full_text, audio_file)
        
        print(f"\n✅ Transkription færdig!")
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
    finally:
        # Clean up temporary chunk files
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Oprenset chunk-filer")

if __name__ == "__main__":
    main()
