"""
==============================================================================
RetailPulse: Member 2 Test Suite (Airflow DAG & Conversational BI)
File: tests/test_member2_bi.py

Tests:
  1. Airflow DAG integrity & task dependency structure
  2. WarehouseService query accuracy against dbt analytical models
  3. Predefined SQL queries for the 3 core business questions
  4. Conversational natural language query intent parsing
==============================================================================
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.streamlit_app import WarehouseService, parse_conversational_query, QUERY_CATALOG


class TestMember2Components(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.warehouse = WarehouseService()

    def test_q1_highest_revenue_product(self):
        """Tests Q1: Which product generated the highest revenue?"""
        q_meta = QUERY_CATALOG["highest_revenue_product"]
        df, latency = self.warehouse.run_query(q_meta["sql"], q_meta["model"])
        
        self.assertFalse(df.empty, "Q1 returned an empty dataframe")
        top_product = df.iloc[0]["product"]
        top_revenue = float(df.iloc[0]["total_revenue"])
        
        # Ground truth from Member 1's dataset: Laptop is top product with 6,890,000 INR
        self.assertEqual(top_product, "Laptop")
        self.assertEqual(top_revenue, 6890000.0)

    def test_q2_highest_sales_region(self):
        """Tests Q2: Which region recorded the highest sales?"""
        q_meta = QUERY_CATALOG["highest_sales_region"]
        df, latency = self.warehouse.run_query(q_meta["sql"], q_meta["model"])
        
        self.assertFalse(df.empty, "Q2 returned an empty dataframe")
        top_region = df.iloc[0]["region"]
        top_revenue = float(df.iloc[0]["total_revenue"])
        
        # Ground truth: South territory leads with 4,823,494 INR
        self.assertEqual(top_region, "South")
        self.assertEqual(top_revenue, 4823494.0)

    def test_q3_monthly_sales_trend(self):
        """Tests Q3: How does revenue change month by month?"""
        q_meta = QUERY_CATALOG["monthly_revenue_trend"]
        df, latency = self.warehouse.run_query(q_meta["sql"], q_meta["model"])
        
        self.assertFalse(df.empty, "Q3 returned an empty dataframe")
        # Exactly 12 months in time span
        self.assertEqual(len(df), 12, "Monthly sales mart must contain exactly 12 months")
        
        # Total revenue across all months must equal total gross revenue (17,379,476 INR)
        total_monthly_rev = round(float(df["total_revenue"].sum()), 2)
        self.assertEqual(total_monthly_rev, 17379476.0)

    def test_conversational_intent_parser(self):
        """Tests natural language intent routing."""
        # Q1 variants
        self.assertEqual(parse_conversational_query("Which product generated the highest revenue?")[0], "highest_revenue_product")
        self.assertEqual(parse_conversational_query("What is the top product by sales?")[0], "highest_revenue_product")
        self.assertEqual(parse_conversational_query("best selling product")[0], "highest_revenue_product")

        # Q2 variants
        self.assertEqual(parse_conversational_query("Which region recorded the highest sales?")[0], "highest_sales_region")
        self.assertEqual(parse_conversational_query("top sales region")[0], "highest_sales_region")
        self.assertEqual(parse_conversational_query("regional sales")[0], "highest_sales_region")

        # Q3 variants
        self.assertEqual(parse_conversational_query("How does revenue change month by month?")[0], "monthly_revenue_trend")
        self.assertEqual(parse_conversational_query("Show monthly revenue trend")[0], "monthly_revenue_trend")

        # Dynamic filters
        intent, flt = parse_conversational_query("Show all laptop transactions in south region")
        self.assertEqual(intent, "filtered_orders")
        self.assertEqual(flt.get("product"), "Laptop")
        self.assertEqual(flt.get("region"), "South")

    def test_dag_file_structure(self):
        """Verifies that the Airflow DAG file is parseable and contains required tasks."""
        dag_path = PROJECT_ROOT / "airflow" / "dags" / "retail_sales_pipeline.py"
        self.assertTrue(dag_path.is_file(), "DAG file missing at airflow/dags/retail_sales_pipeline.py")
        
        content = dag_path.read_text(encoding="utf-8")
        required_tasks = [
            "start",
            "check_airbyte_sync_mode",
            "trigger_airbyte_sync",
            "validate_raw_ingestion",
            "dbt_run",
            "dbt_test",
            "validate_bigquery_output",
            "end",
        ]
        for task in required_tasks:
            self.assertIn(task, content, f"Task '{task}' missing from retail_sales_pipeline.py")


if __name__ == "__main__":
    unittest.main()
