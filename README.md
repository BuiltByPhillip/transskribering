# Interview Transcription Script

Automatic transcription of audio interviews to any language using OpenAI Whisper API.

## Installation

```bash
pip install openai
```

That's it. Seriously.

## Usage

```bash
python3 transcript_interview.py interview.mp3
```

With environment variable (more secure):
```bash
export OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
python3 transcript_interview.py interview.mp3
```

With API key directly:
```bash
python3 transcript_interview.py interview.mp3 sk-YOUR_API_KEY_HERE
```

Get your API key here: https://platform.openai.com/api-keys

## Language Support

Default language is English. Specify any language using 2-letter codes or common names:

```bash
# Using language code
python3 transcript_interview.py interview.mp3 da       # Danish
python3 transcript_interview.py interview.mp3 es       # Spanish
python3 transcript_interview.py interview.mp3 fr       # French

# Using --language flag
python3 transcript_interview.py interview.mp3 --language danish
python3 transcript_interview.py interview.mp3 --language spanish
python3 transcript_interview.py interview.mp3 --language=de

# With API key and language
python3 transcript_interview.py interview.mp3 sk-YOUR_KEY_HERE da
```

### Supported Languages

| Code | Name | Code | Name |
|------|------|------|------|
| en | English | de | German |
| da | Danish | es | Spanish |
| fr | French | it | Italian |
| pt | Portuguese | nl | Dutch |
| ru | Russian | ja | Japanese |
| zh | Chinese | sv | Swedish |

(All language codes supported by OpenAI Whisper work)

## Supported Formats

MP3, WAV, FLAC, OGG, M4A, WEBM — anything Whisper API supports.

## Large Files

Files larger than 25MB are automatically split and transcribed in chunks. You get one transcript file.

```bash
# Works with 100MB+ files
python3 transcript_interview.py huge_recording.mp3
python3 transcript_interview.py huge_recording_danish.mp3 da
```

## Output

The script saves the transcription as `[filename]_transcript.txt`.

## Pricing

Whisper API costs ~$0.02 per minute of audio. One hour costs ~$1.20.

---

Made by Rune 🎙️
