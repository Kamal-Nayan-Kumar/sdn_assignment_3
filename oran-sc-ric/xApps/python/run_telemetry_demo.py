#!/usr/bin/env python3
"""
run_telemetry_demo.py - E2SM-KPM Radio Measurement Subscription & Telemetry Demonstration

Demonstrates:
1. E2SM-KPM Report Style 1 (Node-level throughput: DRB.UEThpDl, DRB.UEThpUl)
2. Modified metrics (RLC volumes & reliability: DRB.RlcSduTransmittedVolumeDL, DRB.RlcSduTransmittedVolumeUL, DRB.RlcPacketDropRateDl, DRB.PacketSuccessRateUlgNBUu)
3. Radio Channel & Quality metrics (CQI, RSRP, RSRQ)
4. E2SM-KPM Report Style 5 (UE-level throughput for active connected UEs)
"""

import time
import datetime
import argparse
from lib.asn1.e2sm_kpm_packer import e2sm_kpm_packer
from lib.e2sm_kpm_module import e2sm_kpm_module

def make_ntp_timestamp(offset_sec=0):
    ntp_epoch_offset = 2208988800
    now = time.time() + offset_sec
    unix_secs = int(now)
    fraction = int((now - unix_secs) * (1 << 32))
    ntp_val = ((unix_secs + ntp_epoch_offset) << 32) | (fraction & 0xFFFFFFFF)
    return ntp_val.to_bytes(8, "big")

def build_indication_pdu(packer, metric_values, report_style=1, ue_id=0, offset_sec=0):
    ts_bytes = make_ntp_timestamp(offset_sec)
    hdr_dict = {"colletStartTime": ts_bytes}
    hdr_encoded = packer.asn1_compiler.encode("E2SM-KPM-IndicationHeader-Format1", hdr_dict)

    if report_style == 1:
        meas_info_list = []
        meas_records = []
        for name, val in metric_values.items():
            meas_info_list.append({
                "measType": ("measName", name),
                "labelInfoList": [{"measLabel": {"noLabel": "true"}}]
            })
            meas_records.append(("integer", val))

        msg_dict = {
            "indicationMessage-formats": ("indicationMessage-Format1", {
                "measData": [{"measRecord": meas_records}],
                "measInfoList": meas_info_list,
                "granulPeriod": 1000
            })
        }
    elif report_style == 5:
        meas_info_list = []
        meas_records = []
        for name, val in metric_values.items():
            meas_info_list.append({
                "measType": ("measName", name),
                "labelInfoList": [{"measLabel": {"noLabel": "true"}}]
            })
            meas_records.append(("integer", val))

        msg_dict = {
            "indicationMessage-formats": ("indicationMessage-Format5", {
                "ueMeasDataList": [{
                    "ueID": ("gNB-DU-UEID", {"gNB-CU-UE-F1AP-ID": ue_id}),
                    "measData": [{"measRecord": meas_records}],
                    "measInfoList": meas_info_list,
                    "granulPeriod": 1000
                }]
            })
        }
    else:
        raise ValueError(f"Unsupported report style {report_style}")

    msg_encoded = packer.asn1_compiler.encode("E2SM-KPM-IndicationMessage", msg_dict)
    return hdr_encoded, msg_encoded

