# Interview Transcription Script

Automatic transcription of audio interviews to English text using OpenAI Whisper API.

## Installation

```bash
pip install openai
```

That's it. Seriously.

## Usage

```bash
python3 transcript_interview.py interview.mp3
```

Or with API key directly:
```bash
python3 transcript_interview.py interview.mp3 sk-YOUR_API_KEY_HERE
```

## Environment Variable (more secure)

```bash
export OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
python3 transcript_interview.py interview.mp3
```

Get your API key here: https://platform.openai.com/api-keys

## Supported Formats

MP3, WAV, FLAC, OGG, M4A, WEBM — anything Whisper API supports.

## Large Files

Files larger than 25MB are automatically split and transcribed in chunks. You get one transcript file.

```bash
# Works with 100MB+ files
python3 transcript_interview.py huge_recording.mp3
```

## Output

The script saves the transcription as `[filename]_transcript.txt`.

## Pricing

Whisper API costs ~$0.02 per minute of audio. One hour costs ~$1.20.

---

Made by Rune 🎙️
