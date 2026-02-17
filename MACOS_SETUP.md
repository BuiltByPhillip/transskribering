# Setup til macOS

Sådan installer og bruger du transkriberingsscriptet på Mac.

## 1. Installér Python (hvis ikke allerede installeret)

macOS kommer med Python, men du bør bruge en nyere version:

```bash
# Metode 1: Homebrew (anbefales)
brew install python3

# Metode 2: Download fra python.org
# Gå til https://www.python.org/downloads/ og download macOS installer
```

Check version:
```bash
python3 --version  # Skal være 3.8 eller nyere
```

## 2. Clone eller download repoet

```bash
# Option A: Clone med git
git clone https://github.com/BuiltByPhillip/transskribering.git
cd transskribering

# Option B: Download ZIP
# Klik "Code" → "Download ZIP" på GitHub
# Udpak og åbn mappen i Terminal
```

## 3. Installér Python dependencies

```bash
pip3 install openai
```

## 4. Få OpenAI API key

1. Gå til https://platform.openai.com/api-keys
2. Log ind (eller opret konto)
3. Klik "Create new secret key"
4. Kopier nøglen (gem den et sikkert sted!)

## 5. Eksekver scriptet

```bash
# Metode 1: Med API key direkte
python3 transcript_interview.py interview.mp3 sk-YOUR_API_KEY_HERE

# Metode 2: Med environment variable (mere sikkert)
export OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
python3 transcript_interview.py interview.mp3
```

## Eksempler

```bash
# MP3
python3 transcript_interview.py interview.mp3

# WAV
python3 transcript_interview.py recording.wav

# M4A (iPhone voice memo)
python3 transcript_interview.py voice_memo.m4a
```

## Output

Scriptet opretter automatisk `interview_transcript.txt` med transkriptionen.

## Fejlfinding på Mac

### "command not found: python3"
```bash
# Installér Python via Homebrew
brew install python3
```

### "No module named 'openai'"
```bash
pip3 install openai
```

### "Permission denied"
```bash
chmod +x transcript_interview.py
./transcript_interview.py interview.mp3 sk-YOUR_KEY
```

### API key fejl
- Kontrollér at nøglen er korrekt (skal starte med `sk-`)
- Gå til https://platform.openai.com/account/api-keys og regenerer hvis nødvendigt

## Tips til Mac

- **Voice Memos:** Hvis du har optaget i iPhone Voice Memos, eksportér som M4A
- **Finder:** Træk audio-filen direkte ind i Terminal efter scriptet for fuldt path
- **Shortcut:** Lav et shell script alias for nemmere brug:
  ```bash
  echo 'alias transcribe="python3 ~/path/to/transcript_interview.py"' >> ~/.zshrc
  source ~/.zshrc
  # Så kan du bare skrive: transcribe interview.mp3
  ```

## Pris

OpenAI Whisper API koster ca. 0,02 USD pr. minut audio.
- 30 min interview ≈ $0,60
- Billigt og højkvalitet!

---

Spørgsmål? Skriv til Phillip 🎙️
