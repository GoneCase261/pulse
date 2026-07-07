def combine_signals(audio_events, net_motion_events, window=3.0):
    """
    Votes across audio and net motion signals.
    Goal requires sustained audio (4+ seconds) — no exceptions.
    Net motion + quick audio = near miss only.
    Net motion alone = near miss only.
    """
    final_events = []
    used_motion = set()

    for audio_event in audio_events:
        at = audio_event["timestamp"]
        sustained = audio_event.get("sustained_seconds", 0)

        nearby_motion = [
            m for i, m in enumerate(net_motion_events)
            if abs(m["timestamp"] - at) <= window
            and i not in used_motion
        ]

        if nearby_motion:
            best_motion = max(nearby_motion, key=lambda x: x["avg_motion"])
            motion_idx = net_motion_events.index(best_motion)
            used_motion.add(motion_idx)

            if audio_event["event"] == "goal_audio" and sustained >= 4:
                # Both agree AND audio sustained = confirmed goal
                final_events.append({
                    "timestamp": at,
                    "event": "goal",
                    "confidence": min(1.0, audio_event["confidence"] + 0.15),
                    "source": "audio+vision",
                    "sustained_seconds": sustained
                })
            else:
                # Motion present but audio not sustained enough = near miss
                final_events.append({
                    "timestamp": at,
                    "event": "near_miss",
                    "confidence": audio_event["confidence"],
                    "source": "audio+vision",
                    "sustained_seconds": sustained
                })
        else:
            # Audio only
            if audio_event["event"] == "goal_audio" and sustained >= 4:
                final_events.append({
                    "timestamp": at,
                    "event": "goal",
                    "confidence": round(audio_event["confidence"] * 0.75, 2),
                    "source": "audio_only",
                    "sustained_seconds": sustained
                })
            else:
                final_events.append({
                    "timestamp": at,
                    "event": "near_miss",
                    "confidence": round(audio_event["confidence"] * 0.6, 2),
                    "source": "audio_only",
                    "sustained_seconds": sustained
                })

    # Net motion with no audio match = near miss, never goal
    for i, motion in enumerate(net_motion_events):
        if i not in used_motion:
            final_events.append({
                "timestamp": motion["timestamp"],
                "event": "near_miss",
                "confidence": 0.45,
                "source": "vision_only"
            })

    return sorted(final_events, key=lambda x: x["timestamp"])
