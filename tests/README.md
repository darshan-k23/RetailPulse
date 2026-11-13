# Pipeline Tests & Quality Validation

This directory contains standalone Python validation scripts used to audit and reconcile data across stages of the pipeline:

1. **Reconciliation Check**:
   - Compare row counts in PostgreSQL (`retail_source.public.orders`) vs BigQuery (`raw_retail.orders`).
2. **Schema & Null Verification**:
   - Verify non-null constraints on primary keys and essential transaction attributes.
3. **Data Integrity & Consistency Check**:
   - Validate that `total_amount = (quantity * unit_price) - discount_amount`.
   - Check that date ranges match expected bounds.

