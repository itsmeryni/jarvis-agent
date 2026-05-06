import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper
import requests
import subprocess
import tempfile
import os
import time
import re
import threading
import tkinter as tk
import math
import webbrowser
import pyautogui

# ── CONFIG ──────────────────────────────────────────────
OLLAMA_URL    = "http://localhost:11434/api/generate"
OLLAMA_MODEL  = "llama3.1"
PIPER_MODEL   = "en_GB-alan-medium.onnx"  # must be in same folder as jarvis.py
SAMPLE_RATE   = 16000
RECORD_SECS   = 5
CLAP_THRESH   = 0.3
CLAP_WINDOW   = 1.5
MIN_GAP       = 0.15

SYSTEM_PROMPT = """You are JARVIS (Just A Rather Very Intelligent System).
You are the AI assistant modeled after the AI from Iron Man.
You are witty, precise, and slightly British in manner.
You address the user as 'sir'.
Keep responses concise and spoken-word friendly — no markdown, no bullet points, no asterisks.
When the user asks you to open an app, search something, or control the PC,
start your response with [ACTION: <command>] followed by your spoken confirmation.
Examples:
- User: open chrome → [ACTION: open chrome] Opening Chrome right away, sir.
- User: search for weather → [ACTION: search weather] Pulling that up now, sir.
- User: what is AI? → Just a Rather Very Intelligent answer, sir. AI stands for..."""

# ── APP PATHS (customize these for your PC) ─────────────
APP_PATHS = {
    "chrome":     r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad":    r"notepad.exe",
    "calculator": r"calc.exe",
    "steam":      r"C:\Program Files (x86)\Steam\Steam.exe",
    "csgo":       r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\cs2.exe",
    "discord":    os.path.expanduser(r"~\AppData\Local\Discord\Update.exe"),
    "spotify":    os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe"),
    "explorer":   r"explorer.exe",
    "vscode":     os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
}

# ── CONVERSATION MEMORY ──────────────────────────────────
memory = []

# ── WHISPER MODEL ────────────────────────────────────────
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("Whisper ready.")

