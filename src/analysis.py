"""
Financial analysis, risk aggregation, and visualization engine.
Processes the cleaned LendingClub portfolio, evaluates empirical credit risk,
and generates charts for reports and dashboards.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import (
    PROCESSED_DATA_PATH,
    VIS_DIR,
    METADATA_DIR,
    COLOR_PALETTE
)
from src.financial_metrics import (
    calculate_portfolio_kpis,
    analyze_by_dimension,
    analyze_vintages
)

# Apply global publication styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

def format_currency(x, pos):
    """Format tick values as billions, millions or thousands."""
    if abs(x) >= 1e9:
        return f"${x*1e-9:.1f}B"
    elif abs(x) >= 1e6:
        return f"${x*1e-6:.1f}M"
    elif abs(x) >= 1e3:
        return f"${x*1e-3:.0f}K"
    else:
        return f"${x:.0f}"

def run_portfolio_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute complete analysis and output summary datasets and visualizations."""
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Calculating overall portfolio KPIs...")
    kpis = calculate_portfolio_kpis(df)

    print("Analyzing by Grade...")
    grade_df = analyze_by_dimension(df, "grade")
    # Sort grades A through G
    valid_grades = ["A", "B", "C", "D", "E", "F", "G"]
    grade_df = grade_df[grade_df["grade"].isin(valid_grades)].sort_values(
        "grade", key=lambda x: pd.Categorical(x, categories=valid_grades, ordered=True)
    )

    print("Analyzing by Subgrade...")
    subgrade_df = analyze_by_dimension(df, "sub_grade").sort_values("sub_grade")

    print("Analyzing by Loan Purpose...")
    purpose_df = analyze_by_dimension(df, "purpose").sort_values("total_funded_amnt", ascending=False)

    print("Analyzing by Loan Term...")
    term_df = analyze_by_dimension(df, "term_months").sort_values("term_months")

    print("Analyzing by Income Bracket...")
    income_order = ["< $35K", "$35K - $60K", "$60K - $90K", "$90K - $120K", "$120K+"]
    income_df = analyze_by_dimension(df, "income_bracket")
    income_df = income_df[income_df["income_bracket"].isin(income_order)].sort_values(
        "income_bracket", key=lambda x: pd.Categorical(x, categories=income_order, ordered=True)
    )

    print("Analyzing by DTI Bracket...")
    dti_order = ["< 10%", "10% - 20%", "20% - 30%", "30%+"]
    dti_df = analyze_by_dimension(df, "dti_bracket")
    dti_df = dti_df[dti_df["dti_bracket"].isin(dti_order)].sort_values(
        "dti_bracket", key=lambda x: pd.Categorical(x, categories=dti_order, ordered=True)
    )

    print("Analyzing by Home Ownership...")
    home_df = analyze_by_dimension(df, "home_ownership").sort_values("total_funded_amnt", ascending=False)

    print("Analyzing by State...")
    state_df = analyze_by_dimension(df, "addr_state").sort_values("total_funded_amnt", ascending=False)

    print("Analyzing Origination Vintages...")
    vintage_df = analyze_vintages(df)

    # Save summary tables to JSON / CSV
    summary_results = {
        "kpis": kpis,
        "grade_metrics": grade_df.to_dict(orient="records"),
        "purpose_metrics": purpose_df.to_dict(orient="records"),
        "term_metrics": term_df.to_dict(orient="records"),
        "income_metrics": income_df.to_dict(orient="records"),
        "dti_metrics": dti_df.to_dict(orient="records"),
        "vintage_metrics": vintage_df.to_dict(orient="records")
    }

    with open(METADATA_DIR / "financial_summary_results.json", "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=4)

    # Save CSVs for Excel builder
    grade_df.to_csv(METADATA_DIR / "summary_grade.csv", index=False)
    purpose_df.to_csv(METADATA_DIR / "summary_purpose.csv", index=False)
    term_df.to_csv(METADATA_DIR / "summary_term.csv", index=False)
    vintage_df.to_csv(METADATA_DIR / "summary_vintage.csv", index=False)
    income_df.to_csv(METADATA_DIR / "summary_income.csv", index=False)
    dti_df.to_csv(METADATA_DIR / "summary_dti.csv", index=False)
    home_df.to_csv(METADATA_DIR / "summary_home.csv", index=False)
    state_df.to_csv(METADATA_DIR / "summary_state.csv", index=False)

    # Generate Visualizations
    generate_all_visualizations(df, kpis, grade_df, purpose_df, term_df, vintage_df, income_df, dti_df, subgrade_df)

    return summary_results

def generate_all_visualizations(
    df: pd.DataFrame,
    kpis: Dict[str, Any],
    grade_df: pd.DataFrame,
    purpose_df: pd.DataFrame,
    term_df: pd.DataFrame,
    vintage_df: pd.DataFrame,
    income_df: pd.DataFrame,
    dti_df: pd.DataFrame,
    subgrade_df: pd.DataFrame
):
    """Generate high-resolution charts for the analysis."""
    print("Generating visualizations...")

    # 1. Loan Status Distribution
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    status_counts = df["loan_status_standard"].value_counts()
    colors = [COLOR_PALETTE["secondary"] if "Paid" in s else COLOR_PALETTE["danger"] if "Charged" in s or "Default" in s else COLOR_PALETTE["primary"] for s in status_counts.index]
    bars = ax.barh(status_counts.index, status_counts.values, color=colors, edgecolor="black", alpha=0.85)
    ax.set_title("LendingClub Historical Portfolio: Loan Status Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Loans", fontsize=11, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df)) * 100
        ax.text(w + (max(status_counts.values)*0.01), bar.get_y() + bar.get_height()/2, f"{int(w):,} ({pct:.1f}%)", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(VIS_DIR / "01_loan_status_distribution.png")
    plt.close()

    # 2. Monthly Origination Trajectory
    if "issue_year_month" in df.columns:
        monthly_trend = df.groupby("issue_year_month", observed=True).agg(
            funded=("funded_amnt", "sum"),
            count=("id", "count")
        ).reset_index()
        monthly_trend = monthly_trend.dropna().sort_values("issue_year_month")

        fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
        ax2 = ax1.twinx()
        
        l1 = ax1.plot(monthly_trend["issue_year_month"], monthly_trend["funded"], color=COLOR_PALETTE["primary"], linewidth=2.2, label="Capital Funded ($)")
        l2 = ax2.plot(monthly_trend["issue_year_month"], monthly_trend["count"], color=COLOR_PALETTE["accent"], linewidth=1.8, linestyle="--", label="Loan Volume (Count)")
        
        ax1.set_title("LendingClub Historical Origination Trajectory (2007 - 2018)", fontsize=14, fontweight="bold", pad=15)
        ax1.set_xlabel("Origination Year-Month", fontsize=11, labelpad=10)
        ax1.set_ylabel("Monthly Capital Funded ($)", fontsize=11, color=COLOR_PALETTE["primary"])
        ax2.set_ylabel("Monthly Loan Volume (Count)", fontsize=11, color=COLOR_PALETTE["accent"])
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

        # Sample every 12th label on x-axis
        ticks = range(0, len(monthly_trend), 12)
        ax1.set_xticks(ticks)
        ax1.set_xticklabels(monthly_trend["issue_year_month"].iloc[ticks], rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(VIS_DIR / "02_origination_trend.png")
        plt.close()

    # 3. Capital Funded by Credit Grade
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bars = ax.bar(grade_df["grade"], grade_df["total_funded_amnt"], color=COLOR_PALETTE["primary"], edgecolor="black", alpha=0.85)
    ax.set_title("Origination Capital Funded by Credit Grade (A through G)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Credit Grade", fontsize=11, labelpad=10)
    ax.set_ylabel("Total Funded Amount ($)", fontsize=11, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + max(grade_df["total_funded_amnt"])*0.01, format_currency(h, 0), ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(VIS_DIR / "03_funded_amount_by_grade.png")
    plt.close()

    # 4. Default Rate vs. Interest Rate by Grade
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
    ax2 = ax1.twinx()
    
    x = np.arange(len(grade_df))
    w = 0.38
    b1 = ax1.bar(x - w/2, grade_df["terminal_default_rate_pct"], width=w, color=COLOR_PALETTE["danger"], label="Closed Default Rate (%)", alpha=0.85)
    b2 = ax2.bar(x + w/2, grade_df["avg_int_rate"], width=w, color=COLOR_PALETTE["primary"], label="Average Interest Rate (%)", alpha=0.85)
    
    ax1.set_title("Credit Risk vs. Pricing: Default Rate & Interest Rate by Grade", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Credit Grade", fontsize=11, labelpad=10)
    ax1.set_ylabel("Closed Cohort Default Rate (%)", fontsize=11, color=COLOR_PALETTE["danger"])
    ax2.set_ylabel("Average Note Interest Rate (%)", fontsize=11, color=COLOR_PALETTE["primary"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(grade_df["grade"])
    
    for bar in b1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%", ha="center", fontsize=8, color=COLOR_PALETTE["danger"], fontweight="bold")
    for bar in b2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%", ha="center", fontsize=8, color=COLOR_PALETTE["primary"], fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(VIS_DIR / "04_default_rate_by_grade.png")
    plt.close()

    # 5. Purpose Distribution & Outstanding Balance
    top_purposes = purpose_df.head(8)
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    y = np.arange(len(top_purposes))
    h = 0.38
    ax.barh(y - h/2, top_purposes["total_funded_amnt"], height=h, color=COLOR_PALETTE["primary"], label="Funded Principal ($)", alpha=0.85)
    ax.barh(y + h/2, top_purposes["total_out_prncp"], height=h, color=COLOR_PALETTE["accent"], label="Outstanding Principal ($)", alpha=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels([p.replace("_", " ").title() for p in top_purposes["purpose"]])
    ax.invert_yaxis()
    ax.set_title("Top Loan Purposes: Capital Origination vs. Outstanding Exposure", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Monetary Amount ($)", fontsize=11, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(VIS_DIR / "05_purpose_distribution.png")
    plt.close()

    # 6. Risk by Term (36 vs 60 Months)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    bars = ax.bar([f"{t} Months" for t in term_df["term_months"]], term_df["terminal_default_rate_pct"], color=[COLOR_PALETTE["primary"], COLOR_PALETTE["danger"]], width=0.5, edgecolor="black")
    ax.set_title("Credit Risk by Loan Tenure: 36 vs. 60 Months", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Closed Cohort Default Rate (%)", fontsize=11, labelpad=10)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.2f}%", ha="center", fontsize=10, fontweight="bold")
    plt.tight_layout()
    plt.savefig(VIS_DIR / "06_risk_by_term.png")
    plt.close()

    # 7. Income & DTI Risk Matrix
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    ax1.bar(income_df["income_bracket"], income_df["terminal_default_rate_pct"], color=COLOR_PALETTE["primary"], edgecolor="black", alpha=0.85)
    ax1.set_title("Default Rate by Annual Income Bracket", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylabel("Default Rate (%)", fontsize=10)
    ax1.set_xticklabels(income_df["income_bracket"], rotation=20, ha="right")
    for idx, row in income_df.iterrows():
        ax1.text(row["income_bracket"], row["terminal_default_rate_pct"] + 0.3, f"{row['terminal_default_rate_pct']:.1f}%", ha="center", fontsize=8, fontweight="bold")

    ax2.bar(dti_df["dti_bracket"], dti_df["terminal_default_rate_pct"], color=COLOR_PALETTE["warning"], edgecolor="black", alpha=0.85)
    ax2.set_title("Default Rate by Debt-to-Income (DTI) Bracket", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylabel("Default Rate (%)", fontsize=10)
    ax2.set_xticklabels(dti_df["dti_bracket"], rotation=20, ha="right")
    for idx, row in dti_df.iterrows():
        ax2.text(row["dti_bracket"], row["terminal_default_rate_pct"] + 0.3, f"{row['terminal_default_rate_pct']:.1f}%", ha="center", fontsize=8, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(VIS_DIR / "07_income_and_dti_risk.png")
    plt.close()

    # 8. Repayment Cashflow Breakdown
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    cashflows = [
        ("Funded Capital", kpis["total_funded_amnt"], COLOR_PALETTE["primary"]),
        ("Principal Repaid", kpis["total_rec_prncp"], COLOR_PALETTE["secondary"]),
        ("Interest Received", kpis["total_rec_int"], COLOR_PALETTE["accent"]),
        ("Late Fees", kpis["total_rec_late_fee"], COLOR_PALETTE["warning"]),
        ("Recoveries", kpis["total_recoveries"], COLOR_PALETTE["danger"]),
        ("Outstanding Principal", kpis["total_out_prncp"], COLOR_PALETTE["neutral"])
    ]
    labels = [c[0] for c in cashflows]
    vals = [c[1] for c in cashflows]
    cols = [c[2] for c in cashflows]
    bars = ax.bar(labels, vals, color=cols, edgecolor="black", alpha=0.85)
    ax.set_title("Cumulative Portfolio Cashflows & Balance Breakdown", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Monetary Volume ($)", fontsize=11, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.xticks(rotation=25, ha="right")
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + max(vals)*0.01, format_currency(h, 0), ha="center", fontsize=8, fontweight="bold")
    plt.tight_layout()
    plt.savefig(VIS_DIR / "09_repayment_cashflows.png")
    plt.close()

    # 9. Vintage Origination & Performance Trajectory
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    ax2 = ax1.twinx()
    
    v_clean = vintage_df[(vintage_df["issue_year"] >= 2007) & (vintage_df["issue_year"] <= 2018)].sort_values("issue_year")
    ax1.bar(v_clean["issue_year"], v_clean["total_funded_amnt"], color=COLOR_PALETTE["primary"], alpha=0.7, label="Annual Funded Amount ($)")
    ax2.plot(v_clean["issue_year"], v_clean["terminal_default_rate_pct"], color=COLOR_PALETTE["danger"], marker="o", linewidth=2.5, label="Default Rate (%)")
    
    ax1.set_title("Origination Vintages (2007-2018): Funded Capital vs. Observed Default Rate", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Origination Vintage Year", fontsize=11, labelpad=10)
    ax1.set_ylabel("Annual Capital Funded ($)", fontsize=11, color=COLOR_PALETTE["primary"])
    ax2.set_ylabel("Terminal Default Rate (%)", fontsize=11, color=COLOR_PALETTE["danger"])
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    ax1.set_xticks(v_clean["issue_year"])
    
    plt.tight_layout()
    plt.savefig(VIS_DIR / "10_vintage_performance.png")
    plt.close()

    print("All visualizations generated successfully.")

if __name__ == "__main__":
    print(f"Loading cleaned dataset from {PROCESSED_DATA_PATH}...")
    df = pd.read_parquet(PROCESSED_DATA_PATH)
    print(f"Loaded {len(df):,} records. Running analysis...")
    run_portfolio_analysis(df)
