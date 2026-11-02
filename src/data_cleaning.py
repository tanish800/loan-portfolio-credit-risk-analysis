"""
Data cleaning and ETL pipeline for LendingClub Loan Portfolio.
Processes the authentic historical dataset using chunking to maintain memory efficiency.
Performs rigorous schema validation, type conversions, missing-value treatments,
and derived credit feature engineering.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    PROCESSED_CSV_PATH,
    METADATA_DIR,
    REPORTS_DIR,
    CORE_COLUMNS,
    STATUS_CATEGORIES
)

def parse_emp_length(val: Any) -> float:
    """Parse employment length string to numeric years."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip().lower()
    if "<" in val_str:
        return 0.5
    elif "10+" in val_str:
        return 10.0
    else:
        # Extract digits
        digits = "".join([c for c in val_str if c.isdigit()])
        return float(digits) if digits else np.nan

def clean_term(val: Any) -> int:
    """Standardize loan term string (' 36 months' -> 36, ' 60 months' -> 60)."""
    if pd.isna(val):
        return 36
    val_str = str(val).strip()
    if "60" in val_str:
        return 60
    return 36

def standardize_status(status_raw: Any) -> str:
    """Map raw loan status to standardized status categories."""
    if pd.isna(status_raw):
        return "Unknown"
    status_str = str(status_raw).strip()
    return STATUS_CATEGORIES.get(status_str, status_str)

