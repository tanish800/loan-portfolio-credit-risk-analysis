"""
Data validation module for LendingClub Loan Portfolio.
Verifies data schema, integrity, uniqueness, range boundaries, and consistency.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import CORE_COLUMNS, METADATA_DIR

def validate_raw_schema(df_sample: pd.DataFrame) -> Dict[str, Any]:
    """Validate that expected core financial attributes exist in the raw dataset."""
    present_cols = set(df_sample.columns)
    missing_cols = [col for col in CORE_COLUMNS if col not in present_cols]
    
    return {
        "total_columns_found": len(df_sample.columns),
        "core_columns_expected": len(CORE_COLUMNS),
        "core_columns_present": len(CORE_COLUMNS) - len(missing_cols),
        "missing_core_columns": missing_cols,
        "is_valid": len(missing_cols) == 0
    }

def validate_id_uniqueness(df: pd.DataFrame) -> Dict[str, Any]:
    """Verify unique loan identifiers and identify any duplicate loan IDs."""
    if "id" not in df.columns:
        return {"status": "FAIL", "message": "id column missing"}
    
    # Exclude null or empty IDs first
    valid_ids = df["id"].dropna()
    total_ids = len(valid_ids)
    unique_ids = valid_ids.nunique()
    duplicates = total_ids - unique_ids
    
    return {
        "total_ids": total_ids,
        "unique_ids": unique_ids,
        "duplicate_count": duplicates,
        "is_unique": duplicates == 0
    }

def validate_financial_boundaries(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for negative or logically impossible financial values."""
    checks = {}
    
    # 1. Loan Amount > 0
    if "loan_amnt" in df.columns:
        invalid_loan_amnt = int((df["loan_amnt"] <= 0).sum())
        checks["invalid_loan_amount_count"] = invalid_loan_amnt
    
    # 2. Funded Amount > 0
    if "funded_amnt" in df.columns:
        invalid_funded_amnt = int((df["funded_amnt"] <= 0).sum())
        checks["invalid_funded_amount_count"] = invalid_funded_amnt
        
    # 3. Interest Rate in [0, 100]
    if "int_rate" in df.columns:
        invalid_rate = int(((df["int_rate"] < 0) | (df["int_rate"] > 100)).sum())
        checks["invalid_interest_rate_count"] = invalid_rate
        
    # 4. Total Payment >= 0
    if "total_pymnt" in df.columns:
        invalid_pymnt = int((df["total_pymnt"] < 0).sum())
        checks["negative_total_payment_count"] = invalid_pymnt
        
    # 5. Outstanding Principal >= 0
    if "out_prncp" in df.columns:
        invalid_out_prncp = int((df["out_prncp"] < 0).sum())
        checks["negative_outstanding_principal_count"] = invalid_out_prncp
        
    # 6. Annual Income >= 0
    if "annual_inc" in df.columns:
        invalid_income = int((df["annual_inc"] < 0).sum())
        checks["negative_annual_income_count"] = invalid_income
        
    # Overall boundary pass
    all_passed = all(count == 0 for count in checks.values())
    checks["all_boundaries_valid"] = all_passed
    return checks

def validate_categorical_domains(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate categorical fields against known domain spaces."""
    valid_grades = {"A", "B", "C", "D", "E", "F", "G"}
    results = {}
    
    if "grade" in df.columns:
        observed_grades = set(df["grade"].dropna().unique())
        invalid_grades = observed_grades - valid_grades
        results["invalid_grades"] = list(invalid_grades)
        results["grades_valid"] = len(invalid_grades) == 0
        
    if "term_months" in df.columns:
        observed_terms = set(df["term_months"].dropna().unique())
        valid_terms = {36, 60}
        invalid_terms = observed_terms - valid_terms
        results["invalid_terms"] = list(invalid_terms)
        results["terms_valid"] = len(invalid_terms) == 0
        
    return results

def run_full_validation(df: pd.DataFrame, report_name: str = "validation_report.json") -> Dict[str, Any]:
    """Execute complete validation suite and persist report."""
    report = {
        "record_count": len(df),
        "column_count": len(df.columns),
        "uniqueness_validation": validate_id_uniqueness(df),
        "financial_boundary_validation": validate_financial_boundaries(df),
        "categorical_validation": validate_categorical_domains(df),
        "null_counts_core": {col: int(df[col].isna().sum()) for col in CORE_COLUMNS if col in df.columns}
    }
    
    out_file = METADATA_DIR / report_name
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    return report
