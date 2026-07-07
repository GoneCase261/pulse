def detect_zoom(frames, zoom_threshold):
    zoom_frames = set()

    for i in range(1, len(frames)):
        prev = frames[i - 1]
        curr = frames[i]

        prev_areas = []
        curr_areas = []

        for obj in prev["detections"]:
            for box in prev["detections"][obj]["boxes"]:
                prev_areas.append(box["area"])

        for obj in curr["detections"]:
            for box in curr["detections"][obj]["boxes"]:
                curr_areas.append(box["area"])

        if not prev_areas or not curr_areas:
            continue

        prev_avg = sum(prev_areas) / len(prev_areas)
        curr_avg = sum(curr_areas) / len(curr_areas)

        if prev_avg == 0:
            continue

        change = (curr_avg - prev_avg) / prev_avg

        if abs(change) > zoom_threshold:
            zoom_frames.add(i)

    return zoom_frames
