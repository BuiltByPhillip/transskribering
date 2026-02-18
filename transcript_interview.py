#!/usr/bin/env python3
"""
Interview Transcription Script
Transcribes audio files to text using OpenAI Whisper API

Installation:
    pip install openai
    
    For large files (>25MB), also install:
    pip install pydub imageio-ffmpeg

Usage:
    python3 transcript_interview.py <audiofile> [api_key] [language]

Examples:
    python3 transcript_interview.py interview.mp3
    python3 transcript_interview.py interview.mp3 da
    python3 transcript_interview.py interview.mp3 --language danish
    python3 transcript_interview.py large_file.m4a sk-KEY da

Languages: en, da, es, fr, de, it, pt, nl, ru, ja, zh, etc.
"""

import sys
import os
from pathlib import Path
from io import BytesIO

MAX_CHUNK_SIZE_MB = 24  # OpenAI limit is 25MB, use 24 for safety
DEFAULT_LANGUAGE = "en"

# Common language codes
LANGUAGE_ALIASES = {
    "english": "en",
    "danish": "da",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "dutch": "nl",
    "russian": "ru",
    "japanese": "ja",
    "chinese": "zh",
}

def setup_ffmpeg():
    """Configure pydub to use imageio-ffmpeg's bundled ffmpeg."""
    try:
        import imageio_ffmpeg
        from pydub import AudioSegment
        
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        AudioSegment.converter = ffmpeg_path
        AudioSegment.ffprobe = ffmpeg_path
        return True
    except Exception as e:
        print(f"Debug: setup_ffmpeg failed: {e}")
        return False

def check_file(audio_file):
    """Check if file exists."""
    if not os.path.exists(audio_file):
        print(f"❌ Error: File '{audio_file}' not found.")
        sys.exit(1)
    
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    return file_size_mb

def normalize_language(lang):
    """Convert language name to code, or validate code."""
    if not lang:
        return DEFAULT_LANGUAGE
    
    lang = lang.lower().strip()
    
    # Check if it's an alias
    if lang in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lang]
    
    # If it's already a code (2 letters), return it
    if len(lang) == 2:
        return lang
    
    print(f"⚠️  Unknown language: {lang}")
    print(f"    Using default: {DEFAULT_LANGUAGE}")
    return DEFAULT_LANGUAGE

def split_audio_file(audio_file, max_size_mb=MAX_CHUNK_SIZE_MB):
    """
    Split audio file into chunks if larger than max_size_mb.
    Uses pydub for proper audio decoding/encoding.
    
    Returns:
        List of BytesIO objects, or None if file is small enough
    """
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        return None
    
    # Check if pydub is available
    if not setup_ffmpeg():
        print("❌ Large file detected but pydub/imageio-ffmpeg not installed.")
        print("   Install with: pip install pydub imageio-ffmpeg")
        sys.exit(1)
    
    from pydub import AudioSegment
    
    print(f"📊 File is {file_size_mb:.1f}MB - splitting into chunks...")
    
    # Load audio
    audio = AudioSegment.from_file(audio_file)
    total_duration_ms = len(audio)
    
    # Calculate chunk duration based on file size ratio
    # Estimate: if X MB = Y ms, then max_size_mb = (Y/X) * max_size_mb ms
    ms_per_mb = total_duration_ms / file_size_mb
    chunk_duration_ms = int(ms_per_mb * max_size_mb * 0.9)  # 0.9 for safety margin
    
    chunks = []
    chunk_num = 1
    start_ms = 0
    
    original_ext = Path(audio_file).suffix.lower()
    export_format = "mp3"  # Always export as MP3 for compatibility
    
    while start_ms < total_duration_ms:
        end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
        chunk_audio = audio[start_ms:end_ms]
        
        # Export to BytesIO
        buffer = BytesIO()
        chunk_audio.export(buffer, format=export_format)
        buffer.seek(0)
        
        chunk_size_mb = len(buffer.getvalue()) / (1024 * 1024)
        print(f"   Chunk {chunk_num}: {chunk_size_mb:.1f}MB ({(end_ms - start_ms) // 1000}s)")
        
        # Give it a filename for Whisper format detection
        buffer.name = f"chunk_{chunk_num:03d}.mp3"
        chunks.append(buffer)
        
        start_ms = end_ms
        chunk_num += 1
    
    print(f"✅ Split into {len(chunks)} chunks\n")
    return chunks

def transcribe_with_whisper(audio_input, api_key=None, language=DEFAULT_LANGUAGE):
    """
    Transcribe audio to text using OpenAI Whisper API.
    
    Args:
        audio_input: Either file path (str) or BytesIO object
        api_key: OpenAI API key (or from OPENAI_API_KEY env var)
        language: Language code
    
    Returns:
        Transcribed text
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed.")
        print("   Install with: pip install openai")
        sys.exit(1)
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found.")
        print()
        print("   Method 1 - As argument:")
        print("     python3 transcript_interview.py interview.mp3 sk-YOUR_KEY_HERE")
        print()
        print("   Method 2 - As environment variable:")
        print("     export OPENAI_API_KEY=sk-YOUR_KEY_HERE")
        print("     python3 transcript_interview.py interview.mp3")
        print()
        print("   Get an API key at: https://platform.openai.com/api-keys")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Determine filename for display
    if isinstance(audio_input, str):
        filename = Path(audio_input).name
        file_obj = open(audio_input, 'rb')
        should_close = True
    else:
        filename = getattr(audio_input, 'name', 'audio.mp3')
        file_obj = audio_input
        should_close = False
    
    print(f"🎙️ Transcribing '{filename}' ({language.upper()})...")
    
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=file_obj,
            language=language,
            response_format="text"
        )
        return transcript
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error from OpenAI API: {error_msg}")
        if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            print("   → Your API key is invalid.")
        elif "insufficient_quota" in error_msg.lower() or "429" in error_msg:
            print("   → Quota exceeded. Add payment method on OpenAI.")
        elif "413" in error_msg:
            print("   → File too large. This shouldn't happen with chunking.")
        raise
    finally:
        if should_close:
            file_obj.close()

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
    api_key = None
    language = DEFAULT_LANGUAGE
    
    # Parse remaining arguments
    for i in range(2, len(sys.argv)):
        arg = sys.argv[i]
        
        # Check if it's a language flag
        if arg.startswith("--language"):
            if "=" in arg:
                language = normalize_language(arg.split("=")[1])
            elif i + 1 < len(sys.argv):
                language = normalize_language(sys.argv[i + 1])
                break
        # Check if it looks like an API key
        elif arg.startswith("sk-"):
            api_key = arg
        # Otherwise treat as language code
        else:
            language = normalize_language(arg)
    
    # Check file first
    file_size_mb = check_file(audio_file)
    print(f"📁 File: {Path(audio_file).name} ({file_size_mb:.1f}MB)")
    
    try:
        # Check if file needs splitting
        chunks = split_audio_file(audio_file)
        
        if chunks is not None:
            # Transcribe each chunk
            all_transcripts = []
            for i, chunk_buffer in enumerate(chunks, 1):
                print(f"Transcribing chunk {i}/{len(chunks)}...")
                text = transcribe_with_whisper(chunk_buffer, api_key, language)
                all_transcripts.append(text)
                chunk_buffer.close()
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
        print()
        print(full_text)
        print()
        print("--- END ---")
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
