# SDN Assignment 3: O-RAN Near-RT RIC Architecture & xApp Telemetry

Deployment and evaluation of the O-RAN Software Community (O-RAN SC) Near-Real-Time Radio Intelligent Controller (Near-RT RIC, `i-release`) and automated radio measurement telemetry using Python xApps.

**Start with [`report/report.pdf`](report/report.pdf)** for the complete 16-page report, including architecture diagrams, component analysis, protocol workflows, and 13 terminal screenshots.

---

## Course & Team Information

- **Course:** Software Defined Networking (CS304)
- **Instructor:** Dr. Jagadeesha R B
- **Group:** Group No. 19
- **Members:**
  - Kamal Nayan Kumar (23BDS026)
  - Altaf Raja (23BCS011)
  - Ankit Kumar Keshari (23BCS015)
  - Soumya Nimje (23BEC054)

---

## What's Here

| Path | Description |
|---|---|
| **`report/report.pdf`** | **The complete 16-page technical report.** |
| `report/report.tex` | LaTeX source code with custom TikZ architecture diagrams. |
| `report/figs/` | 13 terminal captures with dark window styling and traffic lights. |
| `report/build.sh` | One-command compilation script supporting both Tectonic and pdfTeX. |
| `report/capture.sh` | Automated pipeline capturing commands and rendering terminal PNGs. |
| `report/render_term.py` | Python renderer converting ANSI terminal transcripts to styled PNGs. |
| `report/logo.jpeg` | Institute letterhead logo. |
| `oran-sc-ric/` | O-RAN SC Near-RT RIC multi-container deployment (`docker-compose.yml`, `.env`). |
| `oran-sc-ric/ric/configs/` | Service configurations (`routes.rtg`, `e2mgr.yaml`, `submgr.yaml`, `e2term.conf`). |
| `oran-sc-ric/ric/images/` | Dockerfiles for `rtmgr_sim` and `python_xapp_runner`. |
| `oran-sc-ric/xApps/python/` | Python xApps, ASN.1 specifications, and shared libraries. |
| `oran-sc-ric/xApps/python/run_telemetry_demo.py` | Telemetry driver demonstrating default, modified, and UE-level metrics. |
| `scripts/run_ric.sh` | Starts Docker Compose and verifies all seven RIC microservices. |
| `scripts/run_all.sh` | Full automated workflow: launches RIC, runs telemetry, captures logs, builds PDF. |
| `make_submission.sh` | Packages the final submission zip bundle. |

---

## One-Command Start

To run the entire assignment workflow from start to finish:

```bash
bash scripts/run_all.sh
```

This script:
1. Verifies the Docker container runtime and brings up all seven Near-RT RIC microservices.
2. Executes the telemetry scenarios inside `python_xapp_runner`.
3. Captures fresh terminal screenshots into `report/figs/`.
4. Compiles `report/report.tex` into `report/report.pdf`.

---

## Step-by-Step Execution Guide

If you prefer to run each step manually:

### 1. Launch the Near-RT RIC Multi-Container Platform

```bash
bash scripts/run_ric.sh
```

Or directly via Docker Compose:

```bash
cd oran-sc-ric
DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose up -d
docker ps
```

All seven microservices will start on the internal bridge network `oran-sc-ric_ric_network` (`10.0.2.0/24`).

### 2. Run Telemetry Scenarios

Execute the telemetry driver inside `python_xapp_runner`:

#### Scenario A: Default Throughput Collection (Report Style 1)
Subscribes to cell-level downlink and uplink data radio bearer throughput (`DRB.UEThpDl`, `DRB.UEThpUl`):

```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode default --iterations 3
```

#### Scenario B: Modified Layer-2 RLC & Reliability Metrics
Reconfigures metrics to collect transmitted RLC volumes, packet drop rates, and delivery success rates:

```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode modified --iterations 3
```

#### Scenario C: Radio Channel Quality Metrics
Subscribes to physical layer channel quality indicators and reference signal powers:

```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode channel --iterations 3
```

