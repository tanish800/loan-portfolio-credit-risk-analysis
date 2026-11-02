"""
Configuration module for Loan Portfolio & Credit Risk Analysis Project.
Defines directory paths, URLs, column specifications, and analysis thresholds.
"""

from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

# Output directories
REPORTS_DIR = BASE_DIR / "reports"
VIS_DIR = BASE_DIR / "visualizations"
EXCEL_DIR = BASE_DIR / "excel"
POWERBI_DIR = BASE_DIR / "powerbi"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
TESTS_DIR = BASE_DIR / "tests"

# Dataset URL & File details
DATASET_NAME = "LendingClub Loan Accepted Dataset"
DATASET_REPO = "codesignal/lending-club-loan-accepted"
DATASET_SOURCE_URL = "https://huggingface.co/datasets/codesignal/lending-club-loan-accepted"
RAW_DATA_FILENAME = "accepted_2007_to_2018Q4.csv"
RAW_DATA_PATH = RAW_DATA_DIR / RAW_DATA_FILENAME
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "cleaned_lending_club_loans.parquet"
PROCESSED_CSV_PATH = PROCESSED_DATA_DIR / "cleaned_lending_club_loans_sample.csv"
POWERBI_DATA_DIR = POWERBI_DIR / "data_model"

# Key analysis columns to select and clean
CORE_COLUMNS = [
    "id",
    "loan_amnt",
    "funded_amnt",
    "funded_amnt_inv",
    "term",
    "int_rate",
    "installment",
    "grade",
    "sub_grade",
    "emp_title",
    "emp_length",
    "home_ownership",
    "annual_inc",
    "verification_status",
    "issue_d",
    "loan_status",
    "purpose",
    "title",
    "addr_state",
    "dti",
    "delinq_2yrs",
    "earliest_cr_line",
    "fico_range_low",
    "fico_range_high",
    "inq_last_6mths",
    "open_acc",
    "pub_rec",
    "revol_bal",
    "revol_util",
    "total_acc",
    "initial_list_status",
    "out_prncp",
    "out_prncp_inv",
    "total_pymnt",
    "total_pymnt_inv",
    "total_rec_prncp",
    "total_rec_int",
    "total_rec_late_fee",
    "recoveries",
    "collection_recovery_fee",
    "last_pymnt_d",
    "last_pymnt_amnt",
    "last_fico_range_high",
    "last_fico_range_low",
    "application_type",
    "tot_coll_amt",
    "tot_cur_bal",
    "pub_rec_bankruptcies",
    "tax_liens",
    "mort_acc"
]

# Standard financial loan status categories
STATUS_CATEGORIES = {
    "Fully Paid": "Fully Paid",
    "Current": "Current",
    "Charged Off": "Charged Off",
    "Default": "Default",
    "Late (31-120 days)": "Late (31-120 days)",
    "In Grace Period": "In Grace Period",
    "Late (16-30 days)": "Late (16-30 days)",
    "Does not meet the credit policy. Status:Fully Paid": "Fully Paid (Legacy)",
    "Does not meet the credit policy. Status:Charged Off": "Charged Off (Legacy)"
}

# Color palette for financial visualization
COLOR_PALETTE = {
    "primary": "#1f4e79",      # Navy Blue
    "secondary": "#2ca02c",    # Green
    "accent": "#00a88f",       # Teal
    "danger": "#d9534f",       # Crimson/Red
    "warning": "#f0ad4e",      # Amber
    "info": "#5bc0de",         # Sky Blue
    "neutral": "#6c757d",      # Slate Gray
    "background": "#f8f9fa"
}