# ── JARVIS UI ────────────────────────────────────────────
class JarvisUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S")
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.93)
        self.root.overrideredirect(True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 500, 200
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{sh-h-40}")
        tk.Label(self.root, text="J.A.R.V.I.S",
                 fg='#00BFFF', bg='black',
                 font=('Courier New', 14, 'bold')).pack(pady=(12, 0))
        self.status = tk.Label(self.root,
                               text="ONLINE  —  Awaiting instructions, sir.",
                               fg='#00BFFF', bg='black',
                               font=('Courier New', 9),
                               wraplength=460)
        self.status.pack(pady=4)
        self.canvas = tk.Canvas(self.root, width=460, height=70,
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        self.bars = []
        for i in range(40):
            x = 20 + i * 11
            b = self.canvas.create_rectangle(x, 35, x + 7, 35,
                                             fill='#00BFFF', outline='')
            self.bars.append(b)
        self.animating = False
        self._animate()
        self.root.withdraw()

    def _animate(self):
        for i, bar in enumerate(self.bars):
            if self.animating:
                h = abs(math.sin(time.time() * 3 + i * 0.4)) * 26 + 4
            else:
                h = abs(math.sin(i * 0.4)) * 5 + 2
            self.canvas.coords(bar, 20 + i * 11, 35 - h, 27 + i * 11, 35 + h)
        self.root.after(50, self._animate)

    def set_status(self, text, speaking=False):
        self.status.config(text=text)
        self.animating = speaking

    def show(self):
        self.root.deiconify()
        self.root.lift()

    def hide(self):
        self.root.withdraw()

    def run(self):
        self.root.mainloop()


# ── TEXT TO SPEECH ───────────────────────────────────────
def speak(text):
    try:
        proc = subprocess.Popen(
            ["piper", "--model", PIPER_MODEL, "--output-raw"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        raw, _ = proc.communicate(input=text.encode())
        play = subprocess.Popen(
            ["python", "-c",
             "import sys,sounddevice as sd,numpy as np;"
             "d=sys.stdin.buffer.read();"
             "a=np.frombuffer(d,dtype=np.int16);"
             "sd.play(a,22050);sd.wait()"],
            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        play.communicate(input=raw)
    except Exception:
        # Fallback to pyttsx3 if Piper not available
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for v in voices:
            if 'english' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()


# ── PC ACTIONS ───────────────────────────────────────────
def execute_action(cmd):
    cmd = cmd.lower().strip()
    for app, path in APP_PATHS.items():
        if app in cmd:
            try:
                subprocess.Popen(path, shell=True)
                return
            except Exception:
                pass
    if "search" in cmd:
        query = re.sub(r'search\s*(for)?', '', cmd).strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "youtube" in cmd:
        webbrowser.open("https://youtube.com")
    elif "volume up" in cmd:
        for _ in range(5):
            pyautogui.press('volumeup')
    elif "volume down" in cmd:
        for _ in range(5):
            pyautogui.press('volumedown')
    elif "mute" in cmd:
        pyautogui.press('volumemute')
    elif "screenshot" in cmd:
        path = os.path.expanduser("~/Desktop/jarvis_screenshot.png")
        pyautogui.screenshot().save(path)


# ── OLLAMA (LOCAL AI) ─────────────────────────────────────
def ask_jarvis(user_text):
    global memory
    memory.append({"role": "user", "content": user_text})
    if len(memory) > 20:
        memory = memory[-20:]

    # Build prompt with memory
    history = ""
    for msg in memory[:-1]:
        role = "User" if msg["role"] == "user" else "JARVIS"
        history += f"{role}: {msg['content']}\n"

    full_prompt = f"{SYSTEM_PROMPT}\n\n{history}User: {user_text}\nJARVIS:"

    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    })

    reply = response.json().get("response", "").strip()
    memory.append({"role": "assistant", "content": reply})
    return reply


# ── VOICE RECORDING ──────────────────────────────────────
def record_audio():
    audio = sd.rec(int(RECORD_SECS * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    return audio


def transcribe(audio):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, SAMPLE_RATE, audio)
        result = whisper_model.transcribe(f.name)
        os.unlink(f.name)
    return result["text"].strip()


# ── CLAP DETECTION ────────────────────────────────────────
def start_clap_listener(on_double_clap):
    clap_times = []

    def callback(indata, frames, time_info, status):
        volume = np.linalg.norm(indata) / len(indata)
        now = time.time()
        if volume > CLAP_THRESH:
            if not clap_times or (now - clap_times[-1]) > MIN_GAP:
                clap_times.append(now)
            while clap_times and (now - clap_times[0]) > CLAP_WINDOW:
                clap_times.pop(0)
            if len(clap_times) >= 2:
                clap_times.clear()
                threading.Thread(target=on_double_clap, daemon=True).start()

    with sd.InputStream(callback=callback, channels=1,
                        samplerate=44100, blocksize=1024):
        print("Listening for double clap...")
        while True:
            sd.sleep(100)


# ── MAIN JARVIS LOOP ──────────────────────────────────────
ui = JarvisUI()


def jarvis_triggered():
    ui.show()
    ui.set_status("LISTENING...", speaking=False)
    speak("Yes sir?")

    audio = record_audio()
    text = transcribe(audio)

    if not text:
        ui.set_status("ONLINE  —  Awaiting instructions, sir.")
        time.sleep(2)
        ui.hide()
        return

    print(f"You: {text}")
    ui.set_status(f'"{text}"')

    reply = ask_jarvis(text)
    print(f"Jarvis: {reply}")

    # Handle action tag
    action_match = re.search(r'\[ACTION:\s*(.+?)\]', reply)
    spoken = re.sub(r'\[ACTION:.+?\]', '', reply).strip()

    if action_match:
        execute_action(action_match.group(1))

    ui.set_status(spoken[:80], speaking=True)
    speak(spoken)
    ui.set_status("ONLINE  —  Awaiting instructions, sir.", speaking=False)
    time.sleep(3)
    ui.hide()


# Start clap listener in background thread
threading.Thread(
    target=start_clap_listener,
    args=(jarvis_triggered,),
    daemon=True
).start()

print("Jarvis is ready. Clap twice to activate!")
ui.run()
