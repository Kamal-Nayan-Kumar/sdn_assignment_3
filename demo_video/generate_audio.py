#!/usr/bin/env python3
"""
generate_audio.py - Generate voice narration tracks for demo video using macOS 'say'
and encode them into clean MP3/AAC audio files.
"""

import os
import subprocess
import json

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "Samantha" # High quality natural voice on macOS
RATE = "175"       # Natural reading cadence (words per minute)

SCENES = [
    {
        "id": 1,
        "title": "Introduction & Overview",
        "text": "Welcome to the project demonstration guide for Software Defined Networking Assignment 3, presented by Group 19. In this assignment, we deploy the O-RAN Software Community Near-Real-Time Radio Intelligent Controller, examine its decoupled microservices, and demonstrate real-time radio measurement telemetry using containerized Python xApps."
    },
    {
        "id": 2,
        "title": "O-RAN & Near-RT RIC Architecture",
        "text": "Open RAN disaggregates monolithic cellular base stations into standardized, interoperable functional units. The Service Management and Orchestration layer hosts non-real-time rApps over the A1 interface for long-term policies. At the network edge, the Near-Real-Time RIC executes control loops between 10 milliseconds and 1 second over the E2 interface, hosting xApps that optimize radio resources and collect live telemetry."
    },
    {
        "id": 3,
        "title": "Objective 1: Multi-Container Platform Deployment",
        "text": "For Objective 1, we deploy the Near-RT RIC as a multi-container platform using Docker Compose without requiring Kubernetes or Helm. All seven microservices communicate across an internal Docker bridge network on subnet 10.0.2.0/24. The RIC Message Router provides low-latency peer-to-peer messaging, while Redis backs the Radio Network Information Base."
    },
    {
        "id": 4,
        "title": "Objective 1: Component Inspection & Protocol Logs",
        "text": "Inspecting the microservices verifies that the E2 Termination point listens for base stations on SCTP port 36421 and connects to RMR on port 38000. The E2 Manager maintains node states in Redis on port 3801, and the Subscription Manager exposes its REST server on port 8088. Static routing table routes.rtg directs message types such as 12010 for subscriptions and 12050 for indications."
    },
    {
        "id": 5,
        "title": "Objective 2: Monitoring xApp & User Throughput",
        "text": "In Objective 2, we execute the monitoring xApp inside the python xApp runner container. The xApp dispatches a REST subscription request to the Subscription Manager targeting the connected gNodeB. Upon receiving periodic RIC Indication messages over RMR, the xApp decodes the payload, observing downlink throughput averaging 16.55 Megabits per second and uplink throughput averaging 5.22 Megabits per second."
    },
    {
        "id": 6,
        "title": "Objective 2: Metric Reconfiguration (RLC Volume & Reliability)",
        "text": "Next, we reconfigure the monitoring xApp to inspect lower-layer radio metrics. The xApp subscribes to cumulative RLC transmitted data volumes, packet drop rates, and uplink success rates. Telemetry reveals steady linear byte volume accumulation up to 8.4 Megabytes downlink and 4.2 Megabytes uplink, maintaining zero packet loss and a 100 percent packet delivery success rate."
    },
    {
        "id": 7,
        "title": "Advanced UE-Level Telemetry & Channel Quality",
        "text": "Using E2SM-KPM Report Style 5, we demonstrate fine-grained per-user telemetry indexed by user identifier. This provides the granular data required for user-specific slicing and scheduling. Our telemetry plots confirm that User 0 receives 10.2 Megabits per second, with physical radio channel indicators showing high CQI values and strong signal power."
    },
    {
        "id": 8,
        "title": "Upstream Bug Fix & Project Summary",
        "text": "During framework investigation, we diagnosed and resolved an upstream bug in the official Python framework, where sys.getsizeof caused APER decoding failures. Replacing it with buffer length restored reliable decoding, verified by 8 out of 8 passing pytest unit tests. All code, configuration files, and the 18-page technical report are packaged in the final submission bundle."
    }
]

def generate_scene_audio():
    total_duration = 0.0
    durations = {}

    for scene in SCENES:
        s_id = scene["id"]
        aiff_path = os.path.join(AUDIO_DIR, f"scene_{s_id}.aiff")
        mp3_path = os.path.join(AUDIO_DIR, f"scene_{s_id}.mp3")

        print(f"[*] Generating speech for Scene {s_id}: {scene['title']}...")
        subprocess.run(["say", "-v", VOICE, "-r", RATE, scene["text"], "-o", aiff_path], check=True)
        # Convert to 44.1kHz stereo MP3
        subprocess.run([
            "ffmpeg", "-y", "-i", aiff_path,
            "-ar", "44100", "-ac", "2", "-b:a", "192k",
            mp3_path
        ], check=True, stderr=subprocess.DEVNULL)
        os.remove(aiff_path)

        # Get exact duration using ffprobe
        probe_res = subprocess.run([
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", mp3_path
        ], capture_output=True, text=True, check=True)
        dur = float(json.loads(probe_res.stdout)["format"]["duration"])
        durations[s_id] = dur
        total_duration += dur
        print(f"    -> Duration: {dur:.2f}s")

    print("\n" + "="*50)
    print(f"Total Video Runtime: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print("="*50)
    return durations

if __name__ == "__main__":
    generate_scene_audio()
