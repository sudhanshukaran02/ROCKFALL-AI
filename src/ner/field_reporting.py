import os
import sys
import uuid
from datetime import datetime
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.ner.config import Config


# ---------------------------------------------------------
# FIELD REPORTING LOCAL DATABASE MODULE
# ---------------------------------------------------------
FIELD_REPORTS_DIR = os.path.join(Config.BASE_DIR, "data", "field_reports")
FIELD_REPORTS_CSV = os.path.join(FIELD_REPORTS_DIR, "field_reports.csv")

DEFAULT_COLUMNS = [
    "report_id", "timestamp", "latitude", "longitude",
    "incident_type", "severity", "description", "photo_path",
    "reporter_name", "infrastructure_affected", "road_blocked",
    "status", "reviewer_notes", "verified_at"
]


def init_field_report_db():
    os.makedirs(FIELD_REPORTS_DIR, exist_ok=True)
    if not os.path.exists(FIELD_REPORTS_CSV):
        df_empty = pd.DataFrame(columns=DEFAULT_COLUMNS)
        df_empty.to_csv(FIELD_REPORTS_CSV, index=False)
        print(f"[FieldReporting] Initialized database at {FIELD_REPORTS_CSV}", flush=True)


def submit_field_report(
    latitude,
    longitude,
    incident_type,
    severity,
    description,
    photo_path="None",
    reporter_name="Citizen / Field Engineer",
    infrastructure_affected="Road / Slope Transit",
    road_blocked=False,
):
    """
    Submits a prototype field report and stores it locally in data/field_reports/field_reports.csv
    """
    init_field_report_db()

    report_id = f"REP-{str(uuid.uuid4())[:8].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_report = {
        "report_id": report_id,
        "timestamp": timestamp,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "incident_type": str(incident_type),
        "severity": str(severity),
        "description": str(description),
        "photo_path": str(photo_path),
        "reporter_name": str(reporter_name),
        "infrastructure_affected": str(infrastructure_affected),
        "road_blocked": bool(road_blocked),
        "status": "PENDING_VERIFICATION",
        "reviewer_notes": "",
        "verified_at": "",
    }

    df = pd.read_csv(FIELD_REPORTS_CSV)
    # Ensure all columns exist
    for col in DEFAULT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = pd.concat([df, pd.DataFrame([new_report])], ignore_index=True)
    df.to_csv(FIELD_REPORTS_CSV, index=False)

    print(f"[FieldReporting] Submitted Report ID: {report_id} at ({latitude}, {longitude})", flush=True)
    return new_report


def get_all_field_reports():
    """
    Reads and returns all submitted field reports from local CSV storage.
    """
    init_field_report_db()
    try:
        df = pd.read_csv(FIELD_REPORTS_CSV)
        # Ensure all columns exist
        for col in DEFAULT_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df.fillna("")
        return df
    except Exception as e:
        print(f"[FieldReporting ERROR] Failed to load field reports: {e}", flush=True)
        return pd.DataFrame(columns=DEFAULT_COLUMNS)


def get_field_report_by_id(report_id: str):
    """
    Retrieves a single field report by its ID.
    """
    df = get_all_field_reports()
    matched = df[df["report_id"] == report_id]
    if matched.empty:
        return None
    d = matched.iloc[0].to_dict()
    # Sanitize dictionary values
    for k, v in d.items():
        if pd.isna(v):
            d[k] = ""
    return d


def update_field_report_verification(report_id: str, new_status: str, reviewer_notes: str = ""):
    """
    Updates the verification status and reviewer notes of a field report.
    """
    init_field_report_db()
    df = pd.read_csv(FIELD_REPORTS_CSV)
    for col in DEFAULT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df.fillna("")
    idx_match = df.index[df["report_id"] == report_id].tolist()
    if not idx_match:
        return None

    idx = idx_match[0]
    df.at[idx, "status"] = new_status
    df.at[idx, "reviewer_notes"] = reviewer_notes
    df.at[idx, "verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_csv(FIELD_REPORTS_CSV, index=False)
    print(f"[FieldReporting] Updated Report {report_id} -> {new_status}", flush=True)
    d = df.iloc[idx].to_dict()
    for k, v in d.items():
        if pd.isna(v):
            d[k] = ""
    return d

