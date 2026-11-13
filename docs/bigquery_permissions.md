# RetailPulse: BigQuery IAM Permissions & Credential Security Guide

This document defines the **least-privilege IAM configuration** and **credential security standards** for Airbyte (ingestion) and dbt (transformation).

---

## 1. Golden Rules of Credential Security

> [!CAUTION]
> **NEVER COMMIT CREDENTIAL KEYS TO GIT**
> 1. Service account JSON keys contain private cryptographic keys that grant programmatic access to your Google Cloud project.
> 2. Committing a key file to GitHub or a public repository triggers automated scanner revocation or malicious resource hijacking.
> 3. Store keys exclusively in a local folder ignored by Git (e.g., `keys/gcp_service_account.json`).
> 4. Our [.gitignore](file:///c:/Users/Swapnaja/OneDrive/Desktop/RetailPulse/.gitignore) has been configured to strictly ignore `*.json`, `keys/`, `secrets/`, and `.env`.

---

## 2. Least-Privilege IAM Permission Matrix

In enterprise data engineering, tools are granted only the minimum permissions required to perform their specific tasks:

| Component | Project-Level Role | Dataset-Level Role: `raw_retail` | Dataset-Level Role: `analytics_retail` | Why This Role? |
| :--- | :--- | :--- | :--- | :--- |
| **Airbyte** (Ingestion) | `BigQuery Job User`<br>(`roles/bigquery.jobUser`) | `BigQuery Data Editor`<br>(`roles/bigquery.dataEditor`) | *No Access Needed* | Must execute load jobs and create/overwrite raw tables in `raw_retail`. Has no business reading or touching analytics models. |
| **dbt Core** (Transformation) | `BigQuery Job User`<br>(`roles/bigquery.jobUser`) | `BigQuery Data Viewer`<br>(`roles/bigquery.dataViewer`) | `BigQuery Data Editor`<br>(`roles/bigquery.dataEditor`) | Must run transformation queries, read raw data from `raw_retail`, and create/replace tables/views in `analytics_retail`. |

> [!TIP]
> For a 2-person college microproject, you can either create **two separate service accounts** (best practice) or **one unified pipeline service account** (`retailpulse-sa`) that combines the required roles:
> - Project Level: `BigQuery Job User`
> - Dataset `raw_retail`: `BigQuery Data Editor`
> - Dataset `analytics_retail`: `BigQuery Data Editor`

---

## 3. Step-by-Step: Creating the Pipeline Service Account in GCP Console

### Step 1: Open Service Accounts
1. In the [Google Cloud Console](https://console.cloud.google.com/), select your project.
2. In the top search bar, type `Service Accounts` and select **Service Accounts (IAM & Admin)**.
3. Click **+ Create Service Account** at the top of the page.

### Step 2: Service Account Details
- **Service account name:** `retailpulse-pipeline-sa`
- **Service account ID:** (auto-generated, e.g., `retailpulse-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`)
- **Description:** `Service account for RetailPulse Airbyte ingestion and dbt transformations`
- Click **Create and Continue**.

### Step 3: Grant Project-Level Role
- Click **Select a role** dropdown.
- Filter or search for `BigQuery Job User` (`roles/bigquery.jobUser`).
  *(This allows the service account to execute SQL queries and run load jobs in the project).*
- Click **Continue**.
- Click **Done** (Skip granting user access to this service account).

---

## 4. Step-by-Step: Generate & Secure the JSON Key

1. On the **Service Accounts** list page, click on the newly created service account email (`retailpulse-pipeline-sa@...`).
2. Navigate to the **Keys** tab (at the top).
3. Click **Add Key** &rarr; **Create new key**.
4. Select **JSON** as the key type.
5. Click **Create**.
6. The JSON private key will download to your local machine (typically `Downloads`).
7. **Safely place the key:**
   - Create a local directory in your project root called `keys` (already gitignored):
     ```powershell
     New-Item -ItemType Directory -Path "keys" -Force
     ```
   - Move the downloaded JSON file into `keys/` and rename it to `gcp_service_account.json`:
     ```powershell
     Move-Item -Path "$HOME\Downloads\YOUR_DOWNLOADED_KEY.json" -Destination "keys\gcp_service_account.json"
     ```

---

## 5. Step-by-Step: Scoping Dataset Permissions (Fine-Grained Security)

To ensure least privilege, grant dataset-specific access directly inside BigQuery Studio:

### Granting Access to `raw_retail`:
1. In **BigQuery Studio**, expand your project in the Explorer pane.
2. Click on the `raw_retail` dataset.
3. Click **Sharing** &rarr; **Permissions** (in the dataset details header).
4. Click **+ Add Principal**.
5. In **New principals**, paste the service account email:
   `retailpulse-pipeline-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`
6. In **Select a role**, choose **BigQuery** &rarr; **BigQuery Data Editor**.
7. Click **Save**.

### Granting Access to `analytics_retail`:
1. Click on the `analytics_retail` dataset.
2. Click **Sharing** &rarr; **Permissions**.
3. Click **+ Add Principal**.
4. In **New principals**, paste the same service account email.
5. In **Select a role**, choose **BigQuery** &rarr; **BigQuery Data Editor**.
6. Click **Save**.

---

## 6. Updating Local Environment (.env)

Once you obtain your Project ID and service account key:
Open your local `.env` and configure:

```ini
GCP_PROJECT_ID=your-actual-project-id
GCP_REGION=US
BIGQUERY_RAW_DATASET=raw_retail
BIGQUERY_ANALYTICS_DATASET=analytics_retail
GOOGLE_APPLICATION_CREDENTIALS=keys/gcp_service_account.json
```
*(Leave the placeholder in `.env.example`, only edit your private `.env` file).*

