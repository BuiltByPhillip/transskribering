#!/usr/bin/env python3
"""
Interview Transcription Script
Transcribes audio files to English text using OpenAI Whisper API

Installation:
    pip install openai

Usage:
    python3 transcript_interview.py <audiofile.mp3> [openai_api_key]
    
Example:
    python3 transcript_interview.py interview.mp3
    python3 transcript_interview.py huge_100mb_recording.mp3  # Auto-split if >25MB

Supported formats: MP3, WAV, FLAC, OGG, M4A, WEBM
Works with files of any size.
"""

import sys
import os
from pathlib import Path

MAX_FILE_SIZE_MB = 25

def check_file(audio_file):
    """Check if file exists."""
    if not os.path.exists(audio_file):
        print(f"❌ Error: File '{audio_file}' not found.")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    return file_size_mb

def split_audio_file(audio_file, max_size_mb=MAX_FILE_SIZE_MB):
    """
    Split audio file into byte-chunks if larger than max_size_mb.
    Handles file as binary - no decoding needed.
    
    Returns:
        List of byte-chunks, or None if file is small enough
    """
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        return None
    
    chunk_size_bytes = max_size_mb * 1024 * 1024
    chunks = []
    
    print(f"📊 File is {file_size_mb:.1f}MB - splitting into {max_size_mb}MB chunks...")
    
    with open(audio_file, 'rb') as f:
        chunk_num = 1
        while True:
            chunk = f.read(chunk_size_bytes)
            if not chunk:
                break
            chunks.append(chunk)
            print(f"   Chunk {chunk_num}: {len(chunk) / (1024 * 1024):.1f}MB")
            chunk_num += 1
    
    print(f"✅ Split into {len(chunks)} chunks\n")
    return chunks

def transcribe_with_whisper(audio_data, filename, api_key=None, language="en"):
    """
    Transcribe audio to text using OpenAI Whisper API.
    
    Args:
        audio_data: Either file path (str) or byte data
        filename: Name of the file (for display + Whisper format detection)
        api_key: OpenAI API key (or from OPENAI_API_KEY env var)
        language: Language code (default: "en" for English, "da" for Danish)
    
    Returns:
        Transcribed text
    """
    
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed.")
        print("   Install with: pip install openai")
        sys.exit(1)
    
    # Get API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found.")
        print()
        print("   Method 1 - As argument:")
        print(f"     python3 transcript_interview.py interview.mp3 sk-YOUR_KEY_HERE")
        print()
        print("   Method 2 - As environment variable:")
        print("     export OPENAI_API_KEY=sk-YOUR_KEY_HERE")
        print(f"     python3 transcript_interview.py interview.mp3")
        print()
        print("   Get an API key at: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    print(f"🎙️  Transcribing '{filename}'...")
    
    try:
        # If audio_data is bytes, wrap in BytesIO
        if isinstance(audio_data, bytes):
            from io import BytesIO
            audio_file = BytesIO(audio_data)
            audio_file.name = filename  # Whisper uses filename for format detection
        else:
            audio_file = open(audio_data, 'rb')
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="text"
        )
        
        if isinstance(audio_data, bytes):
            audio_file.close()
        else:
            audio_file.close()
        
        return transcript
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error from OpenAI API: {error_msg}")
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            print("   → Your API key is invalid. Check that it's correct.")
        elif "insufficient_quota" in error_msg.lower() or "429" in error_msg:
            print("   → You've used your free quota. Add a payment method on OpenAI.")
        elif "file" in error_msg.lower() and "format" in error_msg.lower():
            print("   → File format not supported. Try converting to MP3.")
        raise

def save_transcript(text, audio_file):
    """Save transcription to a text file in the same directory as the audio file."""
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
    
    # Check file first
    file_size_mb = check_file(audio_file)
    print(f"📁 File: {Path(audio_file).name} ({file_size_mb:.1f}MB)")
    
    try:
        # Check if file needs splitting
        chunks = split_audio_file(audio_file)
        
        if chunks is not None:
            # File was too large - transcribe chunks
            all_transcripts = []
            for i, chunk_data in enumerate(chunks, 1):
                print(f"Transcribing chunk {i}/{len(chunks)}...")
                text = transcribe_with_whisper(chunk_data, Path(audio_file).name, api_key)
                all_transcripts.append(text)
                print(f"  ✓ Chunk {i} done\n")
            
            # Combine transcriptions with spacing
            full_text = "\n\n".join(all_transcripts)
        else:
            # File was small enough - transcribe directly
            print()
            full_text = transcribe_with_whisper(audio_file, Path(audio_file).name, api_key)
        
        output_file = save_transcript(full_text, audio_file)
        
        print(f"✅ Transcription complete!")
        print(f"📄 Text saved to: {output_file}")
        print(f"📊 Length: {len(full_text)} characters, ~{len(full_text.split())} words")
        print()
        print("--- TRANSCRIPT ---")
        print()
        print(full_text)
        print()
        print("--- END ---")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
