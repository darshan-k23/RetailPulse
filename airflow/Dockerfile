FROM apache/airflow:2.8.3-python3.11

USER airflow

# Create an isolated virtual environment for dbt (PIP_USER=false overrides base image setting)
RUN python -m venv /home/airflow/dbt_venv \
    && PIP_USER=false /home/airflow/dbt_venv/bin/pip install --no-cache-dir \
       dbt-core~=1.8.0 \
       dbt-bigquery~=1.8.0 \
       google-cloud-bigquery>=3.20.0 \
       requests>=2.28.0 \
    && ln -sf /home/airflow/dbt_venv/bin/dbt /home/airflow/.local/bin/dbt
