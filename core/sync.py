import json
import os
from moviepy import VideoFileClip, AudioFileClip
from pydub import AudioSegment
from core.music import generate_music_bed


def build_chunked_music_bed(scores, duration_ms, chunk_duration_s=10):
    """
    Splits scores into chunks of chunk_duration_s seconds.
    Each chunk gets its own avg intensity and music segment.
    Joins all segments into one continuous music bed.
    """
    chunk_duration_ms = chunk_duration_s * 1000
    num_chunks = max(1, int(duration_ms / chunk_duration_ms))

    full_music_bed = AudioSegment.silent(duration=0)

    for i in range(num_chunks):
        chunk_start_s = i * chunk_duration_s
        chunk_end_s = chunk_start_s + chunk_duration_s

        chunk_scores = [
            f["intensity"] for f in scores
            if chunk_start_s <= f["timestamp"] < chunk_end_s
        ]

        if chunk_scores:
            chunk_avg = sum(chunk_scores) / len(chunk_scores)
        else:
            chunk_avg = sum(f["intensity"] for f in scores) / len(scores)

        remaining_ms = duration_ms - len(full_music_bed)
        segment_ms = min(chunk_duration_ms, remaining_ms)

        segment = generate_music_bed(chunk_avg, segment_ms)
        full_music_bed += segment

    return full_music_bed


def orchestrate(video_path, audio_manifest_path, scores_path, output_path, lead_offset_s=1.5):

    with open(scores_path, "r", encoding="utf-8") as f:
        scores = json.load(f)

    video = VideoFileClip(video_path)
    if video.audio is None:
        raise ValueError("Input video does not contain an audio track.")

    video.audio.write_audiofile("output/temp_game_audio.mp3")
    game_audio = AudioSegment.from_mp3("output/temp_game_audio.mp3")

    duration_ms = len(game_audio)

    music_bed = build_chunked_music_bed(scores, duration_ms)
    print(f"[Pulse] Music bed built — {len(music_bed) / 1000:.1f}s")

    music_bed -= 0
    final_mix = game_audio.overlay(music_bed)

    with open(audio_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    prev_clip_end_ms = 0

    for entry in manifest:

        entry_lead = entry.get("lead_offset", lead_offset_s)
        position_ms = int((entry["timestamp"] - entry_lead) * 1000)

        position_ms = max(0, position_ms)

        if position_ms < prev_clip_end_ms:
            is_real_event = entry.get("event") in (
                "goal", "near_miss", "crowd_spike")
            if is_real_event:
                position_ms = prev_clip_end_ms + 3
            else:
                print(
                    f"[Pulse] Skipping t={entry['timestamp']}s — no real event, would overlap")
                continue

        audio_path = os.path.normpath(entry["audio_path"])
        clip = AudioSegment.from_mp3(audio_path)
        final_mix = final_mix.overlay(clip, position=position_ms)

        prev_clip_end_ms = position_ms + len(clip)

    # export mixed audio
    final_mix.export("output/temp_final_audio.mp3", format="mp3")

    # attach to video and export
    final_audio = AudioFileClip("output/temp_final_audio.mp3")
    final_video = video.with_audio(final_audio)
    final_video.write_videofile(
        output_path, codec="libx264", audio_codec="aac")

    # clean up(files not required once final video ready)
    os.remove("output/temp_game_audio.mp3")
    os.remove("output/temp_final_audio.mp3")

    return output_path
