import json
import os


def find_event_boost(timestamp, events, event_weights, window=2.0):

    # Find the highest-weight event near this timestamp and return its boost value.
    nearby = [
        e for e in events
        if abs(e["timestamp"] - timestamp) <= window
    ]
    if not nearby:
        return 0.0

    best = max(nearby, key=lambda e: event_weights.get(e["event"], 0.0))
    return event_weights.get(best["event"], 0.0)


def normalise_scores(scored_frames):
    """
    Min-max normalise intensity scores across all frames to 0-10 range.
    Skips normalisation if all frames have the same intensity.
    """
    intensities = [f["intensity"] for f in scored_frames]
    min_i = min(intensities)
    max_i = max(intensities)

    if max_i == min_i:
        return scored_frames

    for frame in scored_frames:
        normalised = (frame["intensity"] - min_i) / (max_i - min_i) * 10
        frame["intensity"] = round(normalised, 1)

    return scored_frames

# SCORING


def calculate_intensity(frame_analysis, intensity_weights, max_counts,
                        event_boost=0.0, crowd_energy=0.0):
    score = 0.0

    # Motion
    motion = frame_analysis["motion_score"] / 100.0
    score += motion * intensity_weights.get("motion", 0)

    # Detections
    for obj, data in frame_analysis["detections"].items():
        count = data["count"]
        max_c = max_counts.get(obj, 10)
        normalised = min(1.0, count / max_c)
        score += normalised * intensity_weights.get(obj, 0)

    # Crowd energy
    score += crowd_energy * intensity_weights.get("crowd", 0.3)

    # Event boost
    score += event_boost

    return round(min(score * 10, 10.0), 1)


def score_all_frames(analysis_path, intensity_weights, max_counts,
                     events=None, event_weights=None,
                     crowd_energy_path="output/crowd_energy.json"):

    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    if events is None:
        events = []
    if event_weights is None:
        event_weights = {}

    # Load crowd energy timeline
    crowd_energy_map = {}
    if os.path.exists(crowd_energy_path):
        with open(crowd_energy_path, "r", encoding="utf-8") as f:
            crowd_energy_map = json.load(f)
        print(f"[Pulse] Crowd energy loaded — {len(crowd_energy_map)} seconds")
    else:
        print("[Pulse] No crowd energy file, skipping crowd signal.")

    scored = []
    for frame in analysis:
        boost = find_event_boost(
            timestamp=frame["timestamp"],
            events=events,
            event_weights=event_weights
        )

        second_key = str(int(frame["timestamp"]))
        crowd_energy = crowd_energy_map.get(second_key, 0.0)

        intensity = calculate_intensity(
            frame_analysis=frame,
            intensity_weights=intensity_weights,
            max_counts=max_counts,
            event_boost=boost,
            crowd_energy=crowd_energy
        )

        scored.append({
            "frame_id": frame["frame_id"],
            "timestamp": frame["timestamp"],
            "intensity": intensity,
            "motion_score": frame["motion_score"],
            "detections": frame["detections"],
            "crowd_energy": crowd_energy
        })

    # Add trend data
    for i in range(len(scored)):
        trend_data = calculate_trend(scored, i, window=5)
        scored[i]["trend"] = trend_data["trend"]
        scored[i]["delta"] = trend_data["delta"]
        scored[i]["recent_scores"] = trend_data["recent_scores"]

    scored = normalise_scores(scored)
    return scored


def save_scores(scored_frames, output_path="output/scores.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scored_frames, f, indent=2)
    print(f"[Pulse] Scores saved to {output_path}")


# TREND CALCULATION
def calculate_trend(scored_frames, current_index, window=5):
    start = max(0, current_index - window)
    recent = scored_frames[start:current_index + 1]
    recent_scores = [f["intensity"] for f in recent]

    if len(recent_scores) < 2:
        return {"trend": "neutral", "delta": 0, "recent_scores": recent_scores}

    delta = recent_scores[-1] - recent_scores[0]
    is_peak = recent_scores[-1] == max(recent_scores)

    if is_peak and delta > 1.5:
        trend = "peak"
    elif delta > 0.8:
        trend = "building"
    elif delta < -1.0:
        trend = "declining"
    else:
        trend = "neutral"

    return {
        "trend":         trend,
        "delta":         round(delta, 2),
        "recent_scores": recent_scores
    }