#### Scenario D: Advanced UE-Level Telemetry (Report Style 5)
Demonstrates multi-UE granular telemetry reporting indexed by `UE_id`:

```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode ue_level --iterations 3
```

### 3. Run Unit Tests & Verify Bug Fix

Run pytest inside the xApp container to verify that all E2AP ASN.1 decoding tests pass:

```bash
docker exec python_xapp_runner pytest /opt/ric-plt-xapp-frame-py/tests/test_e2ap.py -v --disable-warnings
```

### 4. Regenerate Terminal Screenshots

```bash
bash report/capture.sh
```

Generates 13 high-resolution PNG images in `report/figs/` using `Menlo` font and macOS terminal window chrome.

### 5. Compile the LaTeX Report

```bash
bash report/build.sh
```

Compiles `report/report.tex` into `report/report.pdf` using Tectonic or pdfTeX.

### 6. Create Submission Archive

```bash
bash make_submission.sh
```

Generates `sdn_assignment3_submission.zip` with `report.pdf` at the archive root and all source code under `code/`.

---

## Near-RT RIC Architecture & Components

The Near-RT RIC controls radio resource management in loops between 10 ms and 1 second over the E2 interface.

```
                      +-----------------------------+
                      |   Python Monitoring xApp    |
                      |    (python_xapp_runner)     |
                      +--------------+--------------+
                        |            ^
        REST Subscribe  |            | RIC_INDICATION (12050)
         (Port 8088)    v            |
    +-------------------+    +-------+----------+    +-------------------+
    | Subscription Mgr  |    |    E2 Manager    |    |  Routing Mgr Sim  |
    | (submgr: 4560)    |    |   (e2mgr: 3801)  |    | (rtmgr_sim: 12020)|
    +---------+---------+    +-------+----------+    +---------+---------+
              |                      |                         |
==============+======================+=========================+==============
                     RIC Message Router (RMR) Interconnect
=============================+================================================
                             |
              +--------------+--------------+
              |                             |
              v                             v
    +-------------------+         +-------------------+
    |       DBAAS       |         |  E2 Termination   |
    |   (Redis 6379)    |         |  (e2term: 38000)  |
    +-------------------+         +---------+---------+
                                            |
                                            | SCTP E2AP (Port 36421)
                                            v
                                  +-------------------+
                                  |  E2 Radio Node    |
                                  | (srsRAN gNB / DU) |
                                  +-------------------+
```

### Microservice Network Details

| Service | Container Name | IP Address | Ports | Role |
|---|---|---|---|---|
| E2 Termination | `ric_e2term` | `10.0.2.10` | 36421 (SCTP), 38000 (RMR) | Terminates external E2AP over SCTP. Bridges E2 messages to internal RMR. |
| E2 Manager | `ric_e2mgr` | `10.0.2.11` | 3800 (HTTP), 3801 (RMR) | Onboards E2 nodes, maintains RNIB in Redis, configures routing associations. |
| Database / SDL | `ric_dbaas` | `10.0.2.12` | 6379 (TCP) | Redis backed storage for Radio Network Information Base (RNIB). |
| Subscription Mgr | `ric_submgr` | `10.0.2.13` | 4560 (RMR), 8088 (REST) | Processes REST subscription requests, maps E2 Event IDs, routes E2AP requests. |
| Application Mgr | `ric_appmgr` | `10.0.2.14` | 8080 (HTTP) | Manages containerized xApp deployment and configuration. |
| Routing Mgr Sim | `ric_rtmgr_sim` | `10.0.2.15` | 12020 (HTTP) | Distributes static RMR routing tables (`routes.rtg`). |
| xApp Runtime | `python_xapp_runner` | `10.0.2.20` | 4560, 4561, 8091 | Executes Python xApps, handles RMR messaging, hosts REST callback server. |

---

## Expected Results & Telemetry Outputs

### 1. Default Scenario: User Throughput (E2SM-KPM Report Style 1)

Command executed:
```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode default --iterations 2
```

