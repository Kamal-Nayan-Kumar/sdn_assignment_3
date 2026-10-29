#!/usr/bin/env python3
"""
generate_kalpit_audio.py - Generate natural, calm, friendly male voice narration
using Sarvam AI TTS with speaker 'kalpit_en_edtech'.
"""

import os
import requests
import json
import base64
import subprocess

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_kalpit")
os.makedirs(AUDIO_DIR, exist_ok=True)

API_KEY = "sk_17jnf99y_eHeuiqstgxn8lEKBATh9k9Am"
URL = "https://api.sarvam.ai/text-to-speech"
HEADERS = {
    "api-subscription-key": API_KEY,
    "Content-Type": "application/json"
}

SCENES = [
    {
        "id": 1,
        "title": "Introduction & O-RAN Architecture",
        "inputs": [
            "Welcome to the demonstration of Software Defined Networking Assignment 3 for course EC 466, presented by Group 19. We deploy the O-RAN Software Community Near-Real-Time Radio Intelligent Controller and collect radio telemetry using containerized Python xApps.",
            "Open RAN disaggregates monolithic base stations into open functional units. The Near-RT RIC operates control loops between 10 milliseconds and 1 second over the E2 interface, hosting xApps that optimize radio resources."
        ]
    },
    {
        "id": 2,
        "title": "Objective 1: Multi-Container RIC Deployment",
        "inputs": [
            "For Objective 1, we deploy the Near-RT RIC multi-container platform using Docker Compose. All seven microservices communicate across an internal Docker bridge network on subnet 10.0.2.0/24.",
            "We verify the Docker runtime, launch the containers, and inspect active container health. The RIC Message Router provides low-latency messaging, while Redis backs the Radio Network Information Base."
        ]
    },
    {
        "id": 3,
        "title": "Objective 1: Component Inspection & Protocol Logs",
        "inputs": [
            "Inspecting the microservices verifies that E2 Termination listens for base stations on SCTP port 36421 and RMR port 38000. E2 Manager maintains base station connectivity in Redis on RMR port 3801.",
            "Subscription Manager coordinates subscriptions on RMR port 4560 and exposes its REST API on port 8088. We verify active E2 termination in Redis and review the static routing table routes.rtg."
        ]
    },
    {
        "id": 4,
        "title": "Objective 2: Monitoring xApp & User Throughput",
        "inputs": [
            "In Objective 2, we execute the monitoring xApp inside the python xApp runner container. The xApp initiates an HTTP REST subscription targeting the gNodeB with Subscription ID 65 under E2SM-KPM Report Style 1.",
            "Periodic RIC Indication messages arrive over RMR every 1000 milliseconds, decoding real-time throughput of 16.55 Megabits per second downlink and 5.22 Megabits per second uplink."
        ]
    },
    {
        "id": 5,
        "title": "Objective 2: Metric Reconfiguration (RLC Volumes & Reliability)",
        "inputs": [
            "Next, we reconfigure the monitoring xApp to inspect lower-layer radio metrics. We subscribe to cumulative layer-2 RLC transmitted volume and QoS packet delivery reliability.",
            "Telemetry arrives with Subscription ID 66, displaying downlink volume accumulating to 8.4 Megabytes and uplink volume to 4.2 Megabytes, maintaining zero packet loss and 100 percent packet success."
        ]
    },
    {
        "id": 6,
        "title": "Advanced Telemetry, Upstream Bug Fix & Summary",
        "inputs": [
            "Finally, we evaluate E2SM-KPM Report Style 5, extracting per-user telemetry for individual connected UEs, confirming User 0 receives 10.2 Megabits per second with high CQI and strong signal power.",
            "We also resolved an upstream bug in the official Python framework, where sys.getsizeof caused APER decoding failures, verified by 8 out of 8 passing pytest tests. All code and the 18-page technical report are packaged in the final submission bundle."
        ]
    }
]

def generate_audio():
    total_duration = 0.0
    durations = {}

    for scene in SCENES:
        s_id = scene["id"]
        wav_path = os.path.join(AUDIO_DIR, f"scene_{s_id}.wav")
        mp3_path = os.path.join(AUDIO_DIR, f"scene_{s_id}.mp3")

        print(f"[*] Requesting Sarvam AI (kalpit_en_edtech) for Scene {s_id}: {scene['title']}...")
        payload = {
            "inputs": scene["inputs"],
            "target_language_code": "en-IN",
            "speaker": "kalpit_en_edtech",
            "pitch": 0,
            "pace": 1.05,
            "loudness": 1.0,
            "speech_sample_rate": 24000,
            "enable_preprocessing": True,
            "model": "bulbul:v4-flash"
        }

        resp = requests.post(URL, headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Sarvam API Error ({resp.status_code}): {resp.text}")

        data = resp.json()
        audio_b64 = data["audios"][0]
        audio_bytes = base64.b64decode(audio_b64)

        with open(wav_path, "wb") as f:
            f.write(audio_bytes)

        # Convert to 44.1kHz stereo MP3 with ffmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_path,
            "-ar", "44100", "-ac", "2", "-b:a", "192k",
            mp3_path
        ], check=True, stderr=subprocess.DEVNULL)
        os.remove(wav_path)

        # Probe duration
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", mp3_path
        ], capture_output=True, text=True, check=True)
        dur = float(json.loads(probe.stdout)["format"]["duration"])
        durations[s_id] = dur
        total_duration += dur
        print(f"    -> Generated {mp3_path} ({dur:.2f} seconds)")

    print("\n" + "="*55)
    print(f"Total Narration Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print("="*55)
    return durations

if __name__ == "__main__":
    generate_audio()
