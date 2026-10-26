# SDN Assignment 3: O-RAN Near-RT RIC Architecture & xApp Telemetry

This project implements and evaluates the O-RAN Software Community (O-RAN SC) Near-Real-Time Radio Intelligent Controller (Near-RT RIC, `i-release`) and explores radio measurement subscriptions using containerized Python xApps.

## Student Information

- **Kamal Nayan Kumar** (23BDS026)
- **Altaf Raja** (23BCS011)
- **Ankit Kumar Keshari** (23BCS015)
- **Soumya Nimje** (23BEC054)
- **Instructor:** Dr. Jagadeesha R B
- **Course:** Software Defined Networking (CS304)

---

## Objectives

1. **Objective 1: Installation & Software Component Identification**
   - Deploy a minimal O-RAN SC Near-RT RIC multi-container platform in Docker without Kubernetes or Helm.
   - Inspect all containers, network namespaces, IP allocations, and process logs.
   - Analyze the roles of the E2 Manager (`e2mgr`), Subscription Manager (`submgr`), and xApp Framework (`ric-plt-xapp-frame-py`).
   - Examine the RIC Message Router (RMR) static routing table and the Shared Data Layer (SDL) database backed by Redis.

2. **Objective 2: xApp Radio Measurement Subscription**
   - Understand the E2 interface (E2AP) and the E2 Service Model for Key Performance Measurements (E2SM-KPM).
   - Execute the monitoring xApp inside `python_xapp_runner` to collect downlink and uplink throughput metrics (`DRB.UEThpDl`, `DRB.UEThpUl`).
   - Modify the requested metrics to collect layer-2 Radio Link Control (RLC) data volume and reliability parameters.
   - Compare Node-level reporting (Report Style 1) against User Equipment level reporting (Report Style 5).

---

## Repository Structure

```
.
├── oran-sc-ric/               # O-RAN SC Near-RT RIC multi-docker setup
│   ├── docker-compose.yml     # Compose recipe for 7 microservices
│   ├── .env                   # Image versions, subnet, and port definitions
│   ├── ric/
│   │   ├── configs/           # Configuration files (routes.rtg, e2mgr.yaml, submgr.yaml)
│   │   └── images/            # Local Dockerfiles (rtmgr_sim, python_xapp_runner)
│   └── xApps/python/          # Python xApps and libraries
│       ├── simple_mon_xapp.py # Basic E2SM-KPM Style 1 monitoring xApp
│       ├── kpm_mon_xapp.py    # Multi-style (Styles 1-5) KPM monitoring xApp
│       ├── run_telemetry_demo.py # Live telemetry driver and scenario runner
│       └── lib/               # Shared xAppBase and ASN.1 packager modules
├── report/                    # Full technical LaTeX report and figures
│   ├── report.tex             # LaTeX source code
│   ├── report.pdf             # Compiled final report (15 pages)
│   ├── build.sh               # Compilation script (supports pdflatex and tectonic)
│   ├── capture.sh             # Terminal screenshot capture pipeline
│   ├── render_term.py         # Terminal snapshot renderer (macOS Menlo style)
│   ├── logo.jpeg              # Institute letterhead logo
│   └── figs/                  # High-resolution terminal capture PNGs
├── scripts/                   # Helper automation scripts
│   ├── run_all.sh             # Top-level runner executing RIC, captures, and report
│   └── run_ric.sh             # Starts and verifies all RIC containers
├── make_submission.sh         # Bundles submission zip archive
└── README.md                  # Project documentation
```

---

## Near-RT RIC Microservices & Topology

All microservices run on a dedicated Docker bridge network (`oran-sc-ric_ric_network`) on subnet `10.0.2.0/24`:

| Container | Service Role | IP Address | Ports | Communication Protocols |
|---|---|---|---|---|
| `ric_e2term` | E2 Termination | 10.0.2.10 | 36421 (SCTP), 38000 (RMR) | E2AP over SCTP, internal RMR |
| `ric_e2mgr` | E2 Manager | 10.0.2.11 | 3800 (HTTP), 3801 (RMR) | RNIB sync, RMR control |
| `ric_dbaas` | Redis Database / SDL | 10.0.2.12 | 6379 (TCP) | Shared Data Layer storage |
| `ric_submgr` | Subscription Manager | 10.0.2.13 | 4560 (RMR), 8088 (REST) | HTTP subscription API, RMR |
| `ric_appmgr` | xApp Application Manager | 10.0.2.14 | 8080 (HTTP) | xApp lifecycle management |
| `ric_rtmgr_sim` | Routing Manager Simulator | 10.0.2.15 | 12020 (HTTP) | Static RMR route distribution |
| `python_xapp_runner` | xApp Execution Container | 10.0.2.20 | 4560, 4561, 8091 | RMR client, REST callback server |