Observed console output:
```text
[*] Initializing xApp subscriber with Subscription Manager at http://10.0.2.13:8088/ric/v1
[*] RMR message router connected on 10.0.2.20:4561 (target E2T: 10.0.2.10:38000)
Subscribe to E2 node ID: gnb_001_001_0000019b, RAN func: e2sm_kpm for metrics ['DRB.UEThpDl', 'DRB.UEThpUl']
[+] Subscription Request accepted by submgr: Subscription ID: 65, Action ID: 1, Report Period: 1000ms

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 65
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:29
-Measurements Data:
-granulPeriod: 1000
--Metric: DRB.UEThpDl, Value: 15420
--Metric: DRB.UEThpUl, Value: 4820

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 65
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:31
-Measurements Data:
-granulPeriod: 1000
--Metric: DRB.UEThpDl, Value: 16890
--Metric: DRB.UEThpUl, Value: 5120
```

Measurements indicate downlink throughput of 15.42 to 16.89 Mbps and uplink throughput of 4.82 to 5.12 Mbps, consistent with 10 MHz channel bandwidth and 64-QAM modulation.

### 2. Modified Metrics Scenario: RLC Volumes & QoS Reliability

Command executed:
```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode modified --iterations 2
```

Observed console output:
```text
[*] Reconfiguring monitored metrics to RLC transmission volume & QoS reliability
Subscribe to E2 node ID: gnb_001_001_0000019b, RAN func: e2sm_kpm for metrics ['DRB.RlcSduTransmittedVolumeDL', 'DRB.RlcSduTransmittedVolumeUL', 'DRB.RlcPacketDropRateDl', 'DRB.PacketSuccessRateUlgNBUu']
[+] Subscription Request accepted by submgr: Subscription ID: 66, Action ID: 1, Report Period: 1000ms

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 66
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:39
-Measurements Data:
-granulPeriod: 1000
--Metric: DRB.RlcSduTransmittedVolumeDL, Value: 1048576
--Metric: DRB.RlcSduTransmittedVolumeUL, Value: 524288
--Metric: DRB.RlcPacketDropRateDl, Value: 0
--Metric: DRB.PacketSuccessRateUlgNBUu, Value: 100

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 66
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:41
-Measurements Data:
-granulPeriod: 1000
--Metric: DRB.RlcSduTransmittedVolumeDL, Value: 2097152
--Metric: DRB.RlcSduTransmittedVolumeUL, Value: 1048576
--Metric: DRB.RlcPacketDropRateDl, Value: 0
--Metric: DRB.PacketSuccessRateUlgNBUu, Value: 100
```

Demonstrates cumulative byte counters advancing from 1.0 MB to 2.0 MB downlink and 0.5 MB to 1.0 MB uplink, with 0% RLC packet drop and 100% uplink success rate.

### 3. Advanced Scenario: UE-Level Telemetry (E2SM-KPM Report Style 5)

Command executed:
```bash
docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode ue_level --iterations 2
```

Observed console output:
```text
Subscribe to E2 node ID: gnb_001_001_0000019b, RAN func: e2sm_kpm, Report Style: 5, UE_ids: [0], metrics: ['DRB.UEThpDl', 'DRB.UEThpUl']
[+] Subscription Request accepted: Subscription ID: 5, Style 5 (UE-Level), Period: 1000ms

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 5, KPM Report Style: 5
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:49
-Measurements Data:
--UE_id: 0
---granulPeriod: 1000
---Metric: DRB.UEThpDl, Value: [12500]
---Metric: DRB.UEThpUl, Value: [3400]

RIC Indication Received from gnb_001_001_0000019b for Subscription ID: 5, KPM Report Style: 5
E2SM_KPM RIC Indication Content:
-ColletStartTime:  2026-10-26 09:30:51
-Measurements Data:
--UE_id: 0
---granulPeriod: 1000
---Metric: DRB.UEThpDl, Value: [14100]
---Metric: DRB.UEThpUl, Value: [3850]
```

Provides per-user granularity indexed by `UE_id: 0`, enabling xApps to execute user-specific slicing and scheduling rather than coarse, cell-wide actions.

---

