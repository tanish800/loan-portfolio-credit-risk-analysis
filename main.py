"""
Master Orchestration Pipeline for Loan Portfolio & Credit Risk Analysis.
Executes the complete reproducible financial analytics lifecycle:
1. Data Verification / Ingestion
2. Schema & Boundary Validation
3. Robust Chunked Data Cleaning & Feature Engineering
4. Portfolio KPIs & Credit Risk Analysis
5. Publication-grade Visualizations
6. Dimensional Star Schema Extraction for Power BI
7. Excel Financial Workbook Generation ('Loan_Portfolio_Analysis.xlsx')
8. Comprehensive Reporting
"""

import sys
import time
import json
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    PROCESSED_CSV_PATH,
    METADATA_DIR,
    REPORTS_DIR,
    VIS_DIR,
    EXCEL_DIR,
    POWERBI_DIR,
    DATASET_NAME,
    DATASET_SOURCE_URL
)
from src.data_download import download_dataset
from src.data_validation import run_full_validation
from src.data_cleaning import process_and_clean_dataset
from src.financial_metrics import calculate_portfolio_kpis
from src.analysis import run_portfolio_analysis
from src.excel_generator import build_excel_workbook
import pandas as pd

def export_powerbi_star_schema(df: pd.DataFrame):
    """
    Export dedicated fact and dimension CSV files for Power BI Desktop ingestion.
    """
    pbi_dir = POWERBI_DIR / "data_model"
    pbi_dir.mkdir(parents=True, exist_ok=True)
    print(f"Exporting Power BI dimensional star schema tables to {pbi_dir}...")

    # 1. Dim_Date
    dates = pd.date_range(start="2007-01-01", end="2018-12-31", freq="D")
    dim_date = pd.DataFrame({
        "Date": dates,
        "Year": dates.year,
        "Quarter": "Q" + dates.quarter.astype(str),
        "MonthNumber": dates.month,
        "MonthName": dates.strftime("%B"),
        "YearMonth": dates.strftime("%Y-%m"),
        "FiscalYear": "FY" + dates.year.astype(str)
    })
    dim_date.to_csv(pbi_dir / "Dim_Date.csv", index=False)

    # 2. Dim_Grade
    subgrades = sorted(df["sub_grade"].dropna().unique())
    grade_map = {sg: sg[0] for sg in subgrades}
    tier_map = {
        "A": "Prime", "B": "Prime",
        "C": "Near Prime", "D": "Near Prime",
        "E": "Subprime", "F": "High Risk", "G": "High Risk"
    }
    dim_grade = pd.DataFrame({
        "SubGrade": subgrades,
        "Grade": [grade_map[sg] for sg in subgrades],
        "RiskTier": [tier_map.get(grade_map[sg], "Standard") for sg in subgrades],
        "GradeRank": list(range(1, len(subgrades) + 1))
    })
    dim_grade.to_csv(pbi_dir / "Dim_Grade.csv", index=False)

    # 3. Dim_LoanPurpose
    purposes = sorted(df["purpose"].dropna().unique())
    def broad_cat(p):
        p_lower = str(p).lower()
        if "debt" in p_lower or "credit" in p_lower:
            return "Refinancing & Debt Relief"
        elif "business" in p_lower:
            return "Commercial & Business"
        elif "home" in p_lower or "house" in p_lower:
            return "Real Estate & Home"
        else:
            return "Personal & Lifestyle"

    dim_purpose = pd.DataFrame({
        "Purpose": purposes,
        "PurposeName": [p.replace("_", " ").title() for p in purposes],
        "BroadCategory": [broad_cat(p) for p in purposes]
    })
    dim_purpose.to_csv(pbi_dir / "Dim_LoanPurpose.csv", index=False)

    # 4. Dim_Geography
    states = sorted(df["addr_state"].dropna().unique())
    dim_geo = pd.DataFrame({
        "StateCode": states,
        "StateName": states  # Standard 2-letter postal code
    })
    dim_geo.to_csv(pbi_dir / "Dim_Geography.csv", index=False)

    # 5. Fact_Loans Extract (Representative 100,000 analytical loan accounts for fast Power BI loading)
    sample_size = min(100_000, len(df))
    fact_cols = [
        "id", "loan_amnt", "funded_amnt", "term_months", "int_rate", "installment",
        "grade", "sub_grade", "emp_length_years", "home_ownership", "annual_inc",
        "verification_status", "issue_d_parsed", "loan_status_standard", "purpose",
        "addr_state", "dti", "fico_avg", "out_prncp", "total_pymnt", "total_rec_prncp",
        "total_rec_int", "total_rec_late_fee", "recoveries", "is_bad_loan", "is_delinquent"
    ]
    fact_loans = df[[c for c in fact_cols if c in df.columns]].sample(n=sample_size, random_state=42)
    fact_loans.to_csv(pbi_dir / "Fact_Loans_100k.csv", index=False)
    print(f"Power BI star schema exported ({len(fact_loans):,} fact rows).")

