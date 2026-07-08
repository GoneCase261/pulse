import json
import os
from .vision import detect_goal_zone
from .vision import detect_net_motion

from .audio import detect_audio_shape

from .zoom import detect_zoom

from .fusion import combine_signals


def detect_events(analysis_path, video_path, sport_config, frames_dir="output/frames"):
    with open(analysis_path, "r", encoding="utf-8") as f:
        frames = json.load(f)

    zoom_threshold = sport_config.get("zoom_threshold", 0.7)

    goal_zone = detect_goal_zone(video_path)
    if not goal_zone:
        config_zones = sport_config.get("goal_zones", [])
        goal_zone = config_zones[0] if config_zones else None

    audio_events, energy_timeline = detect_audio_shape(video_path)
    print(f"[Pulse] Audio events detected: {len(audio_events)}")

    energy_path = "output/crowd_energy.json"
    os.makedirs("output", exist_ok=True)
    with open(energy_path, "w", encoding="utf-8") as f:
        json.dump(energy_timeline, f)
    print(
        f"[Pulse] Crowd energy timeline saved — {len(energy_timeline)} seconds")

    net_motion_events = []
    if goal_zone:
        meta_path = os.path.join(frames_dir, "metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        frame_files = metadata["frames"]
        net_motion_events = detect_net_motion(
            frame_files, frames_dir, goal_zone)
    else:
        print("[Pulse] No goal zone available, skipping net motion detection.")

    goal_events = combine_signals(audio_events, net_motion_events)

    zoom_frame_indices = detect_zoom(frames, zoom_threshold)
    zoom_events = []
    for i in zoom_frame_indices:
        zoom_events.append({
            "timestamp": frames[i]["timestamp"],
            "event": "zoom",
            "confidence": 1.0
        })

    all_events = goal_events + zoom_events
    all_events = sorted(all_events, key=lambda x: x["timestamp"])

    return all_events


def save_events(events, output_path="output/events.json"):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
    print(f"[Pulse] Events saved to {output_path}")
