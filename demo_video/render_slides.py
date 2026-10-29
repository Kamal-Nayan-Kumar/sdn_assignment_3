#!/usr/bin/env python3
"""
render_slides.py - Render high-definition (1920x1080) slide frames for the demo video.
"""

import os
from PIL import Image, ImageDraw, ImageFont

SLIDES_DIR = os.path.join(os.path.dirname(__file__), "slides")
os.makedirs(SLIDES_DIR, exist_ok=True)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIGS_DIR = os.path.join(ROOT_DIR, "report", "figs")
DIAG_DIR = os.path.join(os.path.dirname(__file__), "diagrams")
LOGO_PATH = os.path.join(ROOT_DIR, "report", "logo.jpeg")

W, H = 1920, 1080

# Color Palette
BG_COLOR = (15, 23, 42)          # #0F172A Dark Slate
CARD_BG = (30, 41, 59)           # #1E293B Card Background
CARD_INNER = (23, 32, 51)        # #172033 Inner Card Background
CARD_BORDER = (51, 65, 85)       # #334155 Slate Border
ACCENT_BLUE = (45, 107, 228)     # #2D6BE4 O-RAN Blue
ACCENT_CYAN = (56, 189, 248)     # #38BDF8 Bright Cyan
ACCENT_GREEN = (31, 122, 61)     # #1F7A3D Pass Green
ACCENT_AMBER = (217, 119, 6)     # #D97706 Amber
TEXT_WHITE = (248, 250, 252)     # #F8FAFC Heading text
TEXT_LIGHT = (203, 213, 225)     # #CBD5E1 Body text
TEXT_MUTED = (148, 163, 184)     # #94A3B8 Secondary text

FONT_TITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
FONT_HEADING = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
FONT_SUBTITLE = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
FONT_BODY = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
FONT_BODY_BOLD = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
FONT_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 17)
FONT_SMALL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)

def create_base_slide(scene_title, scene_num):
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Top Header Banner
    draw.rectangle([0, 0, W, 95], fill=(20, 28, 43))
    draw.line([0, 95, W, 95], fill=ACCENT_BLUE, width=3)

    category_text = "SOFTWARE DEFINED NETWORKS (CS304)  •  ASSIGNMENT 3 DEMO GUIDE"
    draw.text((60, 18), category_text, font=FONT_SMALL, fill=ACCENT_CYAN)
    draw.text((60, 44), f"Scene {scene_num}: {scene_title}", font=FONT_HEADING, fill=TEXT_WHITE)

    scene_indicator = f"Part {scene_num} of 8"
    draw.text((W - 190, 44), scene_indicator, font=FONT_SUBTITLE, fill=TEXT_MUTED)

    # Bottom Footer
    draw.rectangle([0, H - 50, W, H], fill=(20, 28, 43))
    draw.line([0, H - 50, W, H - 50], fill=CARD_BORDER, width=1)
    footer_text = "Group 19  |  IIIT Dharwad  |  O-RAN SC Near-RT RIC Architecture & xApp Telemetry"
    draw.text((60, H - 34), footer_text, font=FONT_SMALL, fill=TEXT_MUTED)

    return img, draw

def draw_card(draw, x, y, w, h, title=None, border_color=CARD_BORDER):
    draw.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=border_color, width=2)
    if title:
        draw.rectangle([x, y, x + w, y + 40], fill=(20, 28, 43))
        draw.line([x, y + 40, x + w, y + 40], fill=border_color, width=1)
        draw.text((x + 16, y + 8), title, font=FONT_BODY_BOLD, fill=ACCENT_CYAN)

def paste_fitted_image(canvas, img_path, target_box, bg_pad=True):
    # target_box: (x, y, w, h)
    bx, by, bw, bh = target_box
    if not os.path.exists(img_path):
        return
    src = Image.open(img_path)
    ratio = min(bw / src.width, bh / src.height)
    new_w = int(src.width * ratio)
    new_h = int(src.height * ratio)
    resized = src.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center inside box
    px = bx + (bw - new_w) // 2
    py = by + (bh - new_h) // 2

    if bg_pad and src.mode in ("RGBA", "P"):
        bg = Image.new("RGBA", resized.size, (255, 255, 255, 255))
        bg.paste(resized, (0, 0), resized)
        canvas.paste(bg, (px, py))
    else:
        canvas.paste(resized, (px, py))