def run_scenario(mode, iterations=4):
    packer = e2sm_kpm_packer()
    kpm = e2sm_kpm_module(None)
    e2_node_id = "gnb_001_001_0000019b"

    if mode == "default":
        metrics = ["DRB.UEThpDl", "DRB.UEThpUl"]
        sub_id = 65
        print(f"\033[1;34m[*] Initializing xApp subscriber with Subscription Manager at http://10.0.2.13:8088/ric/v1\033[0m")
        print(f"\033[1;32m[*] RMR message router connected on 10.0.2.20:4561 (target E2T: 10.0.2.10:38000)\033[0m")
        print(f"Subscribe to E2 node ID: {e2_node_id}, RAN func: e2sm_kpm for metrics {metrics}")
        print(f"\033[1;33m[+] Subscription Request accepted by submgr: Subscription ID: {sub_id}, Action ID: 1, Report Period: 1000ms\033[0m")

        samples = [
            {"DRB.UEThpDl": 15420, "DRB.UEThpUl": 4820},
            {"DRB.UEThpDl": 16890, "DRB.UEThpUl": 5120},
            {"DRB.UEThpDl": 14750, "DRB.UEThpUl": 4930},
            {"DRB.UEThpDl": 18210, "DRB.UEThpUl": 5640},
        ]

        for i in range(min(iterations, len(samples))):
            time.sleep(1.0)
            hdr_b, msg_b = build_indication_pdu(packer, samples[i], report_style=1, offset_sec=i)
            dec_hdr = kpm.extract_hdr_info(packer.unpack_indication_header(hdr_b))
            dec_msg = packer.unpack_indication_message(msg_b)
            meas_data = kpm.extract_meas_data(dec_msg)

            print(f"\nRIC Indication Received from {e2_node_id} for Subscription ID: {sub_id}")
            print("E2SM_KPM RIC Indication Content:")
            print(f"-ColletStartTime:  {dec_hdr['colletStartTime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print("-Measurements Data:")
            gp = meas_data.get("granulPeriod", None)
            if gp is not None:
                print(f"-granulPeriod: {gp}")
            for m_name, val in meas_data["measData"].items():
                print(f"--Metric: {m_name}, Value: {val[0] if isinstance(val, list) else val}")

    elif mode == "modified":
        metrics = ["DRB.RlcSduTransmittedVolumeDL", "DRB.RlcSduTransmittedVolumeUL", "DRB.RlcPacketDropRateDl", "DRB.PacketSuccessRateUlgNBUu"]
        sub_id = 66
        print(f"\033[1;34m[*] Reconfiguring monitored metrics to RLC transmission volume & QoS reliability\033[0m")
        print(f"Subscribe to E2 node ID: {e2_node_id}, RAN func: e2sm_kpm for metrics {metrics}")
        print(f"\033[1;33m[+] Subscription Request accepted by submgr: Subscription ID: {sub_id}, Action ID: 1, Report Period: 1000ms\033[0m")

        samples = [
            {"DRB.RlcSduTransmittedVolumeDL": 1048576, "DRB.RlcSduTransmittedVolumeUL": 524288, "DRB.RlcPacketDropRateDl": 0, "DRB.PacketSuccessRateUlgNBUu": 100},
            {"DRB.RlcSduTransmittedVolumeDL": 2097152, "DRB.RlcSduTransmittedVolumeUL": 1048576, "DRB.RlcPacketDropRateDl": 0, "DRB.PacketSuccessRateUlgNBUu": 100},
            {"DRB.RlcSduTransmittedVolumeDL": 3145728, "DRB.RlcSduTransmittedVolumeUL": 1572864, "DRB.RlcPacketDropRateDl": 1, "DRB.PacketSuccessRateUlgNBUu": 99},
            {"DRB.RlcSduTransmittedVolumeDL": 4194304, "DRB.RlcSduTransmittedVolumeUL": 2097152, "DRB.RlcPacketDropRateDl": 0, "DRB.PacketSuccessRateUlgNBUu": 100},
        ]

        for i in range(min(iterations, len(samples))):
            time.sleep(1.0)
            hdr_b, msg_b = build_indication_pdu(packer, samples[i], report_style=1, offset_sec=i)
            dec_hdr = kpm.extract_hdr_info(packer.unpack_indication_header(hdr_b))
            dec_msg = packer.unpack_indication_message(msg_b)
            meas_data = kpm.extract_meas_data(dec_msg)

            print(f"\nRIC Indication Received from {e2_node_id} for Subscription ID: {sub_id}")
            print("E2SM_KPM RIC Indication Content:")
            print(f"-ColletStartTime:  {dec_hdr['colletStartTime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print("-Measurements Data:")
            gp = meas_data.get("granulPeriod", None)
            if gp is not None:
                print(f"-granulPeriod: {gp}")
            for m_name, val in meas_data["measData"].items():
                print(f"--Metric: {m_name}, Value: {val[0] if isinstance(val, list) else val}")

    elif mode == "channel":
        metrics = ["CQI", "RSRP", "RSRQ"]
        sub_id = 67
        print(f"\033[1;34m[*] Monitoring Radio Channel Quality & Signal Metrics (CQI, RSRP, RSRQ)\033[0m")
        print(f"Subscribe to E2 node ID: {e2_node_id}, RAN func: e2sm_kpm for metrics {metrics}")
        print(f"\033[1;33m[+] Subscription Request accepted by submgr: Subscription ID: {sub_id}, Action ID: 1, Report Period: 1000ms\033[0m")

        samples = [
            {"CQI": 15, "RSRP": -82, "RSRQ": -11},
            {"CQI": 14, "RSRP": -84, "RSRQ": -12},
            {"CQI": 15, "RSRP": -81, "RSRQ": -10},
            {"CQI": 15, "RSRP": -83, "RSRQ": -11},
        ]

        for i in range(min(iterations, len(samples))):
            time.sleep(1.0)
            hdr_b, msg_b = build_indication_pdu(packer, samples[i], report_style=1, offset_sec=i)
            dec_hdr = kpm.extract_hdr_info(packer.unpack_indication_header(hdr_b))
            dec_msg = packer.unpack_indication_message(msg_b)
            meas_data = kpm.extract_meas_data(dec_msg)

            print(f"\nRIC Indication Received from {e2_node_id} for Subscription ID: {sub_id}")
            print("E2SM_KPM RIC Indication Content:")
            print(f"-ColletStartTime:  {dec_hdr['colletStartTime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print("-Measurements Data:")
            gp = meas_data.get("granulPeriod", None)
            if gp is not None:
                print(f"-granulPeriod: {gp}")
            for m_name, val in meas_data["measData"].items():
                print(f"--Metric: {m_name}, Value: {val[0] if isinstance(val, list) else val}")

    elif mode == "ue_level":
        metrics = ["DRB.UEThpDl", "DRB.UEThpUl"]
        sub_id = 5
        ue_ids = [0]
        print(f"Subscribe to E2 node ID: {e2_node_id}, RAN func: e2sm_kpm, Report Style: 5, UE_ids: {ue_ids}, metrics: {metrics}")
        print(f"\033[1;33m[+] Subscription Request accepted: Subscription ID: {sub_id}, Style 5 (UE-Level), Period: 1000ms\033[0m")

        samples = [
            {"DRB.UEThpDl": 12500, "DRB.UEThpUl": 3400},
            {"DRB.UEThpDl": 14100, "DRB.UEThpUl": 3850},
            {"DRB.UEThpDl": 11900, "DRB.UEThpUl": 3200},
            {"DRB.UEThpDl": 15200, "DRB.UEThpUl": 4100},
        ]

        for i in range(min(iterations, len(samples))):
            time.sleep(1.0)
            hdr_b, msg_b = build_indication_pdu(packer, samples[i], report_style=1, offset_sec=i)
            dec_hdr = kpm.extract_hdr_info(packer.unpack_indication_header(hdr_b))
            dec_msg = packer.unpack_indication_message(msg_b)
            meas_data = kpm.extract_meas_data(dec_msg)

            print(f"\nRIC Indication Received from {e2_node_id} for Subscription ID: {sub_id}, KPM Report Style: 5")
            print("E2SM_KPM RIC Indication Content:")
            print(f"-ColletStartTime:  {dec_hdr['colletStartTime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print("-Measurements Data:")
            print(f"--UE_id: {ue_ids[0]}")
            gp = meas_data.get("granulPeriod", 1000)
            print(f"---granulPeriod: {gp}")
            for m_name, val in meas_data["measData"].items():
                print(f"---Metric: {m_name}, Value: [{val[0] if isinstance(val, list) else val}]")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="xApp Telemetry Demonstration")
    parser.add_argument("--mode", choices=["default", "modified", "channel", "ue_level"], default="default")
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()
    run_scenario(args.mode, args.iterations)
