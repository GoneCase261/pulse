⚽ Pulse

AI-powered sports highlight generation using computer vision, audio analysis, and LLM-generated commentary.

Pulse analyzes a sports video, detects important moments by combining multiple signals, scores the intensity of play, generates contextual commentary, synthesizes speech, and produces a final highlight video with commentary and background music.

🎥 Demo
Before:


https://github.com/user-attachments/assets/d9fa4b62-51ae-4dda-abe3-9670ac0fe3e0



After:


https://github.com/user-attachments/assets/b4c0dd75-e9e7-493b-9b71-fef78c444407


🧠 What it does

Instead of relying on a single cue, Pulse combines information from multiple sources to estimate when important moments happen.

The pipeline includes:

Frame extraction from the source video

Object detection using YOLO

Motion analysis

Crowd energy analysis from audio

Goal and near-miss detection through multi-signal fusion

Frame intensity scoring

LLM-generated sports commentary

Speech synthesis using ElevenLabs

Background music selection based on match intensity

Audio/video synchronization to produce the final output

⚙️ Tech Stack

Languages

Python

Computer Vision

YOLOv8

OpenCV

Audio Processing

Librosa
PyDub

AI

Groq API (Llama 3.1 8B Instant)

ElevenLabs Text-to-Speech

Video Processing

MoviePy

Configuration

JSON-based sport configurations

📊 Pipeline

Video

↓

Extract Frames

↓

YOLO Detection + Motion Analysis

↓

Crowd Audio Analysis

↓

Multi-signal Event Detection

↓

Frame Intensity Scoring

↓

Highlight Selection

↓

LLM Commentary Generation

↓

Speech Synthesis

↓

Background Music Generation

↓

Audio Synchronization

↓

Final Highlight Video

📁 Project Structure
Pulse/

├── app.py

├── core/

│   ├── commentary.py

│   ├── detector.py

│   ├── extractor.py

│   ├── music.py

│   ├── scorer.py

│   ├── sync.py

│   ├── speech.py

│   ├── config_loader.py

│   └── events/

│       ├── __init__.py

│       ├── audio.py

│       ├── fusion.py

│       ├── manager.py

│       ├── vision.py

│       └── zoom.py

├── configs/

│   └── football.json

├── data/

├── music/

├── output/

├── requirements.txt

├── .env.example

├── .gitignore

└── README.md

🚀 Getting Started

1. Clone the repository
git clone <repository-url>
cd Pulse

2. Install dependencies
pip install -r requirements.txt
3. Install FFmpeg

MoviePy and PyDub require FFmpeg to be installed and available in your system PATH.

4. Configure environment variables

Create a .env file.

GROQ_API_KEY=your_key

ELEVENLABS_API_KEY=your_key

ELEVENLABS_VOICE_ID=your_voice_id

5. Add a video

Place the input video inside the data/ folder.

6. Run

python app.py

The generated highlight video will be saved inside:

output/final_output.mp4

📝 Limitations

Event detection combines audio and visual signals instead of relying on a single detector.

Commentary is generated from the detected game situation rather than using fixed templates.

Different sports can be supported by adding new configuration files.

Detection quality depends on the video angle, crowd audio, and object visibility.

Commentary timing is approximate and may lag the actual event by a small amount in the current version.

🔮 Future Improvements

Additional sports support

Player and team recognition

Better commentary timing alignment

Multi-language commentary

Streaming/live match support

Learned event detection models instead of rule-based signal fusion
