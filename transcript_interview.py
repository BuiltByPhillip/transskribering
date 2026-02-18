#!/usr/bin/env python3
"""
Interview Transcription Script
Transcribes audio files to text using OpenAI Whisper API

Installation:
    pip install openai
    
    For large files (>25MB):
    brew install ffmpeg  (macOS)
    apt install ffmpeg   (Linux)
    choco install ffmpeg (Windows)

Usage:
    python3 transcript_interview.py <audiofile> [api_key] [language]

Examples:
    python3 transcript_interview.py interview.mp3
    python3 transcript_interview.py interview.mp3 da
    python3 transcript_interview.py interview.mp3 --language danish
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from io import BytesIO

MAX_CHUNK_SIZE_MB = 24
DEFAULT_LANGUAGE = "en"

LANGUAGE_ALIASES = {
    "english": "en", "danish": "da", "spanish": "es", "french": "fr",
    "german": "de", "italian": "it", "portuguese": "pt", "dutch": "nl",
    "russian": "ru", "japanese": "ja", "chinese": "zh",
}

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_file(audio_file):
    """Check if file exists."""
    if not os.path.exists(audio_file):
        print(f"❌ Error: File '{audio_file}' not found.")
        sys.exit(1)
    return os.path.getsize(audio_file) / (1024 * 1024)

def normalize_language(lang):
    """Convert language name to code."""
    if not lang:
        return DEFAULT_LANGUAGE
    lang = lang.lower().strip()
    return LANGUAGE_ALIASES.get(lang, lang if len(lang) == 2 else DEFAULT_LANGUAGE)

def get_audio_duration(audio_file):
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1:nokey=1", audio_file],
            capture_output=True, timeout=10, text=True
        )
        return float(result.stdout.strip())
    except:
        return None

def split_audio_file(audio_file, max_size_mb=MAX_CHUNK_SIZE_MB):
    """Split audio file using ffmpeg."""
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        return None
    
    if not check_ffmpeg():
        print("❌ ffmpeg not installed.")
        print()
        if sys.platform == "darwin":
            print("Install with: brew install ffmpeg")
        elif sys.platform == "linux":
            print("Install with: apt install ffmpeg")
        elif sys.platform == "win32":
            print("Install with: choco install ffmpeg")
        else:
            print("Install ffmpeg for your system")
        sys.exit(1)
    
    duration = get_audio_duration(audio_file)
    if not duration:
        print("❌ Could not determine audio duration.")
        sys.exit(1)
    
    # Calculate chunk duration
    chunk_duration = (duration / file_size_mb) * max_size_mb * 0.9
    
    print(f"📊 File is {file_size_mb:.1f}MB ({duration:.0f}s) - splitting into chunks...")
    
    temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
    chunks = []
    chunk_num = 1
    start_time = 0
    
    while start_time < duration:
        end_time = min(start_time + chunk_duration, duration)
        chunk_file = os.path.join(temp_dir, f"chunk_{chunk_num:03d}.mp3")
        
        # Use ffmpeg to extract chunk
        subprocess.run(
            ["ffmpeg", "-i", audio_file, "-ss", str(start_time), "-to", str(end_time),
             "-q:a", "9", "-n", chunk_file],
            capture_output=True, timeout=300
        )
        
        if os.path.exists(chunk_file):
            chunk_size = os.path.getsize(chunk_file) / (1024 * 1024)
            print(f"   Chunk {chunk_num}: {chunk_size:.1f}MB ({end_time - start_time:.0f}s)")
            chunks.append(chunk_file)
            chunk_num += 1
        
        start_time = end_time
    
    print(f"✅ Split into {len(chunks)} chunks\n")
    return chunks, temp_dir

def transcribe_with_whisper(audio_input, api_key=None, language=DEFAULT_LANGUAGE):
    """Transcribe using OpenAI Whisper."""
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed.")
        print(f"   {sys.executable} -m pip install openai")
        sys.exit(1)
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found.")
        print("   Set: export OPENAI_API_KEY=sk-YOUR_KEY_HERE")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    filename = Path(audio_input).name if isinstance(audio_input, str) else "audio.mp3"
    print(f"🎙️  Transcribing '{filename}' ({language.upper()})...")
    
    try:
        with open(audio_input, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="text"
            )
        return transcript
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def save_transcript(text, audio_file):
    """Save transcript to file."""
    output_file = Path(audio_file).parent / (Path(audio_file).stem + "_transcript.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return str(output_file)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_key = None
    language = DEFAULT_LANGUAGE
    
    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        if arg.startswith("--language"):
            language = normalize_language(arg.split("=")[-1] if "=" in arg else (sys.argv[i+1] if i+1 < len(sys.argv) else ""))
        elif arg.startswith("sk-"):
            api_key = arg
        else:
            language = normalize_language(arg)
    
    file_size_mb = check_file(audio_file)
    print(f"📁 File: {Path(audio_file).name} ({file_size_mb:.1f}MB)")
    
    temp_dir = None
    try:
        result = split_audio_file(audio_file)
        
        if result:
            chunks, temp_dir = result
            all_transcripts = []
            for i, chunk_file in enumerate(chunks, 1):
                print(f"Transcribing chunk {i}/{len(chunks)}...")
                text = transcribe_with_whisper(chunk_file, api_key, language)
                all_transcripts.append(text)
                print(f"  ✓ Chunk {i} done\n")
            full_text = "\n\n".join(all_transcripts)
        else:
            full_text = transcribe_with_whisper(audio_file, api_key, language)
        
        output_file = save_transcript(full_text, audio_file)
        
        print(f"✅ Transcription complete!")
        print(f"📄 Text saved to: {output_file}")
        print(f"📊 Length: {len(full_text)} characters, ~{len(full_text.split())} words")
        print()
        print("--- TRANSCRIPT ---")
        print(full_text)
        print("--- END ---")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(1)
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
