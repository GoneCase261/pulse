import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def find_event_at_timestamp(events, timestamp, window=2.0):
    candidates = [
        e for e in events
        if abs(e["timestamp"] - timestamp) <= window
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda x: x["confidence"])


def build_prompt(scored_frame, sport_config, event=None):
    intensity = scored_frame["intensity"]
    timestamp = scored_frame["timestamp"]
    trend = scored_frame.get("trend", "neutral")
    style = sport_config["commentary_style"]
    sport = sport_config["display_name"]

    if event:
        etype = event["event"]
        sustained = event.get("sustained_seconds", 0)
        source = event.get("source", "unknown")

        if etype == "goal":
            situation = "GOAL"
            instruction = (
                "A goal has just been scored. "
                f"Crowd noise sustained for {sustained} seconds. "
                f"Confirmed by: {source}. "
                "React immediately. Explosive, short. No setup, no buildup — pure reaction."
            )
            word_limit = "4-6 words. Single phrase."
            temperature = 0.4

        elif etype == "near_miss":
            situation = "NEAR MISS"
            instruction = (
                "A shot just missed or was saved. Crowd reacted briefly. "
                "React with immediate disappointment or relief. No setup."
            )
            word_limit = "5-7 words."
            temperature = 0.4

        elif etype == "crowd_spike":
            situation = "CROWD REACTING"
            instruction = (
                "The crowd is suddenly loud — something is happening. "
                "Build tension, don't resolve it. The commentator doesn't know what yet."
            )
            word_limit = "6-8 words."
            temperature = 0.5

        elif etype == "zoom":
            situation = "CAMERA ZOOMING IN"
            instruction = (
                "Camera is tightening on a player or moment. "
                "Quiet, focused anticipation."
            )
            word_limit = "6-8 words."
            temperature = 0.5

        else:
            situation = "GENERAL PLAY"
            instruction = _intensity_instruction(intensity, trend)
            word_limit = "6-8 words."
            temperature = 0.5

    else:
        situation = "GENERAL PLAY"
        instruction = _intensity_instruction(intensity, trend)
        word_limit = "6-8 words."
        temperature = 0.5

    prompt = f"""You are a {style}. Sport: {sport}.

CURRENT SITUATION: {situation}

CONTEXT:{instruction}
Your task is to generate a short live commentary line that sounds natural during a real {sport} broadcast.
STRICT OUTPUT RULES:
1. Return ONLY the commentary.
2. Return EXACTLY ONE sentence.
3. Never exceed {word_limit}
4. Never use line breaks.
5. Never use quotation marks.
6. Never explain the commentary.
7. Never describe the instructions.
8. Never mention the sport, situation, or context explicitly.
9. Use different wording every time.
Examples:

GOAL:
Back of the net!

NEAR MISS:
Just wide of the post.

CAMERA ZOOM:
Everyone is watching now.

GENERAL PLAY:
Pressure continues to build.

Return ONLY the commentary.
"""
    return prompt, temperature


def _intensity_instruction(intensity, trend):
    if intensity <= 3:
        return (
            "Quiet moment in the game. "
            "Calm, analytical observation. "
            "Describe what's happening on the pitch simply."
        )
    elif intensity <= 6:
        if trend == "building":
            return "Pressure is building. Describe the growing tension without overreacting."
        else:
            return "Mid-intensity play. Something may be developing. Measured commentary."
    elif intensity <= 8:
        return "Sharp, urgent moment. The game is live. Short, punchy."
    else:
        return "High intensity. Something is about to happen or just did. Immediate, sharp."


def generate_commentary(scored_frame, sport_config, event=None):
    prompt, temperature = build_prompt(scored_frame, sport_config, event)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=40,
        temperature=temperature
    )

    return response.choices[0].message.content.strip()


def generate_commentary_for_highlights(scored_frames, sport_config, events=None, n=10):
    if not scored_frames:
        return []

    if events is None:
        events = []

    selected = []
    selected_timestamps = set()
    last_ts = -999  # single variable used throughout all steps

    clip_duration = scored_frames[-1]["timestamp"]
    base_gap = 5.0
    end_zone = clip_duration * 0.3  # last 30% of clip gets tighter gap

    def dynamic_gap(timestamp):
        # Shrink gap requirement in last 20% of clip
        time_remaining = clip_duration - timestamp
        return 3.0 if time_remaining < end_zone else base_gap

    # Step 1 — goals always make it in, no gap check, no time guard
    for goal in [e for e in events if e["event"] == "goal" and e["confidence"] >= 0.7]:
        closest = min(scored_frames, key=lambda f: abs(
            f["timestamp"] - goal["timestamp"]))
        if closest["timestamp"] not in selected_timestamps:
            selected.append((closest, goal))
            selected_timestamps.add(closest["timestamp"])
            last_ts = closest["timestamp"]

    # Step 2 — near misses: dynamic gap + skip first 2 seconds
    for nm in [e for e in events if e["event"] == "near_miss" and e["confidence"] >= 0.6]:
        closest = min(scored_frames, key=lambda f: abs(
            f["timestamp"] - nm["timestamp"]))
        if (
            closest["timestamp"] not in selected_timestamps
            and closest["timestamp"] - last_ts >= dynamic_gap(closest["timestamp"])
            and closest["timestamp"] >= 2.0
        ):
            selected.append((closest, nm))
            selected_timestamps.add(closest["timestamp"])
            last_ts = closest["timestamp"]

    # Step 3 — fill remaining slots from intensity buckets
    remaining = n - len(selected)
    if remaining > 0 and scored_frames:
        bucket_size = clip_duration / remaining

        for b in range(remaining):
            bucket_start = b * bucket_size
            bucket_end = bucket_start + bucket_size

            candidates = [
                f for f in scored_frames
                # <= to catch last frame
                if bucket_start <= f["timestamp"] <= bucket_end
                and f["timestamp"] not in selected_timestamps
                and f["intensity"] >= 5.0
                and f["timestamp"] >= 2.0  # never pick first 2 seconds
            ]

            if candidates:
                best = max(candidates, key=lambda x: x["intensity"])
                nearby_event = find_event_at_timestamp(
                    events, best["timestamp"])
                if best["timestamp"] - last_ts >= dynamic_gap(best["timestamp"]):
                    selected.append((best, nearby_event))
                    selected_timestamps.add(best["timestamp"])
                    last_ts = best["timestamp"]

    # Step 4 — sort chronologically
    selected = sorted(selected, key=lambda x: x[0]["timestamp"])

    # Step 5 — final gap filter with dynamic gap (catches anything that slipped through)
    filtered = []
    last_ts = -999
    for frame, event in selected:
        if frame["timestamp"] - last_ts >= dynamic_gap(frame["timestamp"]):
            filtered.append((frame, event))
            last_ts = frame["timestamp"]

    # Step 6 — generate commentary
    results = []
    for frame, event in filtered:
        etype = event["event"] if event else None

        print(
            f"[Pulse] Commentary t={frame['timestamp']}s "
            f"intensity={frame['intensity']} "
            f"event={etype or 'none'}"
        )

        line = generate_commentary(frame, sport_config, event)

        results.append({
            "frame_id":    frame["frame_id"],
            "timestamp":   frame["timestamp"],
            "intensity":   frame["intensity"],
            "trend":       frame["trend"],
            "commentary":  line,
            "event":       etype,
            "lead_offset": 0.5 if etype in ("goal", "near_miss") else 1.5
        })

    return results
