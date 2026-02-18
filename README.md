# Interview Transcription Script

Transcribe audio interviews to text using OpenAI Whisper API.

## Installation

```bash
# Python packages
pip install openai

# For large files (>25MB), also install ffmpeg
brew install ffmpeg      # macOS
apt install ffmpeg       # Linux
choco install ffmpeg     # Windows
```

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

Default is English. Specify with code or name:

```bash
python3 transcript_interview.py interview.mp3 da           # Danish
python3 transcript_interview.py interview.mp3 --language danish
python3 transcript_interview.py interview.mp3 sk-KEY es    # Spanish
```

Supported: en, da, es, fr, de, it, pt, nl, ru, ja, zh, sv, and more.

## Large Files

Files >25MB are automatically split and transcribed. Requires ffmpeg.

```bash
python3 transcript_interview.py huge_file.m4a da
```

## Supported Formats

MP3, WAV, FLAC, OGG, M4A, WEBM — anything ffmpeg handles.

## Pricing

~$0.02/minute. One hour ≈ $1.20.

---

Made with Claude AI
