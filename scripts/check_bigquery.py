"""
RetailPulse - Phase 3: BigQuery Connectivity & Dataset Health Check
Script: scripts/check_bigquery.py

Purpose:
    Safely tests local authentication with Google Cloud BigQuery using the
    service account JSON key and verifies that raw_retail and analytics_retail
    datasets exist in the specified project.

Safety:
    - Never hardcodes project IDs or credentials.
    - Reads from .env.
    - Performs read-only metadata checks ($0.00 cost).
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound, PermissionDenied
except ImportError:
    print("[ERROR] 'google-cloud-bigquery' library is not installed.", file=sys.stderr)
    print("Please run: pip install google-cloud-bigquery", file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_REGION = os.getenv("GCP_REGION", "US")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
REQUIRED_DATASETS = ["raw_retail", "analytics_retail"]


def validate_environment() -> Path:
    """Verifies that .env contains valid configuration before connecting."""
    if not GCP_PROJECT_ID or GCP_PROJECT_ID == "your_gcp_project_id_here":
        print("[ERROR] GCP_PROJECT_ID is not configured in .env.", file=sys.stderr)
        print("Please edit your .env file with your Google Cloud Project ID.", file=sys.stderr)
        sys.exit(1)

    if not CREDENTIALS_PATH:
        print("[ERROR] GOOGLE_APPLICATION_CREDENTIALS is not set in .env.", file=sys.stderr)
        sys.exit(1)

    # Resolve path relative to project root if relative
    key_path = Path(CREDENTIALS_PATH)
    if not key_path.is_absolute():
        key_path = PROJECT_ROOT / key_path

    if not key_path.is_file():
        print(f"[ERROR] Service account key file not found at: {key_path}", file=sys.stderr)
        print("Please place your downloaded GCP service account JSON key in the 'keys/' folder.", file=sys.stderr)
        sys.exit(1)

    return key_path


def test_bigquery_connection(key_file: Path):
    """Initializes BigQuery client and inspects datasets."""
    print("=" * 70)
    print(" RetailPulse - Phase 3: BigQuery Connectivity Check")
    print("=" * 70)
    print(f"Target GCP Project:   {GCP_PROJECT_ID}")
    print(f"Expected Region:      {GCP_REGION}")
    print(f"Key File Location:    {key_file}")
    print("-" * 70)

    try:
        # Initialize client with credentials file
        client = bigquery.Client.from_service_account_json(
            str(key_file),
            project=GCP_PROJECT_ID
        )

        print(f"[SUCCESS] Authenticated successfully with Google Cloud.")
        print(f"Service Account Email: {client.get_service_account_email()}")
        print("-" * 70)

        # Check for required datasets
        all_found = True
        for dataset_id in REQUIRED_DATASETS:
            full_dataset_ref = f"{GCP_PROJECT_ID}.{dataset_id}"
            try:
                dataset = client.get_dataset(full_dataset_ref)
                print(f"[FOUND] Dataset '{dataset_id}':")
                print(f"        - Location:    {dataset.location}")
                print(f"        - Created:     {dataset.created.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except NotFound:
                print(f"[MISSING] Dataset '{dataset_id}' does not exist in project '{GCP_PROJECT_ID}'!", file=sys.stderr)
                all_found = False
            except PermissionDenied as perm_err:
                print(f"[PERMISSION DENIED] Service account cannot access '{dataset_id}': {perm_err}", file=sys.stderr)
                all_found = False

        print("=" * 70)
        if all_found:
            print("CONNECTIVITY STATUS: SUCCESS - Datasets are accessible and ready.")
        else:
            print("CONNECTIVITY STATUS: ACTION NEEDED - Please create missing datasets or check permissions.")
            sys.exit(1)
        print("=" * 70)

    except Exception as err:
        print(f"\n[ERROR] BigQuery connection failed: {err}", file=sys.stderr)
        sys.exit(1)


def main():
    key_path = validate_environment()
    test_bigquery_connection(key_path)


if __name__ == "__main__":
    main()

