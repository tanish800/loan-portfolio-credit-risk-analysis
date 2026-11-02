"""
Unit tests for Financial Metrics and Credit Risk Calculation Engine.
Validates zero division errors, mathematical precision, and edge-case handling.
"""

import pytest
import pandas as pd
import numpy as np
from src.financial_metrics import (
    calculate_portfolio_kpis,
    analyze_by_dimension,
    analyze_vintages
)

@pytest.fixture
def sample_portfolio_df():
    """Create controlled sample portfolio with known expected outcomes."""
    data = {
        "id": ["1", "2", "3", "4", "5"],
        "loan_amnt": [10000.0, 20000.0, 15000.0, 30000.0, 25000.0],
        "funded_amnt": [10000.0, 20000.0, 15000.0, 30000.0, 25000.0],
        "term_months": [36, 60, 36, 60, 36],
        "int_rate": [7.5, 12.0, 18.5, 24.0, 10.0],
        "installment": [311.0, 444.0, 546.0, 864.0, 806.0],
        "grade": ["A", "B", "D", "E", "B"],
        "sub_grade": ["A3", "B2", "D4", "E1", "B5"],
        "loan_status_standard": [
            "Fully Paid",           # Closed non-default
            "Current",              # Active performing
            "Charged Off",          # Closed default
            "Late (31-120 days)",   # Active delinquent
            "Fully Paid"            # Closed non-default
        ],
        "out_prncp": [0.0, 15000.0, 0.0, 28000.0, 0.0],
        "total_pymnt": [11196.0, 6000.0, 3500.0, 2000.0, 29000.0],
        "total_rec_prncp": [10000.0, 5000.0, 2000.0, 1000.0, 25000.0],
        "total_rec_int": [1196.0, 1000.0, 1500.0, 1000.0, 4000.0],
        "total_rec_late_fee": [0.0, 0.0, 50.0, 100.0, 0.0],
        "recoveries": [0.0, 0.0, 1200.0, 0.0, 0.0],
        "issue_year": [2015, 2016, 2015, 2017, 2016],
        "purpose": ["credit_card", "debt_consolidation", "small_business", "debt_consolidation", "home_improvement"],
        "income_bracket": ["$60K - $90K", "$35K - $60K", "< $35K", "$120K+", "$90K - $120K"],
        "dti_bracket": ["10% - 20%", "20% - 30%", "30%+", "10% - 20%", "< 10%"],
        "home_ownership": ["MORTGAGE", "RENT", "RENT", "MORTGAGE", "OWN"],
        "addr_state": ["CA", "NY", "TX", "FL", "CA"]
    }
    return pd.DataFrame(data)

def test_portfolio_kpis_basic(sample_portfolio_df):
    kpis = calculate_portfolio_kpis(sample_portfolio_df)
    
    assert kpis["total_loans"] == 5
    assert kpis["total_loan_amnt"] == 100000.0
    assert kpis["total_funded_amnt"] == 100000.0
    assert kpis["total_out_prncp"] == 43000.0
    assert kpis["total_pymnt"] == 51696.0
    assert kpis["total_rec_prncp"] == 43000.0
    assert kpis["total_rec_int"] == 8696.0
    assert kpis["total_rec_late_fee"] == 150.0
    assert kpis["total_recoveries"] == 1200.0
    assert kpis["avg_loan_amnt"] == 20000.0
    assert kpis["avg_int_rate"] == 14.4

def test_default_and_delinquency_rates(sample_portfolio_df):
    kpis = calculate_portfolio_kpis(sample_portfolio_df)
    
    # Closed cohort: 2 Fully Paid + 1 Charged Off = 3 loans
    # Bad loans: 1 Charged Off
    # Terminal Default Rate = 1 / 3 = 33.33%
    assert kpis["closed_loans_count"] == 3
    assert kpis["terminal_default_rate_pct"] == 33.33
    
    # Portfolio Default Rate = 1 / 5 = 20.00%
    assert kpis["portfolio_default_rate_pct"] == 20.0
    
    # Active cohort: 1 Current + 1 Late = 2 loans
    # Delinquency Rate = 1 / 2 = 50.00%
    assert kpis["active_loans_count"] == 2
    assert kpis["delinquency_rate_active_pct"] == 50.0

def test_financial_ratios(sample_portfolio_df):
    kpis = calculate_portfolio_kpis(sample_portfolio_df)
    
    # Charged off funded: 15,000 (from loan 3)
    # Total funded: 100,000
    # Charge-off rate = 15,000 / 100,000 = 15.00%
    assert kpis["charge_off_rate_pct"] == 15.0
    
    # Recovery rate: 1,200 recoveries / 15,000 charged off funded = 8.00%
    assert kpis["recovery_rate_pct"] == 8.0
    
    # Outstanding ratio: 43,000 / 100,000 = 43.00%
    assert kpis["outstanding_portfolio_ratio_pct"] == 43.0

def test_division_by_zero_safety():
    empty_df = pd.DataFrame(columns=[
        "id", "loan_amnt", "funded_amnt", "term_months", "int_rate",
        "installment", "loan_status_standard", "out_prncp", "total_pymnt",
        "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries"
    ])
    kpis = calculate_portfolio_kpis(empty_df)
    assert kpis == {}

def test_dimension_breakdown(sample_portfolio_df):
    grade_metrics = analyze_by_dimension(sample_portfolio_df, "grade")
    assert len(grade_metrics) == 4  # A, B, D, E
    
    grade_a = grade_metrics[grade_metrics["grade"] == "A"].iloc[0]
    assert grade_a["total_loans"] == 1
    assert grade_a["terminal_default_rate_pct"] == 0.0
    
    grade_d = grade_metrics[grade_metrics["grade"] == "D"].iloc[0]
    assert grade_d["total_loans"] == 1
    assert grade_d["terminal_default_rate_pct"] == 100.0