---

## Core Component Responsibilities

### 1. E2 Manager (`e2mgr`)
- Receives `RIC_E2_SETUP_REQ` (message type 12001) forwarded by `e2term` over RMR when an E2 node connects.
- Unpacks the Global gNB ID, PLMN ID, and supported RAN function definitions.
- Records the active node in the Radio Network Information Base (RNIB) in Redis (`dbaas`).
- Associates the RAN node with the active E2 Termination endpoint via the Routing Manager.
- Returns `RIC_E2_SETUP_RESP` (message type 12002) to complete node onboarding.

### 2. Subscription Manager (`submgr`)
- Exposes an HTTP REST API at `http://10.0.2.13:8088/ric/v1/subscriptions` where xApps post subscription requests.
- Maps xApp-specific subscription identifiers to downstream `E2EventInstanceId` parameters.
- Encapsulates Event Trigger and Action Definitions into an ASN.1 encoded `RICsubscriptionRequest` (RMR message type 12010) routed to `e2term`.
- Enforces retransmission and timeout policies if the radio node fails to reply within `e2tSubReqTimeout_ms` (2000 ms).
- Dispatches HTTP callbacks to the xApp's embedded web server upon admission.

### 3. xApp Python Framework (`ric-plt-xapp-frame-py`)
- Provides Ctypes bindings to `librmr_si.so` for low-latency peer-to-peer message routing.
- Implements `ThreadedHTTPServer` to receive subscription responses and lifecycle notifications asynchronously.
- Bundles ASN.1 encoders and decoders for E2AP and E2SM service models (KPM, RC, CCC).

---

## Quick Start & Execution

### 1. Start the Near-RT RIC Multi-Container Platform
```bash
./scripts/run_ric.sh
```
Verify that all 7 containers are running:
```bash
docker ps
```

### 2. Run the Monitoring xApp Scenarios
To run the automated telemetry demonstration inside `python_xapp_runner`:

- **Default Scenario (Node-Level Throughput):**
  ```bash
  docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode default --iterations 3
  ```

- **Modified Metrics Scenario (RLC Volume & Packet Reliability):**
  ```bash
  docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode modified --iterations 3
  ```

- **Radio Channel Metrics Scenario (CQI, RSRP, RSRQ):**
  ```bash
  docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode channel --iterations 3
  ```

- **UE-Level Telemetry Scenario (E2SM-KPM Report Style 5):**
  ```bash
  docker exec python_xapp_runner python3 /opt/xApps/run_telemetry_demo.py --mode ue_level --iterations 3
  ```

### 3. Capture Screenshots
```bash
./report/capture.sh
```
This generates styled terminal PNG snapshots in `report/figs/`.

### 4. Compile the PDF Report
The LaTeX build script automatically uses `tectonic` or `pdflatex`:
```bash
./report/build.sh
```
The compiled 15-page document will be written to `report/report.pdf`.

### 5. Package Submission Archive
```bash
./make_submission.sh
```
Generates `sdn_assignment3_submission.zip` with `report.pdf` at the root and all source code and evidence in `code/`.

---

## Technical Discovery: Upstream Bug Fix

During investigation of the xApp Python framework (`ric-plt-xapp-frame-py`), an upstream bug in `ricxappframe/e2ap/asn1.py` was identified.

In lines 127 and 267 of `asn1.py`:
```python
# Upstream defective code:
indication: indication_msg_t = _asn1_decode_indicationMsg(payload, getsizeof(payload))
```
`sys.getsizeof(payload)` returns the memory allocation of the Python `PyBytesObject` wrapper, adding 33 to 40 bytes of overhead above the actual raw buffer length.

When passed to the C parser `aper_decode_complete(...)` in `libriclibe2ap.so`, the decoder expects `consumed == size`. Because `size` exceeded the true payload length, the parser treated the difference as invalid trailing octets, failing with a NULL pointer error.

**Fix Applied:**
```python
# Corrected code:
indication: indication_msg_t = _asn1_decode_indicationMsg(payload, len(payload))
```
The unit test suite in `tests/test_e2ap.py` passes 8/8 tests after the fix, restoring deterministic decoding of incoming `RIC_INDICATION` telemetry frames.
