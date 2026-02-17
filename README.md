# Interview Transcription Script

Automatisk transkripsjon af audio-interviews til dansk tekst.

## Hvad det gør

- Konverterer audio-filer (MP3, WAV, FLAC, etc.) til dansk tekst
- Bruger OpenAI Whisper API (høj kvalitet, god til dansk)
- Gemmer resultatet i en tekstfil

## Installation

### 1. Installer Python dependencies

```bash
pip install openai
```

### 2. Få en OpenAI API key

1. Gå til https://platform.openai.com/api-keys
2. Log ind (eller opret konto)
3. Klik "Create new secret key"
4. Kopier nøglen

**Pris:** Whisper API koster ca. 0,02 USD pr. minut audio (meget billigt for 30 min)

## Brug

### Metode 1: Med API key direkte

```bash
python3 transcript_interview.py interview.mp3 sk-YOUR_API_KEY_HERE
```

### Metode 2: Med environment variable (mere sikkert)

```bash
export OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
python3 transcript_interview.py interview.mp3
```

### Eksempler

```bash
# MP3 fil
python3 transcript_interview.py interview.mp3

# WAV fil
python3 transcript_interview.py interview.wav

# M4A fil
python3 transcript_interview.py recording.m4a
```

## Output

Scriptet opretter en fil ved navn `[audiofile]_transcript.txt` med den fulde transkription.

**Eksempel:**
- Input: `interview.mp3`
- Output: `interview_transcript.txt`

## Filformater der understøttes

- MP3
- WAV
- FLAC
- OGG Opus
- M4A

## Tips

- For lange interviews (>25 min): prøv først med et kortere klip for at teste
- Audio-kvaliteten påvirker nøjagtigheden
- Hvis interviewet har baggrundsstøj, får du bedre resultater hvis du fjerner det først

## Fejlfinding

**"openai module not found"**
```bash
pip install openai
```

**"API key not found"**
- Sørg for at `OPENAI_API_KEY` env var er sat
- Eller angiv API key direkte som argument

**"Invalid API key"**
- Check at nøglen er korrekt
- Gå til https://platform.openai.com/account/api-keys og regenerer hvis nødvendigt

## Kontakt

Hvis der er spørgsmål, kontakt din søster Phillip.

---

Made by Rune 🎙️
