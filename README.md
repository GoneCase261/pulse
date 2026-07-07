# ⚽ Pulse

Automatically detect the most exciting moments of a sports match and turn them into narrated highlights using AI.

Pulse combines computer vision, audio analysis, and large language models to identify key moments in a football match, generate contextual commentary, synthesize speech, and produce a final highlight video with synchronized commentary and dynamic background music.

---

## 🎥 Demo

### Input Video

*Raw football match footage.*

> *

https://github.com/user-attachments/assets/24dcdd3d-9b1a-4f78-bb4e-427f0f7e5015

*

### Output Video

*Pulse-generated highlight with AI commentary, speech synthesis, and adaptive background music.*

> *

https://github.com/user-attachments/assets/3e9dc458-3242-47a4-a1fe-816eeb2c530d

*

---

## ✨ Features

- Detects important moments using both visual and audio cues
- YOLO-based player and ball detection
- Crowd energy analysis from match audio
- Goal-zone motion detection using optical flow
- Multi-signal event fusion for highlight detection
- Frame-wise intensity scoring
- AI-generated contextual sports commentary
- Speech synthesis using ElevenLabs
- Dynamic background music based on match intensity
- Automatic synchronization of commentary, music, and gameplay

---

## ⚙️ Tech Stack

**Programming Language**
- Python

**Computer Vision**
- YOLOv8
- OpenCV

**Audio Processing**
- Librosa
- PyDub

**Large Language Model**
- Groq API (Llama 3.1 8B Instant)

**Text-to-Speech**
- ElevenLabs

**Video Processing**
- MoviePy

**Configuration**
- JSON-based sport configuration

---

## 📊 Execution Pipeline

```text
Input Video
      │
      ▼
Frame Extraction
      │
      ▼
YOLO Object Detection
      │
      ├──────────────┐
      ▼              ▼
Motion Analysis   Crowd Audio Analysis
      │              │
      └──────┬───────┘
             ▼
      Event Detection
             │
             ▼
  Frame Intensity Scoring
             │
             ▼
    Highlight Selection
             │
             ▼
 AI Commentary Generation
             │
             ▼
 Speech Synthesis (TTS)
             │
             ▼
 Dynamic Background Music
             │
             ▼
Audio / Video Synchronization
             │
             ▼
   Final Highlight Video
```

---

## 📁 Project Structure

```text
Pulse/
├── app.py                      # Application entry point
├── configs/
│   └── football.json           # Sport configuration
├── core/
│   ├── commentary.py           # Commentary generation
│   ├── config_loader.py        # Config loader
│   ├── detector.py             # YOLO inference
│   ├── extractor.py            # Frame extraction
│   ├── movie.py                # Video utilities
│   ├── music.py                # Music generation
│   ├── scorer.py               # Intensity scoring
│   ├── speech.py               # Speech synthesis
│   ├── sync.py                 # Audio/video sync
│   └── events/
│       ├── __init__.py
│       ├── audio.py            # Crowd analysis
│       ├── fusion.py           # Signal fusion
│       ├── manager.py          # Event pipeline
│       ├── vision.py           # Vision detection
│       └── zoom.py             # Zoom detection
├── data/                       # Input videos
├── music/                      # Music tracks
├── output/                     # Generated outputs
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/GoneCase261/Pulse.git
cd Pulse
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

Pulse uses MoviePy and PyDub, both of which require FFmpeg to be installed and available through your system PATH.

---

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
```

---

### 5. Add an input video

Place your input video inside the `data/` directory.

---

### 6. Run Pulse

```bash
python app.py
```

The generated highlight video will be available at

```text
output/final_output.mp4
```

---

## ⚠️ Limitations

- Event detection currently combines handcrafted audio and vision signals rather than learned event detection models.
- Detection accuracy depends on factors such as camera angle, crowd audio quality, video resolution, and object visibility.
- The current implementation is optimized for football, with additional sports intended to be supported through configurable pipelines.

---

## 🔮 Future Improvements

- Support for additional sports
- Player and team recognition
- Learned event detection models
- More natural commentary generation
- Multi-language commentary
- Live match support
- Interactive highlight customization

---

## 📄 License

This project is licensed under the MIT License.