def main():
    print("=" * 80)
    print("LOAN PORTFOLIO & CREDIT RISK ANALYSIS: END-TO-END MASTER PIPELINE")
    print("=" * 80)
    start_total = time.time()

    # Step 1: Ingestion
    print("\n[Step 1/7] Checking dataset availability...")
    if not RAW_DATA_PATH.exists():
        print(f"Raw dataset not found at {RAW_DATA_PATH}. Triggering download...")
        download_dataset()
    else:
        print(f"Authentic raw dataset confirmed: {RAW_DATA_PATH} ({RAW_DATA_PATH.stat().st_size:,} bytes).")

    # Step 2: Data Cleaning & Processing
    print("\n[Step 2/7] Checking cleaned dataset...")
    if not PROCESSED_DATA_PATH.exists():
        print("Processing raw records through chunked ETL pipeline...")
        process_and_clean_dataset()
    else:
        print(f"Cleaned dataset already exists: {PROCESSED_DATA_PATH}")

    # Load cleaned dataset for analysis
    print("\nLoading cleaned dataset into memory...")
    t0 = time.time()
    df = pd.read_parquet(PROCESSED_DATA_PATH)
    print(f"Loaded {len(df):,} cleaned loan records in {time.time() - t0:.1f}s.")

    # Step 3: Data Validation
    print("\n[Step 3/7] Running full validation suite...")
    val_report = run_full_validation(df)
    print(f"Validation complete: Unique IDs: {val_report['uniqueness_validation']['is_unique']} | "
          f"Financial Boundaries Valid: {val_report['financial_boundary_validation']['all_boundaries_valid']}")

    # Step 4: Financial Metrics & Visualizations
    print("\n[Step 4/7] Computing financial metrics and generating visualizations...")
    summary_results = run_portfolio_analysis(df)
    kpis = summary_results["kpis"]
    print(f"Portfolio KPIs: Total Funded: ${kpis['total_funded_amnt']:,.2f} | "
          f"Closed Default Rate: {kpis['terminal_default_rate_pct']:.2f}% | "
          f"Delinquency Rate: {kpis['delinquency_rate_active_pct']:.2f}%")

    # Step 5: Power BI Dimensional Model Export
    print("\n[Step 5/7] Preparing Power BI Star Schema extracts...")
    export_powerbi_star_schema(df)

    # Step 6: Excel Financial Workbook Creation
    print("\n[Step 6/7] Building Excel Financial Workbook ('Loan_Portfolio_Analysis.xlsx')...")
    excel_path = build_excel_workbook()
    print(f"Excel workbook generated at: {excel_path}")

    # Step 7: Final Summary
    elapsed_total = time.time() - start_total
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed_total:.1f} SECONDS")
    print(f"Cleaned Records: {len(df):,}")
    print(f"Parquet Path: {PROCESSED_DATA_PATH}")
    print(f"Excel Path: {excel_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
