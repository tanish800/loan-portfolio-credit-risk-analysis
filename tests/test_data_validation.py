"""
Unit tests for Data Validation Module.
Checks schema validation, duplicate detection, boundary enforcement, and reporting.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_validation import (
    validate_raw_schema,
    validate_id_uniqueness,
    validate_financial_boundaries,
    validate_categorical_domains
)

def test_validate_raw_schema():
    # Incomplete schema
    df_incomplete = pd.DataFrame({"id": ["1"], "loan_amnt": [5000]})
    res = validate_raw_schema(df_incomplete)
    assert res["is_valid"] is False
    assert len(res["missing_core_columns"]) > 0

def test_validate_id_uniqueness():
    df_unique = pd.DataFrame({"id": ["101", "102", "103"]})
    res_unique = validate_id_uniqueness(df_unique)
    assert res_unique["is_unique"] is True
    assert res_unique["duplicate_count"] == 0

    df_dup = pd.DataFrame({"id": ["101", "102", "101", "103"]})
    res_dup = validate_id_uniqueness(df_dup)
    assert res_dup["is_unique"] is False
    assert res_dup["duplicate_count"] == 1

def test_validate_financial_boundaries():
    df_valid = pd.DataFrame({
        "loan_amnt": [5000.0, 10000.0],
        "funded_amnt": [5000.0, 10000.0],
        "int_rate": [8.5, 14.2],
        "total_pymnt": [1000.0, 2000.0],
        "out_prncp": [4000.0, 8000.0],
        "annual_inc": [60000.0, 85000.0]
    })
    res_valid = validate_financial_boundaries(df_valid)
    assert res_valid["all_boundaries_valid"] is True

    df_invalid = pd.DataFrame({
        "loan_amnt": [-500.0, 10000.0],       # Negative loan amount
        "funded_amnt": [5000.0, 0.0],         # Zero funded
        "int_rate": [120.0, 14.2],            # Over 100%
        "total_pymnt": [-50.0, 2000.0],       # Negative payment
        "out_prncp": [-10.0, 8000.0],         # Negative outstanding
        "annual_inc": [-100.0, 85000.0]       # Negative income
    })
    res_invalid = validate_financial_boundaries(df_invalid)
    assert res_invalid["all_boundaries_valid"] is False
    assert res_invalid["invalid_loan_amount_count"] == 1
    assert res_invalid["invalid_funded_amount_count"] == 1
    assert res_invalid["invalid_interest_rate_count"] == 1
    assert res_invalid["negative_total_payment_count"] == 1
    assert res_invalid["negative_outstanding_principal_count"] == 1
    assert res_invalid["negative_annual_income_count"] == 1

def test_validate_categorical_domains():
    df_grades = pd.DataFrame({
        "grade": ["A", "B", "C", "X"],
        "term_months": [36, 60, 48, 36]
    })
    res = validate_categorical_domains(df_grades)
    assert res["grades_valid"] is False
    assert "X" in res["invalid_grades"]
    assert res["terms_valid"] is False
    assert 48 in res["invalid_terms"]
