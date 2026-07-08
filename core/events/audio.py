import librosa
import warnings
import numpy as np

# crowd energy per second


def detect_audio_shape(video_path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        audio, sr = librosa.load(video_path, sr=None, mono=True)

    chunk_size = sr
    # ceil to include last partial second
    num_chunks = int(np.ceil(len(audio) / chunk_size))

    energies = []
    for i in range(num_chunks):
        chunk = audio[i * chunk_size:(i + 1) * chunk_size]
        energy = float(np.mean(chunk ** 2))
        energies.append(energy)

    if not energies:
        return [], {}

    avg_energy = sum(energies) / len(energies)
    max_energy = max(energies)
    # lowered from 1.4 to catch saves and near misses
    spike_threshold = avg_energy * 1.4

    energy_timeline = {}
    for i, energy in enumerate(energies):
        normalised = round(energy / max_energy, 4) if max_energy > 0 else 0.0
        energy_timeline[str(i)] = normalised

    events = []
    i = 0
    while i < len(energies):
        if energies[i] > spike_threshold:
            spike_start = i
            sustained_count = 0
            j = i
            while j < len(energies) and energies[j] > spike_threshold:
                sustained_count += 1
                j += 1

            confidence = round(
                min(1.0, energies[i] / (avg_energy * 1.4)), 2)

            if sustained_count >= 4:
                events.append({
                    "timestamp": float(spike_start),
                    "event": "goal_audio",
                    "confidence": confidence,
                    "sustained_seconds": sustained_count
                })
            elif sustained_count >= 1:
                events.append({
                    "timestamp": float(spike_start),
                    "event": "near_miss_audio",
                    "confidence": confidence,
                    "sustained_seconds": sustained_count
                })
            i = j
        else:
            i += 1

    print(f"[Pulse] Audio events detected: {len(events)}")
    return events, energy_timeline
