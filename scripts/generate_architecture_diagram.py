"""
==============================================================================
RetailPulse: Architecture Diagram Generator
Script: scripts/generate_architecture_diagram.py

Generates a publication-quality diagram of the end-to-end data pipeline:
  PostgreSQL -> Airbyte -> BigQuery Raw -> dbt Core -> BigQuery Analytics
  Orchestrated by Apache Airflow -> Consumed by Streamlit Conversational BI
Output: docs/architecture.png
==============================================================================
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "architecture.png"

def draw_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    # Background canvas
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    # Header Title
    ax.text(8.0, 8.5, "RetailPulse: Automated Retail Sales Analytics & Conversational BI Pipeline",
            fontsize=18, fontweight="bold", ha="center", va="center", color="#0F172A")
    ax.text(8.0, 8.1, "End-to-End Modern Data Engineering Architecture | Experiment 9 Microproject",
            fontsize=11, ha="center", va="center", color="#475569")

    # Section 1: Member 1 Box (Top Layer - Data Engineering & Warehousing)
    m1_box = patches.FancyBboxPatch((0.5, 3.8), 15.0, 3.9, boxstyle="round,pad=0.2,rounding_size=0.3",
                                    edgecolor="#3B82F6", facecolor="#EFF6FF", linewidth=1.5, linestyle="--")
    ax.add_patch(m1_box)
    ax.text(0.8, 7.4, "MEMBER 1: DATA ENGINEERING & WAREHOUSING", fontsize=11, fontweight="bold", color="#1D4ED8")

    # 1. Source CSV
    csv_box = patches.FancyBboxPatch((1.0, 4.2), 2.2, 2.7, boxstyle="round,pad=0.1,rounding_size=0.2",
                                    edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(csv_box)
    ax.text(2.1, 6.4, "Source CSV", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(2.1, 5.8, "retail_sales.csv\n• 500 orders\n• ₹17.38M Revenue\n• 12 months data", fontsize=8.5, ha="center", color="#475569")
    ax.text(2.1, 4.6, "[Deterministic]", fontsize=8, ha="center", color="#059669", style="italic")

    # Arrow 1
    ax.annotate("", xy=(3.8, 5.55), xytext=(3.3, 5.55),
                arrowprops=dict(arrowstyle="->", color="#3B82F6", lw=2))
    ax.text(3.55, 5.8, "load_postgres.py", fontsize=7.5, ha="center", color="#3B82F6")

    # 2. PostgreSQL
    pg_box = patches.FancyBboxPatch((3.9, 4.2), 2.3, 2.7, boxstyle="round,pad=0.1,rounding_size=0.2",
                                   edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(pg_box)
    ax.text(5.05, 6.4, "PostgreSQL", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(5.05, 5.75, "Database: retail_source\nTable: public.orders\n• PK: order_id\n• qty > 0, price > 0\n• 500 rows verified", fontsize=8.5, ha="center", color="#475569")
    ax.text(5.05, 4.6, "[OLTP Source]", fontsize=8, ha="center", color="#0284C7", style="italic")

    # Arrow 2 (Airbyte)
    ax.annotate("", xy=(6.9, 5.55), xytext=(6.3, 5.55),
                arrowprops=dict(arrowstyle="->", color="#3B82F6", lw=2))
    ax.text(6.6, 5.9, "Airbyte OSS\n(abctl)", fontsize=8, fontweight="bold", ha="center", color="#2563EB")
    ax.text(6.6, 5.2, "Full Refresh\nOverwrite", fontsize=7, ha="center", color="#64748B")

    # 3. BigQuery Raw
    bqr_box = patches.FancyBboxPatch((7.0, 4.2), 2.3, 2.7, boxstyle="round,pad=0.1,rounding_size=0.2",
                                    edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(bqr_box)
    ax.text(8.15, 6.4, "BigQuery (Raw)", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(8.15, 5.75, "Dataset: raw_retail\nTable: orders\n• Raw ingestion\n• _airbyte_raw_id\n• _airbyte_extracted_at", fontsize=8.5, ha="center", color="#475569")
    ax.text(8.15, 4.6, "[Cloud Warehouse]", fontsize=8, ha="center", color="#D97706", style="italic")

    # Arrow 3 (dbt)
    ax.annotate("", xy=(10.0, 5.55), xytext=(9.4, 5.55),
                arrowprops=dict(arrowstyle="->", color="#3B82F6", lw=2))
    ax.text(9.7, 5.9, "dbt Core\n(dbt-bigquery)", fontsize=8, fontweight="bold", ha="center", color="#EA580C")
    ax.text(9.7, 5.2, "dbt run\ndbt test", fontsize=7, ha="center", color="#64748B")

    # 4. BigQuery Analytics Layer
    bqa_box = patches.FancyBboxPatch((10.1, 4.2), 5.0, 2.7, boxstyle="round,pad=0.1,rounding_size=0.2",
                                    edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(bqa_box)
    ax.text(12.6, 6.4, "BigQuery (Analytics Layer)", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(12.6, 5.65, "Dataset: analytics_retail\n• stg_orders (deduplicated staging view)\n• sales_by_product (7 products, revenue & qty mart)\n• sales_by_region (5 territories mart)\n• monthly_sales (12-month time series mart)\n• 32 automated schema & data quality tests", fontsize=8.5, ha="center", color="#475569")
    ax.text(12.6, 4.6, "[Checksum: ₹17,379,476.00 INR Parity Passed]", fontsize=8, ha="center", color="#059669", fontweight="bold")

    # Section 2: Member 2 Box (Bottom Layer - Orchestration & BI)
    m2_box = patches.FancyBboxPatch((0.5, 0.4), 15.0, 3.1, boxstyle="round,pad=0.2,rounding_size=0.3",
                                    edgecolor="#10B981", facecolor="#F0FDF4", linewidth=1.5, linestyle="--")
    ax.add_patch(m2_box)
    ax.text(0.8, 3.2, "MEMBER 2: ORCHESTRATION & CONVERSATIONAL BUSINESS INTELLIGENCE", fontsize=11, fontweight="bold", color="#047857")

    # 5. Apache Airflow DAG Box
    airflow_box = patches.FancyBboxPatch((1.0, 0.7), 7.0, 2.2, boxstyle="round,pad=0.1,rounding_size=0.2",
                                        edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(airflow_box)
    ax.text(4.5, 2.5, "Apache Airflow DAG: retail_sales_pipeline", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(4.5, 1.8, "start ➔ [trigger_airbyte | manual_notice] ➔ validate_raw ➔ dbt_run ➔ dbt_test ➔ validate_output ➔ end\n"
                      "• Coordinates task execution order & enforces dependencies\n"
                      "• Validates raw record counts & cross-mart checksums\n"
                      "• Dual-mode: REST API Airbyte sync + Simplified manual mode", fontsize=8, ha="center", color="#475569")
    ax.text(4.5, 0.95, "[Docker Compose / LocalExecutor]", fontsize=8, ha="center", color="#0284C7", style="italic")

    # 6. Streamlit Conversational BI Box
    st_box = patches.FancyBboxPatch((8.7, 0.7), 6.4, 2.2, boxstyle="round,pad=0.1,rounding_size=0.2",
                                   edgecolor="#94A3B8", facecolor="#FFFFFF", linewidth=1.2)
    ax.add_patch(st_box)
    ax.text(11.9, 2.5, "Streamlit Conversational BI (app/streamlit_app.py)", fontsize=11, fontweight="bold", ha="center", color="#1E293B")
    ax.text(11.9, 1.8, "• Predefined SQL mapping for 3 core business questions (Q1, Q2, Q3)\n"
                      "• Natural Language conversational intent matching (Zero SQL injection)\n"
                      "• Interactive Plotly charts (Product bar, Regional map, Monthly trend)\n"
                      "• Live BigQuery connection + offline local replica fallback engine", fontsize=8, ha="center", color="#475569")
    ax.text(11.9, 0.95, "[Conversational BI Interface]", fontsize=8, ha="center", color="#059669", style="italic")

    # Connection: BigQuery Analytics -> Streamlit BI
    ax.annotate("", xy=(12.6, 2.95), xytext=(12.6, 4.15),
                arrowprops=dict(arrowstyle="->", color="#10B981", lw=2.5, linestyle="-"))
    ax.text(12.95, 3.55, "Predefined SQL\nQueries", fontsize=8, fontweight="bold", ha="left", color="#047857")

    # Connection: Airflow -> Airbyte & dbt
    ax.annotate("", xy=(6.6, 4.2), xytext=(4.5, 2.95),
                arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5, linestyle=":"))
    ax.text(5.3, 3.5, "Triggers Sync", fontsize=7.5, color="#0284C7", rotation=30)

    ax.annotate("", xy=(9.7, 4.2), xytext=(6.5, 2.95),
                arrowprops=dict(arrowstyle="->", color="#EA580C", lw=1.5, linestyle=":"))
    ax.text(8.3, 3.5, "Executes dbt", fontsize=7.5, color="#EA580C", rotation=22)

    # Save diagram
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Architecture diagram saved successfully to: {OUTPUT_PATH}")

if __name__ == "__main__":
    draw_diagram()
