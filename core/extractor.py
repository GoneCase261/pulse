import cv2
import os
import json
from pathlib import Path


def extract_frames(video_path, output_dir, fps_target=2):
    # Open video
    cap = cv2.VideoCapture(video_path)

    # Check if not opened succesfully
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video:{video_path}")

    # Read video's properties
    native_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames/native_fps

    frame_interval = max(1, int(native_fps / fps_target))
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    saved_frames = []
    frame_index = 0
    extracted_count = 0

    print(f"[Pulse] Extraction from: {Path(video_path)}")
    print(
        f"[Pulse] Duration:{duration_sec}s | Native FPS: {native_fps} | Interval: every {frame_interval} frames")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_index % frame_interval == 0:
            timestamp = frame_index/native_fps

            filename = f"frame_{extracted_count:04d}_t{timestamp:.2f}s.jpg"
            filepath = os.path.join(output_dir, filename)

            # Save the fram as a jpg image
            cv2.imwrite(filepath, frame)

            # Record this frame's info
            saved_frames.append({
                "frame_id": extracted_count,
                "filename": filename,
                "timestamp": round(timestamp, 3)
            })

            extracted_count += 1

        frame_index += 1

    cap.release()  # done with this video, u can free up memory

    # Save evrything about this extraction as JSON
    metadata = {
        "video_path": str(video_path),
        "duration_sec": round(duration_sec, 3),
        "native_fps": native_fps,
        "target_fps": fps_target,
        "resolution": {"width": width, "height": height},
        "total_native_frames": total_frames,
        "extracted_frame_count": extracted_count,
        "frames": saved_frames
    }

    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[Pulse] Done - {extracted_count} frames saved to {output_dir}")

    return metadata
