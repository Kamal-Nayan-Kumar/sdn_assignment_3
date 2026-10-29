#!/usr/bin/env python3
"""
assemble_video.py - Encode individual scene video clips and concatenate into
a complete 1080p MP4 demonstration video with synchronized voice narration.
"""

import os
import subprocess
import json

VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(VIDEO_DIR, "slides")
AUDIO_DIR = os.path.join(VIDEO_DIR, "audio")
CLIPS_DIR = os.path.join(VIDEO_DIR, "clips")
FINAL_MP4 = os.path.join(VIDEO_DIR, "demo_video.mp4")

os.makedirs(CLIPS_DIR, exist_ok=True)

def build_scene_clips():
    clip_paths = []
    for s_id in range(1, 9):
        slide_img = os.path.join(SLIDES_DIR, f"slide_{s_id}.png")
        audio_mp3 = os.path.join(AUDIO_DIR, f"scene_{s_id}.mp3")
        clip_mp4 = os.path.join(CLIPS_DIR, f"clip_{s_id}.mp4")

        print(f"[*] Encoding Scene {s_id} clip...")
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", slide_img,
            "-i", audio_mp3,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-pix_fmt", "yuv420p",
            "-shortest",
            clip_mp4
        ]
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        clip_paths.append(clip_mp4)

    # Concat file
    list_path = os.path.join(CLIPS_DIR, "concat_list.txt")
    with open(list_path, "w") as f:
        for c in clip_paths:
            f.write(f"file '{c}'\n")

    print("[*] Concatenating clips into final demo_video.mp4...")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        FINAL_MP4
    ]
    subprocess.run(concat_cmd, check=True, stderr=subprocess.DEVNULL)

    # Inspect final video
    probe_cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        FINAL_MP4
    ]
    probe_out = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    meta = json.loads(probe_out.stdout)

    duration = float(meta["format"]["duration"])
    size_mb = float(meta["format"]["size"]) / (1024 * 1024)
    print("\n" + "="*55)
    print(f"Final Video: {FINAL_MP4}")
    print(f"Resolution : 1920x1080 (Full HD, 30 fps)")
    print(f"Duration   : {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"File Size  : {size_mb:.2f} MB")
    print("="*55)

if __name__ == "__main__":
    build_scene_clips()
