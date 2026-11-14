FROM apache/airflow:2.8.3-python3.11

USER root
# Install system packages if necessary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       curl \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
# Install dbt-bigquery, BigQuery client and Airbyte provider in Airflow runtime
RUN pip install --no-cache-dir \
    dbt-core~=1.8.0 \
    dbt-bigquery~=1.8.0 \
    google-cloud-bigquery>=3.20.0 \
    apache-airflow-providers-airbyte>=3.7.0 \
    apache-airflow-providers-google>=10.15.0 \
    requests>=2.28.0