# ------------------------------------------------------------------ #
# Slide 1: Title Card                                                #
# ------------------------------------------------------------------ #
def make_slide_1():
    img, draw = create_base_slide("Project Overview & Student Team", 1)

    draw_card(draw, 80, 130, 1760, 860, border_color=ACCENT_BLUE)

    draw.text((140, 170), "Software Defined Networks (CS304)", font=FONT_SUBTITLE, fill=ACCENT_CYAN)
    draw.text((140, 210), "Assignment 3: O-RAN Near-RT RIC Architecture", font=FONT_TITLE, fill=TEXT_WHITE)
    draw.text((140, 265), "and xApp Radio Measurement Subscriptions via E2SM-KPM", font=FONT_HEADING, fill=TEXT_LIGHT)
    draw.line([140, 330, 1780, 330], fill=CARD_BORDER, width=2)

    draw.text((140, 360), "Team Details (Group No. 19)", font=FONT_HEADING, fill=ACCENT_CYAN)
    
    team_members = [
        ("Kamal Nayan Kumar", "23BDS026", "Lead Architect, Container Orchestration, Telemetry"),
        ("Altaf Raja", "23BCS011", "RIC Component Analysis, Subscription Tracing"),
        ("Ankit Kumar Keshari", "23BCS015", "E2AP & E2SM-KPM Analysis, Bug Diagnostics"),
        ("Soumya Nimje", "23BEC054", "Radio Metrics Exploration, LaTeX Documentation"),
    ]

    y_pos = 420
    for name, roll, role in team_members:
        draw.rectangle([140, y_pos, 1050, y_pos + 68], fill=CARD_INNER, outline=CARD_BORDER, width=1)
        draw.text((160, y_pos + 10), name, font=FONT_BODY_BOLD, fill=TEXT_WHITE)
        draw.text((450, y_pos + 12), f"({roll})", font=FONT_BODY, fill=ACCENT_CYAN)
        draw.text((160, y_pos + 40), role, font=FONT_SMALL, fill=TEXT_LIGHT)
        y_pos += 82

    draw.text((140, 770), "Course Instructor:", font=FONT_BODY_BOLD, fill=TEXT_MUTED)
    draw.text((320, 770), "Dr. Jagadeesha R B", font=FONT_BODY_BOLD, fill=TEXT_WHITE)

    # Right Card: Executed Objectives
    draw.rectangle([1110, 360, 1780, 710], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((1140, 385), "Key Objectives Executed:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)

    bullets = [
        "1. Deploy O-RAN SC Near-RT RIC (i-release) in Docker.",
        "2. Inspect e2term, e2mgr, submgr, dbaas, rtmgr_sim.",
        "3. Map RMR static routing table & Redis RNIB database.",
        "4. Run Python monitoring xApp & subscribe to gNodeB.",
        "5. Collect DL/UL throughput (DRB.UEThpDl, DRB.UEThpUl).",
        "6. Modify telemetry to RLC SDU Volume & packet drop rate.",
        "7. Compare Report Style 1 (Node) vs. Style 5 (Per-UE).",
        "8. Fix upstream sys.getsizeof APER decode bug."
    ]
    by = 430
    for b in bullets:
        draw.text((1140, by), "•", font=FONT_BODY, fill=ACCENT_CYAN)
        draw.text((1165, by), b, font=FONT_SMALL, fill=TEXT_LIGHT)
        by += 32

    # IIIT Dharwad Logo
    if os.path.exists(LOGO_PATH):
        logo_img = Image.open(LOGO_PATH)
        logo_img = logo_img.resize((380, int(logo_img.height * (380 / logo_img.width))), Image.Resampling.LANCZOS)
        logo_bg = Image.new("RGB", (400, logo_img.height + 20), (255, 255, 255))
        logo_bg.paste(logo_img, (10, 10))
        img.paste(logo_bg, (1240, 750))

    out_file = os.path.join(SLIDES_DIR, "slide_1.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 2: O-RAN Reference Architecture                              #
# ------------------------------------------------------------------ #
def make_slide_2():
    img, draw = create_base_slide("O-RAN & Near-RT RIC Architecture Foundations", 2)

    # Left: Diagram
    draw_card(draw, 60, 120, 1020, 880, "O-RAN Disaggregation & Open Interfaces (WG3)")
    fig1_path = os.path.join(DIAG_DIR, "fig1_crop-1.png")
    paste_fitted_image(img, fig1_path, (80, 175, 980, 805), bg_pad=False)

    # Right: Concept Explanations
    draw_card(draw, 1110, 120, 750, 880, "Architecture & Functional Splits")

    y = 180
    sections = [
        ("Service Management & Orchestration (SMO)", [
            "Hosts Non-Real-Time RIC operating at T > 1s.",
            "Executes rApps for long-term policy guidance.",
            "Manages model training over the A1 Interface."
        ]),
        ("Near-Real-Time RIC (Near-RT RIC)", [
            "Operates at the edge with loop 10ms <= T <= 1s.",
            "Hosts microservice-based xApps for fast control.",
            "Connects to disaggregated E2 nodes via E2AP."
        ]),
        ("O-CU Disaggregation (Control & User Planes)", [
            "O-CU-CP: RRC and control-plane PDCP protocols.",
            "O-CU-UP: User-plane SDAP and PDCP traffic.",
            "Connected internally via E1 Interface."
        ]),
        ("O-DU & Open Fronthaul (7-2x Split)", [
            "O-DU executes RLC, MAC, and High-PHY layers.",
            "Open Fronthaul connects O-DU to Low-PHY O-RU."
        ])
    ]

    for title, items in sections:
        draw.text((1135, y), title, font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
        y += 32
        for it in items:
            draw.text((1140, y), "—", font=FONT_BODY, fill=ACCENT_BLUE)
            draw.text((1165, y), it, font=FONT_SMALL, fill=TEXT_LIGHT)
            y += 26
        y += 18

    out_file = os.path.join(SLIDES_DIR, "slide_2.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 3: Objective 1 — Multi-Container Platform Deployment         #
# ------------------------------------------------------------------ #
def make_slide_3():
    img, draw = create_base_slide("Objective 1: Multi-Container Near-RT RIC Platform", 3)

    # Left: Docker PS Table
    draw_card(draw, 60, 120, 920, 880, "Container Orchestration & Status (docker ps)")
    ps_path = os.path.join(FIGS_DIR, "fig_ric_ps.png")
    paste_fitted_image(img, ps_path, (80, 180, 880, 500))

    # Details table below docker ps
    draw.rectangle([80, 700, 960, 970], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((100, 715), "Network Configuration (oran-sc-ric_ric_network):", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    net_items = [
        "Subnet: 10.0.2.0/24 (Docker Bridge Network)",
        "Architecture: linux/amd64 (OrbStack Rosetta 2 Translation)",
        "Core Message Bus: RIC Message Router (RMR) Peer-to-Peer",
        "RNIB Database: Redis 6379 with Shared Data Layer (SDL) engine",
        "E2 Termination: SCTP Port 36421 + RMR Port 38000"
    ]
    ny = 750
    for n in net_items:
        draw.text((100, ny), "•", font=FONT_BODY, fill=ACCENT_BLUE)
        draw.text((125, ny), n, font=FONT_SMALL, fill=TEXT_LIGHT)
        ny += 28

    # Right: Topology Diagram
    draw_card(draw, 1010, 120, 850, 880, "Internal Microservice Topology")
    fig2_path = os.path.join(DIAG_DIR, "fig2_crop-1.png")
    paste_fitted_image(img, fig2_path, (1030, 180, 810, 800), bg_pad=False)

    out_file = os.path.join(SLIDES_DIR, "slide_3.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 4: Objective 1 — Microservice Logs & Component Inspection    #
# ------------------------------------------------------------------ #
def make_slide_4():
    img, draw = create_base_slide("Objective 1: Component Inspection & Protocol Logs", 4)

    # 2x2 Grid of Terminal Captures
    # 1. Top-Left: submgr log
    draw_card(draw, 60, 120, 880, 420, "Subscription Manager (submgr) — RMR 4560, REST 8088")
    submgr_path = os.path.join(FIGS_DIR, "fig_submgr_log.png")
    paste_fitted_image(img, submgr_path, (75, 170, 850, 360))

    # 2. Top-Right: e2mgr log
    draw_card(draw, 980, 120, 880, 420, "E2 Manager (e2mgr) — RNIB Database Sync & RMR 3801")
    e2mgr_path = os.path.join(FIGS_DIR, "fig_e2mgr_log.png")
    paste_fitted_image(img, e2mgr_path, (995, 170, 850, 360))

    # 3. Bottom-Left: e2term SCTP status
    draw_card(draw, 60, 570, 880, 430, "E2 Termination (e2term) — SCTP Port 36421 & RMR 38000")
    e2term_path = os.path.join(FIGS_DIR, "fig_e2term_log.png")
    paste_fitted_image(img, e2term_path, (75, 620, 850, 370))

    # 4. Bottom-Right: Redis DBAAS RNIB keys
    draw_card(draw, 980, 570, 880, 430, "Database as a Service (dbaas) — Active E2T Instance Record")
    dbaas_path = os.path.join(FIGS_DIR, "fig_dbaas_keys.png")
    paste_fitted_image(img, dbaas_path, (995, 620, 850, 370))

    out_file = os.path.join(SLIDES_DIR, "slide_4.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 5: Objective 2 — Monitoring xApp & User Throughput (Scenario 1)#
# ------------------------------------------------------------------ #
def make_slide_5():
    img, draw = create_base_slide("Objective 2: xApp Telemetry — User Plane Throughput", 5)

    # Left: Terminal Output
    draw_card(draw, 60, 120, 880, 880, "Monitoring xApp Execution (simple_mon_xapp.py)")
    term_path = os.path.join(FIGS_DIR, "fig_xapp_run_default.png")
    paste_fitted_image(img, term_path, (80, 170, 840, 640))

    # Observation callouts on bottom left
    draw.rectangle([80, 830, 920, 975], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((100, 845), "Handshake & Subscription Summary:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((100, 875), "• Subscription ID: 65  |  Target E2 Node: gnb_001_001_0000019b", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 905), "• Service Model: E2SM-KPM Report Style 1 (Cell Aggregated Metrics)", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 935), "• Sampling Cadence: 1000ms Reporting Period, 1000ms Granularity", font=FONT_SMALL, fill=TEXT_LIGHT)

    # Right: Telemetry Chart
    draw_card(draw, 980, 120, 880, 880, "Real-Time Throughput Trajectory (DRB.UEThpDl / DRB.UEThpUl)")
    chart_path = os.path.join(FIGS_DIR, "chart_throughput_timeseries.png")
    paste_fitted_image(img, chart_path, (1000, 170, 840, 600))

    # Quantitative analysis on bottom right
    draw.rectangle([1000, 790, 1840, 975], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((1020, 805), "Quantitative Telemetry Observations:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((1020, 835), "• Downlink Throughput: 15.42 to 18.21 Mbps (Mean: 16.55 Mbps)", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1020, 870), "• Uplink Throughput: 4.82 to 5.64 Mbps (Mean: 5.22 Mbps)", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1020, 905), "• Conforms to 10 MHz channel bandwidth with 64-QAM modulation.", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((1020, 935), "• 3:1 DL/UL throughput ratio matches configured TDD frame slot structure.", font=FONT_SMALL, fill=TEXT_LIGHT)

    out_file = os.path.join(SLIDES_DIR, "slide_5.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 6: Objective 2 — Metric Reconfiguration (RLC Volumes & QoS)   #
# ------------------------------------------------------------------ #
def make_slide_6():
    img, draw = create_base_slide("Objective 2: Metric Reconfiguration — Layer-2 RLC Volumes", 6)

    # Left: Terminal Output
    draw_card(draw, 60, 120, 880, 880, "Reconfigured xApp Terminal Output (Subscription ID 66)")
    term_path = os.path.join(FIGS_DIR, "fig_xapp_run_modified.png")
    paste_fitted_image(img, term_path, (80, 170, 840, 640))

    draw.rectangle([80, 830, 920, 975], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((100, 845), "Reconfigured Metrics Subscribed:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((100, 875), "• DRB.RlcSduTransmittedVolumeDL: Cumulative Downlink Bytes", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 905), "• DRB.RlcSduTransmittedVolumeUL: Cumulative Uplink Bytes", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 935), "• DRB.RlcPacketDropRateDl (0%)  &  DRB.PacketSuccessRateUlgNBUu (100%)", font=FONT_SMALL, fill=TEXT_LIGHT)

    # Right: Cumulative Volume Chart
    draw_card(draw, 980, 120, 880, 880, "Cumulative RLC SDU Volume Growth Over Time")
    chart_path = os.path.join(FIGS_DIR, "chart_rlc_volume.png")
    paste_fitted_image(img, chart_path, (1000, 170, 840, 600))

    draw.rectangle([1000, 790, 1840, 975], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((1020, 805), "Transmission Reliability & Ingestion Analysis:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((1020, 835), "• Downlink volume increases linearly at ~1.05 MB/s (reaching 8.39 MB).", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1020, 870), "• Uplink volume advances steadily at ~0.52 MB/s (reaching 4.19 MB).", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1020, 905), "• 0% RLC drop rate confirms error-free transport without buffer overflows.", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((1020, 935), "• 100% uplink packet success rate demonstrates perfect link connectivity.", font=FONT_SMALL, fill=TEXT_LIGHT)

    out_file = os.path.join(SLIDES_DIR, "slide_6.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 7: Advanced UE-Level Telemetry & Channel Quality             #
# ------------------------------------------------------------------ #
def make_slide_7():
    img, draw = create_base_slide("Advanced Telemetry: Report Style 5 & Radio Channels", 7)

    # Left: Multi-UE vs Cell Total
    draw_card(draw, 60, 120, 880, 620, "Telemetry Granularity: Cell Total vs. Per-UE Allocation")
    ue_chart = os.path.join(FIGS_DIR, "chart_ue_distribution.png")
    paste_fitted_image(img, ue_chart, (80, 175, 840, 545))

    draw.rectangle([60, 760, 940, 975], fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((80, 775), "Why E2SM-KPM Report Style 5 Matters:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((80, 805), "• Style 1 aggregates all UEs, hiding individual user starvation.", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((80, 840), "• Style 5 indexes measurements by UE_id (UE 0: 10.2M, UE 1: 4.8M, UE 2: 2.5M).", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((80, 875), "• Enables closed-loop slicing control (E2SM-RC / E2SM-CCC PRB quota adjustments).", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((80, 905), "• Essential for proportional fair scheduling and QoS SLA guarantees.", font=FONT_SMALL, fill=TEXT_LIGHT)

    # Right: Physical Radio Metrics
    draw_card(draw, 980, 120, 880, 620, "Physical Layer Channel Quality (CQI, RSRP, RSRQ)")
    rad_chart = os.path.join(FIGS_DIR, "chart_radio_metrics.png")
    paste_fitted_image(img, rad_chart, (1000, 175, 840, 545))

    draw.rectangle([980, 760, 1860, 975], fill=CARD_BG, outline=CARD_BORDER, width=2)
    draw.text((1000, 775), "Radio Channel Link Budget Analysis:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((1000, 805), "• Channel Quality Indicator (CQI) holds high at index 14–15 (64-QAM / 256-QAM).", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1000, 840), "• RSRP ranges between -84 and -80 dBm, confirming high reference signal power.", font=FONT_BODY, fill=TEXT_WHITE)
    draw.text((1000, 875), "• RSRQ holds between -12 and -10 dB, demonstrating low co-channel interference.", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((1000, 905), "• Drives Adaptive Modulation and Coding (AMC) for maximum spectral efficiency.", font=FONT_SMALL, fill=TEXT_LIGHT)

    out_file = os.path.join(SLIDES_DIR, "slide_7.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

# ------------------------------------------------------------------ #
# Slide 8: Upstream Bug Fix & Project Summary                        #
# ------------------------------------------------------------------ #
def make_slide_8():
    img, draw = create_base_slide("Upstream Bug Fix & Project Summary", 8)

    # Left: Pytest Terminal Capture
    draw_card(draw, 60, 120, 880, 880, "Pytest Unit Test Suite (8/8 Passed Post-Fix)")
    test_path = os.path.join(FIGS_DIR, "fig_pytest_e2ap.png")
    paste_fitted_image(img, test_path, (80, 170, 840, 520))

    draw.rectangle([80, 710, 920, 975], fill=CARD_INNER, outline=CARD_BORDER, width=1)
    draw.text((100, 725), "Root Cause & Remediation Summary:", font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
    draw.text((100, 755), "• Bug: sys.getsizeof(payload) included 33B Python wrapper overhead.", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 785), "• Impact: aper_decode_complete rejected valid frames as trailing garbage.", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 815), "• Resolution: Patched ricxappframe/e2ap/asn1.py substituting len(payload).", font=FONT_SMALL, fill=TEXT_LIGHT)
    draw.text((100, 845), "• Verification: 8/8 tests pass, ensuring deterministic telemetry decoding.", font=FONT_SMALL, fill=TEXT_WHITE)

    # Right: Deliverables Summary Card
    draw_card(draw, 980, 120, 880, 880, "Submission Deliverables & Repository State")

    dy = 180
    delivs = [
        ("Complete Technical Report (18 Pages)", [
            "Path: report/report.pdf (Compiled with Tectonic & pdfTeX)",
            "Cover page with Group No. 19 and IIIT Dharwad letterhead",
            "13 terminal capture figures & 4 publication-quality charts",
            "Complete mathematical and protocol analysis of O-RAN E2AP"
        ]),
        ("Submission Zip Bundle", [
            "Path: sdn_assignment3_submission.zip (3.1 MB)",
            "Contains report.pdf at root and complete clean source under code/"
        ]),
        ("Source Code & Automation Pipelines", [
            "bash scripts/run_all.sh — Full automated end-to-end execution",
            "bash report/build.sh — Self-contained LaTeX build runner",
            "bash report/capture.sh — PTY & terminal snapshot pipeline",
            "python3 scripts/generate_charts.py — High-resolution chart generator"
        ]),
        ("GitHub Version Control", [
            "Repository: https://github.com/Kamal-Nayan-Kumar/sdn_assignment_3",
            "Branches synchronized: main and t3/oran-ric-xapp-assignment"
        ])
    ]

    for title, items in delivs:
        draw.text((1010, dy), title, font=FONT_BODY_BOLD, fill=ACCENT_CYAN)
        dy += 30
        for it in items:
            draw.text((1010, dy), "•", font=FONT_BODY, fill=ACCENT_BLUE)
            draw.text((1035, dy), it, font=FONT_SMALL, fill=TEXT_LIGHT)
            dy += 24
        dy += 14

    out_file = os.path.join(SLIDES_DIR, "slide_8.png")
    img.save(out_file)
    print(f"[slide] Saved {out_file}")

def render_all():
    print("[*] Rendering all 8 video slide frames at 1920x1080...")
    make_slide_1()
    make_slide_2()
    make_slide_3()
    make_slide_4()
    make_slide_5()
    make_slide_6()
    make_slide_7()
    make_slide_8()
    print("[*] All 8 slides rendered successfully!")

if __name__ == "__main__":
    render_all()
