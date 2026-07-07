import cv2
import numpy as np
from ultralytics import YOLO


def load_model(model_size="yolov8n"):
    # load yolo model
    return YOLO(f"{model_size}.pt")


def calculate_motion_score(frame_a, frame_b):
    """
    Compare two frames and return a motion score 0-100.
    Higher score = more movement between frames.
    """
    # Convert to grayscale — we only need brightness changes
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)

    # Get absolute difference between frames
    diff = cv2.absdiff(gray_a, gray_b)

    # Blur to reduce camera noise
    diff = cv2.GaussianBlur(diff, (5, 5), 0)

    # Average brightness of difference = average motion
    motion_score = float(np.mean(diff))

    # Scale to 0-100
    return round(min(100.0, motion_score * 2), 2)


def detect_objects(frame, model, target_classes, confidence_threshold=0.4):
    """
    Runs on each single frame.
    Detects objects only specified in target_classes.
    target_classes: dict of {class_id: label} from sport config.
    Returns count and bounding box data for each detected class.
    """
    results = model(frame, verbose=False)
    boxes = results[0].boxes

    # Start with empty structure for every target class
    detections = {
        label: {"count": 0, "boxes": []}
        for label in target_classes.values()
    }

    if boxes is not None:
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id in target_classes and confidence >= confidence_threshold:
                label = target_classes[class_id]

                # Get bounding box corners
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Calculate center and area
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                area = (x2 - x1) * (y2 - y1)

                detections[label]["count"] += 1
                detections[label]["boxes"].append({
                    "center": [round(center_x, 1), round(center_y, 1)],
                    "area": round(area, 1)
                })

    return detections


def analyse_frame(frame, prev_frame, model, target_classes, confidence_threshold=0.4):
    # Combine motion score and detections into one result dict.

    if prev_frame is not None:
        motion = calculate_motion_score(prev_frame, frame)
    else:
        motion = 0.0

    # Object detection for particular sport
    detections = detect_objects(
        frame, model, target_classes, confidence_threshold)

    return {
        "motion_score": motion,
        "detections": detections
    }