def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform a single chunk of records."""
    # 1. Filter out summary/trailer rows (where id is null or non-numeric/empty)
    chunk = chunk.dropna(subset=["id", "loan_amnt"]).copy()
    chunk["id"] = chunk["id"].astype(str).str.strip()
    chunk = chunk[chunk["id"].str.isdigit()].copy()
    
    if len(chunk) == 0:
        return chunk

    # 2. Numeric Conversions
    num_cols = [
        "loan_amnt", "funded_amnt", "funded_amnt_inv", "int_rate", "installment",
        "annual_inc", "dti", "delinq_2yrs", "fico_range_low", "fico_range_high",
        "inq_last_6mths", "open_acc", "pub_rec", "revol_bal", "revol_util",
        "total_acc", "out_prncp", "out_prncp_inv", "total_pymnt", "total_pymnt_inv",
        "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries",
        "collection_recovery_fee", "last_pymnt_amnt", "tot_coll_amt", "tot_cur_bal"
    ]
    for col in num_cols:
        if col in chunk.columns:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype("float64")

    # Fill non-material missing numeric metrics with zero where appropriate (fees, recoveries)
    zero_fill_cols = ["recoveries", "collection_recovery_fee", "total_rec_late_fee", "out_prncp", "out_prncp_inv"]
    for col in zero_fill_cols:
        if col in chunk.columns:
            chunk[col] = chunk[col].fillna(0.0)

    # 3. Clean Term & Employment Length
    chunk["term_months"] = chunk["term"].apply(clean_term).astype("int32")
    chunk["emp_length_years"] = chunk["emp_length"].apply(parse_emp_length)

    # 4. Standardize Loan Status
    chunk["loan_status_standard"] = chunk["loan_status"].apply(standardize_status)

    # 5. Parse Dates (LendingClub format is Mon-YYYY e.g. Dec-2015)
    chunk["issue_d_parsed"] = pd.to_datetime(chunk["issue_d"], format="%b-%Y", errors="coerce")
    chunk["issue_year"] = chunk["issue_d_parsed"].dt.year.astype("Int64")
    chunk["issue_month"] = chunk["issue_d_parsed"].dt.month.astype("Int64")
    chunk["issue_year_month"] = chunk["issue_d_parsed"].dt.strftime("%Y-%m")

    # 6. Feature Engineering
    # Average FICO
    if "fico_range_low" in chunk.columns and "fico_range_high" in chunk.columns:
        chunk["fico_avg"] = (chunk["fico_range_low"] + chunk["fico_range_high"]) / 2.0

    # Income Bracket
    def categorize_income(inc):
        if pd.isna(inc):
            return "Missing"
        elif inc < 35000:
            return "< $35K"
        elif inc < 60000:
            return "$35K - $60K"
        elif inc < 90000:
            return "$60K - $90K"
        elif inc < 120000:
            return "$90K - $120K"
        else:
            return "$120K+"
    chunk["income_bracket"] = chunk["annual_inc"].apply(categorize_income)

    # DTI Bracket
    def categorize_dti(dti):
        if pd.isna(dti):
            return "Missing"
        elif dti < 10:
            return "< 10%"
        elif dti < 20:
            return "10% - 20%"
        elif dti < 30:
            return "20% - 30%"
        else:
            return "30%+"
    chunk["dti_bracket"] = chunk["dti"].apply(categorize_dti)

    # Bad Loan indicator (1 = Default / Charged Off, 0 = Fully Paid, NaN = Active)
    chunk["is_bad_loan"] = np.where(
        chunk["loan_status_standard"].isin(["Charged Off", "Default"]), 1,
        np.where(chunk["loan_status_standard"] == "Fully Paid", 0, np.nan)
    )

    # Delinquent indicator (1 = Late 16-30 or 31-120 days, 0 = Current or In Grace Period)
    chunk["is_delinquent"] = np.where(
        chunk["loan_status_standard"].isin(["Late (31-120 days)", "Late (16-30 days)"]), 1,
        np.where(chunk["loan_status_standard"].isin(["Current", "In Grace Period"]), 0, np.nan)
    )

    # Clean Grade and Subgrade
    chunk["grade"] = chunk["grade"].astype(str).str.strip().str.upper()
    chunk["sub_grade"] = chunk["sub_grade"].astype(str).str.strip().str.upper()
    chunk["home_ownership"] = chunk["home_ownership"].astype(str).str.strip().str.upper()
    chunk["purpose"] = chunk["purpose"].astype(str).str.strip().str.lower()
    chunk["addr_state"] = chunk["addr_state"].astype(str).str.strip().str.upper()

    return chunk

def process_and_clean_dataset(chunk_size: int = 150_000) -> Tuple[Path, Dict[str, Any]]:
    """
    Execute streaming ETL over the full LendingClub dataset.
    Generates Parquet storage and a data quality summary report.
    """
    print(f"Starting chunked ETL processing of {RAW_DATA_PATH}...")
    start_time = time.time()
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_row_count = 0
    cleaned_row_count = 0
    duplicate_ids_count = 0
    seen_ids = set()
    cleaned_chunks = []

    # Use selected columns to optimize I/O and memory
    use_cols = [c for c in CORE_COLUMNS if c != "id"] + ["id"]

    chunk_iter = pd.read_csv(
        RAW_DATA_PATH,
        chunksize=chunk_size,
        usecols=lambda c: c in use_cols,
        low_memory=False,
        encoding="utf-8"
    )

    for i, raw_chunk in enumerate(chunk_iter):
        raw_row_count += len(raw_chunk)
        cleaned = clean_chunk(raw_chunk)
        
        # Check for duplicates across chunks
        chunk_ids = cleaned["id"].astype(str).tolist()
        unique_mask = [id_ not in seen_ids for id_ in chunk_ids]
        
        duplicates_in_chunk = len(chunk_ids) - sum(unique_mask)
        duplicate_ids_count += duplicates_in_chunk
        
        cleaned_deduped = cleaned[unique_mask].copy()
        seen_ids.update(cleaned_deduped["id"].astype(str))
        
        cleaned_row_count += len(cleaned_deduped)
        cleaned_chunks.append(cleaned_deduped)

        print(f"Processed chunk {i+1}: Cumulative raw rows: {raw_row_count:,} | Cleaned rows: {cleaned_row_count:,}")

    # Concatenate all cleaned data
    print("Concatenating processed chunks...")
    full_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    # Ensure uniform types across object columns for pyarrow
    for col in full_df.select_dtypes(include=["object"]).columns:
        full_df[col] = full_df[col].astype(str)
    
    # Save full cleaned dataset to Parquet
    print(f"Exporting full cleaned dataset to {PROCESSED_DATA_PATH}...")
    full_df.to_parquet(PROCESSED_DATA_PATH, index=False, engine="pyarrow", compression="snappy")

    # Export a representative sample (100,000 records) to CSV for Excel and PowerBI direct table view
    sample_size = min(100_000, len(full_df))
    print(f"Exporting representative analytical sample ({sample_size:,} rows) to {PROCESSED_CSV_PATH}...")
    sample_df = full_df.sample(n=sample_size, random_state=42)
    sample_df.to_csv(PROCESSED_CSV_PATH, index=False)

    elapsed = time.time() - start_time
    print(f"ETL completed in {elapsed:.1f}s. Final Cleaned Records: {cleaned_row_count:,}")

    # Generate Data Quality Report Data
    quality_summary = {
        "raw_record_count": raw_row_count,
        "cleaned_record_count": cleaned_row_count,
        "rows_removed": raw_row_count - cleaned_row_count,
        "duplicate_ids_detected": duplicate_ids_count,
        "total_columns_processed": len(full_df.columns),
        "columns_list": list(full_df.columns),
        "parquet_file_path": str(PROCESSED_DATA_PATH),
        "parquet_size_mb": round(PROCESSED_DATA_PATH.stat().st_size / (1024**2), 2),
        "sample_csv_path": str(PROCESSED_CSV_PATH),
        "execution_time_seconds": round(elapsed, 2)
    }

    report_file = METADATA_DIR / "data_cleaning_summary.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(quality_summary, f, indent=4)

    return PROCESSED_DATA_PATH, quality_summary

if __name__ == "__main__":
    process_and_clean_dataset()
