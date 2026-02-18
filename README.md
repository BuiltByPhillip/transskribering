# Interview Transcription Script

Transcribe audio interviews to text using OpenAI Whisper API.

## Installation

```bash
pip install openai
```

For large files (>25MB):
```bash
pip install openai pydub imageio-ffmpeg
```

All dependencies install via pip. No manual ffmpeg installation needed.

## Usage

```bash
python3 transcript_interview.py interview.mp3
```

With API key:
```bash
python3 transcript_interview.py interview.mp3 sk-YOUR_KEY
```

Or use environment variable:
```bash
export OPENAI_API_KEY=sk-YOUR_KEY
python3 transcript_interview.py interview.mp3
```

## Language

Default is English. Specify language with code or name:

```bash
python3 transcript_interview.py interview.mp3 da
python3 transcript_interview.py interview.mp3 --language danish
python3 transcript_interview.py interview.mp3 sk-KEY es
```

Supported: en, da, es, fr, de, it, pt, nl, ru, ja, zh, sv, and more.

## Large Files

Files >25MB are automatically split and transcribed in chunks. Requires pydub + imageio-ffmpeg.

## Supported Formats

MP3, WAV, FLAC, OGG, M4A, WEBM

## Pricing

~$0.02/minute. One hour ≈ $1.20.

---
Made by Rune 🎙️