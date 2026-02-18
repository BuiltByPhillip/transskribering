# Interview Transcription Script

Automatisk transkripsjon af audio-interviews til dansk tekst.

## Installation

```bash
pip install openai
```

Det er alt. Seriøst.

## Brug

```bash
python3 transcript_interview.py interview.mp3
```

Eller med API key direkte:
```bash
python3 transcript_interview.py interview.mp3 sk-YOUR_API_KEY_HERE
```

## Miljøvariabel (mere sikkert)

```bash
export OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
python3 transcript_interview.py interview.mp3
```

Få din API key her: https://platform.openai.com/api-keys

## Filformater

MP3, WAV, FLAC, OGG, M4A, WEBM — alt som Whisper API understøtter.

## Store filer

Filer større end 25MB bliver automatisk delt op og transkriberet i dele. Du får én tekstfil.

```bash
# Virker med 100MB+ filer
python3 transcript_interview.py huge_recording.mp3
```

## Output

Scriptet gemmer transkriptionen som `[filnavn]_transcript.txt`.

## Pris

Whisper API koster ca. 0,02 USD per minut audio. En time koster ~$1.20.

---

Made by Rune 🎙️
