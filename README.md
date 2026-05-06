# J.A.R.V.I.S — Local AI Voice Agent

> "Just A Rather Very Intelligent System"

A fully local AI voice assistant inspired by JARVIS from Iron Man. Clap twice to wake it up, speak a command, and Jarvis responds with voice and takes action on your PC, all running offline with no API keys or monthly costs.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Ollama](https://img.shields.io/badge/Ollama-Llama%203.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## What it does

You clap twice. A HUD overlay appears on your screen. You say something like "Jarvis, open Chrome" or "Jarvis, search for the weather." Jarvis replies in a British voice and carries out the action. That is it.

It runs entirely on your machine — no internet needed after setup, no data sent anywhere, no subscription.

```
[double clap]
Jarvis: "Yes sir?"
You: "Open CSGO"
Jarvis: "Launching Counter-Strike right away, sir."
[game opens]
```

---

## Tech stack

| Part | Tool | Cost |
|---|---|---|
| AI brain | Ollama + Llama 3.1 8B | Free |
| Speech recognition | OpenAI Whisper | Free |
| Voice output | Piper TTS (British Alan) | Free |
| Wake trigger | Clap detection via sounddevice | Free |
| Screen overlay | Python Tkinter | Free |
| PC control | PyAutoGUI + subprocess | Free |

Total cost: $0

---

## What you need before starting

- Windows 10 or 11 (64-bit)
- Python 3.13 — download from python.org
- Ollama — download from ollama.com
- A microphone and speakers
- Around 8GB of free disk space for the AI model
- An NVIDIA GPU helps a lot (RTX 3060 or better), but it works without one — just slower

---

## Setup

This looks long but each step is short. Go through them one at a time.

### Step 1 — Get the code

Download or clone this repository and put the folder somewhere easy to find, like your Desktop.

```bash
git clone https://github.com/yourusername/jarvis-agent.git
cd jarvis-agent
```

### Step 2 — Install Python packages

Open a terminal inside the project folder and run:

```bash
pip install -r requirements.txt
```

This installs everything Jarvis needs — Whisper, audio recording, the UI library, and more. It takes a few minutes depending on your connection.

### Step 3 — Install Ollama and download the AI model

Go to ollama.com and download the Windows installer. After it installs, open a terminal and run:

```bash
ollama run llama3.1
```

The first time you run this it downloads the Llama 3.1 model (about 4.7GB). This is the brain that powers Jarvis. Once you see the `>>>` prompt, press Ctrl+C — the model stays saved on your machine permanently.

### Step 4 — Set up the voice

Download Piper TTS from github.com/rhasspy/piper/releases and add it to your system PATH.

Then download these two voice files and drop them into the project folder:

```
https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx
https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json
```

Just paste each link into your browser and they will download automatically.

---

## Running it

Make sure Ollama is running in the background, then open a terminal in the project folder and run:

```bash
py jarvis.py
```

You will see "Jarvis is ready. Clap twice to activate!" in the terminal. From that point, clap twice anywhere and the overlay appears.

---

## Commands you can try

- "Jarvis, open Chrome"
- "Jarvis, open CSGO"
- "Jarvis, search for the weather in Dubai"
- "Jarvis, take a screenshot"
- "Jarvis, volume up"
- "Jarvis, mute"
- "Jarvis, what is machine learning?"

Anything that is not a PC action gets answered as a regular question. Jarvis also remembers the conversation context throughout your session.

---

## Adding your own apps

Open `jarvis.py` and find the `APP_PATHS` section near the top. Add a new line with the app name and its file path:

```python
APP_PATHS = {
    "chrome":  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "myapp":   r"C:\Path\To\YourApp.exe",   # your app goes here
    ...
}
```

Then say "Jarvis, open myapp" and it will launch.

---

## Tweaking clap sensitivity

If Jarvis triggers too easily or not enough, adjust these two lines near the top of `jarvis.py`:

```python
CLAP_THRESH = 0.3   # lower number = triggers more easily
CLAP_WINDOW = 1.5   # how many seconds you have between the two claps
```

---

## How it works under the hood

1. The script listens to your microphone in the background, watching for two loud audio spikes close together
2. When it detects them, it records 5 seconds of audio
3. Whisper transcribes that audio to text, locally on your machine
4. The text plus your conversation history goes to Ollama, which runs Llama 3.1 on your GPU
5. The response is checked for an `[ACTION: ...]` tag — if one exists, the action runs
6. Piper reads the response out loud in the British voice
7. The overlay hides and goes back to listening

---

## Project structure

```
jarvis-agent/
├── jarvis.py          # the whole application — this is what you run
├── requirements.txt   # Python dependencies
├── .gitignore
└── README.md
```

---

## Troubleshooting

**"ollama is not recognized"** — Close the terminal and open a new one after installing Ollama.

**"python is not recognized"** — Try `py` instead of `python`. If that also fails, reinstall Python from python.org and make sure you tick "Add python.exe to PATH" on the first screen of the installer.

**Clap is not being picked up** — Lower `CLAP_THRESH` to `0.15` or `0.2` and try clapping closer to your microphone.

**No audio output** — Check that your default playback device is set correctly in Windows Sound Settings.

**App will not open** — Check that the file path in `APP_PATHS` matches where the app is actually installed on your PC.

---

## License

MIT — use it, change it, share it however you want.

---

## Credits

- Ollama for making local LLM inference practical
- OpenAI Whisper for offline speech recognition
- Piper TTS for the voice
- Optional: ME (feel free to mention me if you found this post)
