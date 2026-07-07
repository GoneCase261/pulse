⚽ Pulse

AI-powered sports highlight generation using computer vision, audio analysis, and large language models.

Pulse analyzes a sports video, detects important moments by combining visual and audio signals, generates contextual commentary, synthesizes speech, and produces a final highlight video with synchronized commentary and background music.

🎥 Demo
Input Video

Raw football match footage.



https://github.com/user-attachments/assets/78556c16-4b27-45b5-ba4f-f4842ccfe92e



Output Video

Pulse-generated highlight with AI commentary, speech synthesis, and dynamic background music.



https://github.com/user-attachments/assets/1c88e62d-c36c-4634-9a76-348a318a1f61




✨ Features
Multi-signal sports event detection
YOLO-based player and ball detection
Crowd energy analysis from match audio
Motion and zoom detection
Event fusion using audio and visual cues
Intensity scoring for every frame
AI-generated contextual sports commentary
ElevenLabs voice synthesis
Dynamic background music based on game intensity
Automatic synchronization of commentary, music, and gameplay
⚙️ Tech Stack
Programming Language
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
JSON-based sport configuration system
📊 Execution Pipeline
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
📁 Project Structure
Pulse/
├── app.py
├── configs/
│   └── football.json
├── core/
│   ├── commentary.py
│   ├── config_loader.py
│   ├── detector.py
│   ├── extractor.py
│   ├── music.py
│   ├── scorer.py
│   ├── speech.py
│   ├── sync.py
│   └── events/
│       ├── __init__.py
│       ├── audio.py
│       ├── fusion.py
│       ├── manager.py
│       ├── vision.py
│       └── zoom.py
├── data/
├── music/
├── output/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
🚀 Getting Started
1. Clone the repository
git clone https://github.com/<your-username>/Pulse.git
cd Pulse
2. Install dependencies
pip install -r requirements.txt
3. Install FFmpeg

Pulse uses MoviePy and PyDub, both of which require FFmpeg to be installed and accessible through your system PATH.

4. Configure environment variables

Create a .env file in the project root.

GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
5. Add an input video

Place the input video inside the data/ directory.

6. Run Pulse
python app.py

The generated highlight video will be saved to:

output/final_output.mp4
⚠️ Limitations
Event detection currently combines handcrafted audio and vision signals rather than learned event detection models.
Detection accuracy depends on factors such as camera angle, crowd audio quality, video resolution, and object visibility.
The current implementation is optimized for football, with additional sports intended to be supported through configurable pipelines.
🔮 Future Improvements
Support for additional sports
Player and team recognition
Improved event detection using learned models
More natural commentary generation
Multi-language commentary
Live match and streaming support
Interactive highlight customization
