from pydub import AudioSegment
import os


def get_music_category(intensity_score):
    if intensity_score <= 3.0:
        return "low"
    elif intensity_score <= 6.5:
        return "mid"
    else:
        return "high"


def load_music_track(category):
    """
    Tries both 'mid.mp3' and 'medium.mp3' — handles whichever filename exists.
    """
    music_dir = os.path.join(os.path.dirname(__file__), "..", "music")

    # Handle mid/medium naming inconsistency
    candidates = [category]
    if category == "mid":
        candidates.append("medium")
    elif category == "medium":
        candidates.append("mid")

    for name in candidates:
        path = os.path.join(music_dir, f"{name}.mp3")
        if os.path.exists(path):
            return AudioSegment.from_mp3(path)

    raise FileNotFoundError(
        f"No music track found for category '{category}'. "
        f"Looked for: {[c + '.mp3' for c in candidates]} in {music_dir}"
    )


def fit_music_to_duration(track, duration_ms):
    if duration_ms <= 0:
        return AudioSegment.silent(duration=0)

    original = track
    while len(track) < duration_ms:
        track += original

    return track[:duration_ms]


def apply_fade(track, fade_ms=None):

    if fade_ms is None:
        fade_ms = min(1500, len(track)//4)
    return track.fade_in(fade_ms).fade_out(fade_ms)


def generate_music_bed(intensity_score, duration_ms):
    category = get_music_category(intensity_score)
    track = load_music_track(category)
    track = fit_music_to_duration(track, duration_ms)
    return apply_fade(track)
