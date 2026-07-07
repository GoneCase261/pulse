import cv2
import json
import os

from core.config_loader import load_sport_config
from core.detector import load_model, analyse_frame
from core.extractor import extract_frames
from core.scorer import score_all_frames, save_scores
from core.commentary import generate_commentary_for_highlights
from core.voice import synthesise_all_commentary
from core.sync import orchestrate
from core.events import detect_events, save_events

if __name__ == "__main__":

    # Load sport config
    config = load_sport_config("football")
    print(f"[Pulse] Sport: {config['display_name']}")

    # extract frames
    frames_dir = "output/frames"
    meta_path = "output/frames/metadata.json"

    if not os.path.exists(meta_path):
        print("[Pulse] Extracting frames...")
        metadata = extract_frames(
            video_path="data/test_clip.mp4",
            output_dir=frames_dir,
            fps_target=config["fps_target"]
        )
    else:
        print("[Pulse] Frames already extracted, loading metadata...")
        with open(meta_path, "r") as f:
            metadata = json.load(f)

    # run yolo detection
    analysis_path = "output/analysis.json"

    if not os.path.exists(analysis_path):
        print("[Pulse] Loading YOLO model...")
        model = load_model()
        print("[Pulse] Analysing frames...")

        analysis_results = []
        prev_frame = None

        for i, frame_info in enumerate(metadata["frames"]):
            frame = cv2.imread(os.path.join(
                frames_dir, frame_info["filename"]))

            result = analyse_frame(
                frame=frame,
                prev_frame=prev_frame,
                model=model,
                target_classes=config["target_classes"],
                confidence_threshold=config["confidence_threshold"]
            )

            result["timestamp"] = frame_info["timestamp"]
            result["frame_id"] = frame_info["frame_id"]
            analysis_results.append(result)
            prev_frame = frame

            if (i + 1) % 50 == 0:
                print(
                    f"[Pulse] Processed {i + 1}/{metadata['extracted_frame_count']} frames")

        with open(analysis_path, "w") as f:
            json.dump(analysis_results, f, indent=2)
    else:
        print("[Pulse] Analysis already exists, skipping detection...")

   # detect events
    events_path = "output/events.json"

    if not os.path.exists(events_path):
        print("[Pulse] Detecting events...")
        events = detect_events(
            analysis_path=analysis_path,
            video_path="data/test_clip.mp4",
            sport_config=config
        )
        save_events(events)
    else:
        print("[Pulse] Events already detected, loading...")
        with open(events_path, "r") as f:
            events = json.load(f)

    # score all frames
    print("[Pulse] Scoring frames...")
    scored = score_all_frames(
        analysis_path=analysis_path,
        intensity_weights=config["intensity_weights"],
        max_counts=config["max_counts"],
        events=events,
        event_weights=config.get("event_weights", {})
    )
    save_scores(scored)

  # generate commentary
    clip_duration = metadata["duration_sec"]

    n_highlights = max(3, int(clip_duration/15))
    print("\n[Pulse] Generating commentary for top moments...")
    commentary_results = generate_commentary_for_highlights(
        scored_frames=scored,
        sport_config=config,
        events=events,
        n=n_highlights
    )

    with open("output/commentary.json", "w", encoding="utf-8") as f:
        json.dump(commentary_results, f, indent=2)

    print("\n--- Commentary highlights ---")
    for item in commentary_results:
        event_label = f" [{item['event'].upper()}]" if item["event"] else ""
        print(
            f"\n  t={item['timestamp']}s | intensity={item['intensity']}{event_label}")
        print(f"  \"{item['commentary']}\"")

    top = max(scored, key=lambda x: x["intensity"])
    print(f"\n--- Most exciting moment ---")
    print(f"  Timestamp : {top['timestamp']}s")
    print(f"  Intensity : {top['intensity']} / 10")
    print(f"  Motion    : {top['motion_score']}")

    # synthesize voice
    print("\n[Pulse] Synthesising commentary audio...")
    audio_results = synthesise_all_commentary(commentary_results)

    with open("output/audio_manifest.json", "w") as f:
        json.dump(audio_results, f, indent=2)

    print(f"\n[Pulse] {len(audio_results)} audio files saved to output/audio/")

    # final video orchestration
    print("\n[Pulse] Orchestrating final video...")
    final_video_path = orchestrate(
        video_path="data/test_clip.mp4",
        audio_manifest_path="output/audio_manifest.json",
        scores_path="output/scores.json",
        output_path="output/final_output.mp4"
    )
    print(f"\n[Pulse] Done. Final video: {final_video_path}")
