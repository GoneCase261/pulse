import cv2
import numpy as np
import os


def detect_goal_zone(video_path, scan_frames=30):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    best_zone = None
    best_score = 0
    frames_checked = 0

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Sample evenly across first 20% of video
    sample_indices = np.linspace(
        0, int(total_frames * 0.2), scan_frames, dtype=int)

    for idx in sample_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]

        # Only look between y 15% and 65% — goal is never at very top or bottom
        roi_y1 = int(h * 0.15)
        roi_y2 = int(h * 0.65)
        roi = frame[roi_y1:roi_y2, :]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Stricter white mask — goalposts are pure white
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        kernel = np.ones((3, 3), np.uint8)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            roi_h = roi_y2 - roi_y1

            # Must be at least 2% but no more than 25% of frame area
            # Filters out tiny noise AND giant ad boards
            if area < (h * w * 0.02) or area > (h * w * 0.25):
                continue

            x, y, cw, ch = cv2.boundingRect(contour)

            # Aspect ratio between 1.5 and 5.0 — goals are wide but not infinite
            aspect_ratio = cw / ch if ch > 0 else 0
            if aspect_ratio < 1.5 or aspect_ratio > 5.0:
                continue

            # Width between 15% and 55% of frame width
            if cw < w * 0.15 or cw > w * 0.55:
                continue

            # Must be in horizontal center — goals appear center or slightly off
            center_x = (x + cw / 2) / w
            if center_x < 0.15 or center_x > 0.85:
                continue

            # Score = area * aspect bonus
            score = area * min(aspect_ratio, 3.0)

            if score > best_score:
                best_score = score
                pad_x = 0.03
                pad_y = 0.04

                abs_y = (roi_y1 + y) / h
                abs_y2 = (roi_y1 + y + ch) / h

                best_zone = {
                    "x_min": max(0.0, (x / w) - pad_x),
                    "x_max": min(1.0, ((x + cw) / w) + pad_x),
                    "y_min": max(0.0, abs_y - pad_y),
                    "y_max": min(1.0, abs_y2 + pad_y + 0.06)
                }

        frames_checked += 1

    cap.release()

    if best_zone:
        print(f"[Pulse] Goal zone detected: {best_zone}")
    else:
        print("[Pulse] Goal zone not detected, falling back to config.")

    return best_zone


def detect_net_motion(frames_data, frames_dir, goal_zone, motion_threshold=2.0):
    """
    Uses already-extracted frames from disk instead of raw video.
    Much faster — no video decoding needed.
    """
    net_motion_events = []
    prev_gray_crop = None
    prev_timestamp = -5.0

    for frame_info in frames_data:
        frame_path = os.path.join(frames_dir, frame_info["filename"])
        frame = cv2.imread(frame_path)

        if frame is None:
            continue

        timestamp = frame_info["timestamp"]
        h, w = frame.shape[:2]

        x1 = int(goal_zone["x_min"] * w)
        x2 = int(goal_zone["x_max"] * w)
        y1 = int(goal_zone["y_min"] * h)
        y2 = int(goal_zone["y_max"] * h)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        if prev_gray_crop is not None and prev_gray_crop.shape == gray_crop.shape:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray_crop, gray_crop,
                None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0
            )

            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_motion = float(np.mean(magnitude))

            if avg_motion > motion_threshold:
                if timestamp - prev_timestamp > 2.0:
                    net_motion_events.append({
                        "timestamp": timestamp,
                        "avg_motion": round(avg_motion, 3)
                    })
                    prev_timestamp = timestamp

        prev_gray_crop = gray_crop

    print(f"[Pulse] Net motion events: {len(net_motion_events)}")
    return net_motion_events