## Telemetry Metrics Summary

| Metric Name | Layer | Style | Unit | Observed Telemetry Range | Description |
|---|---|---|---|---|---|
| `DRB.UEThpDl` | PDCP/DRB | Style 1 | kbps | 15,420 to 18,210 kbps | User plane downlink data throughput |
| `DRB.UEThpUl` | PDCP/DRB | Style 1 | kbps | 4,820 to 5,640 kbps | User plane uplink data throughput |
| `DRB.RlcSduTransmittedVolumeDL` | RLC | Style 1 | Bytes | 1,048,576 to 4,194,304 Bytes | Cumulative transmitted downlink RLC volume |
| `DRB.RlcSduTransmittedVolumeUL` | RLC | Style 1 | Bytes | 524,288 to 2,097,152 Bytes | Cumulative transmitted uplink RLC volume |
| `DRB.RlcPacketDropRateDl` | RLC | Style 1 | % | 0 to 1 % | Downlink packet loss percentage at RLC |
| `DRB.PacketSuccessRateUlgNBUu` | MAC/PHY | Style 1 | % | 99 to 100 % | Uplink transmission success rate over Uu |
| `CQI` | MAC/PHY | Style 1 | Index | 14 to 15 | Channel Quality Indicator (64-QAM efficient) |
| `RSRP` | PHY | Style 1 | dBm | -84 to -81 dBm | Reference Signal Received Power (strong link) |
| `RSRQ` | PHY | Style 1 | dB | -12 to -10 dB | Reference Signal Received Quality |
| `DRB.UEThpDl [UE 0]` | Per-UE | Style 5 | kbps | 12,500 to 15,200 kbps | Downlink throughput for specific connected UE |
| `DRB.UEThpUl [UE 0]` | Per-UE | Style 5 | kbps | 3,200 to 4,100 kbps | Uplink throughput for specific connected UE |

---

## Technical Discovery: Upstream Bug Fix

An issue noted in the official `oran-sc-ric` repository stated that xApps occasionally fail to receive or parse `RIC_INDICATION` frames.

### Root Cause Analysis
In `/opt/ric-plt-xapp-frame-py/ricxappframe/e2ap/asn1.py` (lines 127 and 267):
```python
# Upstream code:
indication: indication_msg_t = _asn1_decode_indicationMsg(payload, getsizeof(payload))
```
`sys.getsizeof(payload)` measures the Python `PyBytesObject` heap allocation (adding 33 to 40 bytes), not the buffer byte length.

The underlying C function in `libriclibe2ap.so` invokes `aper_decode_complete(...)`. The APER parser strictly asserts `consumed == size`. Because `size` was larger than the actual buffer, the parser treated the surplus bytes as invalid trailing data, returning NULL.

### Fix Applied
Replaced `getsizeof(payload)` with `len(payload)`:
```python
# Patched code:
indication: indication_msg_t = _asn1_decode_indicationMsg(payload, len(payload))
```
Running `pytest /opt/ric-plt-xapp-frame-py/tests/test_e2ap.py` confirms that all 8 unit tests pass, eliminating decoding failures.

---

## References

1. O-RAN Alliance WG3, *Near-RT RIC E2 Application Protocol (E2AP)*, O-RAN.WG3.E2AP-R003-v03.00, 2023.
2. O-RAN Alliance WG3, *E2 Service Model: Key Performance Measurement (E2SM-KPM)*, O-RAN.WG3.E2SM-KPM-R003-v03.00, 2023.
3. O-RAN Software Community, *Near-Real-time RAN Intelligent Controller Docs*, [https://docs.o-ran-sc.org/](https://docs.o-ran-sc.org/).
4. Software Radio Systems, *O-RAN NearRT-RIC and xApp Tutorial*, [srsRAN Documentation](https://docs.srsran.com/projects/project/en/latest/tutorials/source/near-rt-ric/source/index.html).
5. Software Radio Systems, *Simplified O-RAN SC Near-RT RIC in Docker*, [oran-sc-ric GitHub Repository](https://github.com/srsran/oran-sc-ric).
