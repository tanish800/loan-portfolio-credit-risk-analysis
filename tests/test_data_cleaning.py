"""
Unit tests for Data Cleaning and Transformation Module.
Validates string parsing, type transformations, loan status mappings, and missing value logic.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import (
    parse_emp_length,
    clean_term,
    standardize_status,
    clean_chunk
)

def test_parse_emp_length():
    assert parse_emp_length("< 1 year") == 0.5
    assert parse_emp_length("1 year") == 1.0
    assert parse_emp_length("5 years") == 5.0
    assert parse_emp_length("10+ years") == 10.0
    assert np.isnan(parse_emp_length(np.nan))
    assert np.isnan(parse_emp_length("n/a"))

def test_clean_term():
    assert clean_term(" 36 months") == 36
    assert clean_term(" 60 months") == 60
    assert clean_term(36) == 36
    assert clean_term(np.nan) == 36

def test_standardize_status():
    assert standardize_status("Fully Paid") == "Fully Paid"
    assert standardize_status("Charged Off") == "Charged Off"
    assert standardize_status("Current") == "Current"
    assert standardize_status("Late (31-120 days)") == "Late (31-120 days)"
    assert standardize_status("Does not meet the credit policy. Status:Fully Paid") == "Fully Paid (Legacy)"

def test_clean_chunk():
    raw_sample = pd.DataFrame({
        "id": ["1001", "1002", "Total amount funded in policy code 1: 12345", None],
        "loan_amnt": ["5000", "12000", None, None],
        "funded_amnt": ["5000", "12000", None, None],
        "term": [" 36 months", " 60 months", None, None],
        "int_rate": ["8.99", "15.49", None, None],
        "installment": ["158.98", "288.62", None, None],
        "grade": [" A ", "C", None, None],
        "sub_grade": ["A2", "C3", None, None],
        "emp_length": ["< 1 year", "10+ years", None, None],
        "home_ownership": ["rent", "MORTGAGE", None, None],
        "annual_inc": ["45000", "85000", None, None],
        "issue_d": ["Dec-2015", "Aug-2016", None, None],
        "loan_status": ["Fully Paid", "Charged Off", None, None],
        "purpose": ["credit_card", "debt_consolidation", None, None],
        "addr_state": ["ca", "ny", None, None],
        "dti": ["12.5", "22.4", None, None],
        "out_prncp": ["0.0", "0.0", None, None],
        "total_pymnt": ["5723.28", "4102.10", None, None],
        "total_rec_prncp": ["5000.0", "2500.0", None, None],
        "total_rec_int": ["723.28", "1602.10", None, None],
        "total_rec_late_fee": [None, "50.0", None, None],
        "recoveries": [None, "800.0", None, None]
    })
    
    cleaned = clean_chunk(raw_sample)
    
    # Trailer / invalid rows removed
    assert len(cleaned) == 2
    assert set(cleaned["id"]) == {"1001", "1002"}
    
    # Term converted
    assert list(cleaned["term_months"]) == [36, 60]
    
    # Grades upper-cased
    assert list(cleaned["grade"]) == ["A", "C"]
    
    # Home ownership upper-cased
    assert list(cleaned["home_ownership"]) == ["RENT", "MORTGAGE"]
    
    # Numeric types
    assert cleaned["loan_amnt"].dtype == "float64"
    assert cleaned["recoveries"].iloc[0] == 0.0  # Filled NaN with 0
    assert cleaned["recoveries"].iloc[1] == 800.0
    
    # Status indicators
    assert cleaned["is_bad_loan"].iloc[0] == 0.0  # Fully Paid
    assert cleaned["is_bad_loan"].iloc[1] == 1.0  # Charged Off
