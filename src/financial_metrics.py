"""
Financial metrics calculation engine for Loan Portfolio & Credit Risk Analysis.
Implements banking standard credit risk, portfolio performance, repayment,
and cohort/vintage analytics with zero division-by-zero errors.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

def calculate_portfolio_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate headline portfolio performance KPIs.
    Guarantees no double-counting and proper financial domain integrity.
    """
    total_loans = int(len(df))
    if total_loans == 0:
        return {}

    total_loan_amnt = float(df["loan_amnt"].sum())
    total_funded_amnt = float(df["funded_amnt"].sum())
    total_out_prncp = float(df["out_prncp"].sum()) if "out_prncp" in df.columns else 0.0
    total_pymnt = float(df["total_pymnt"].sum()) if "total_pymnt" in df.columns else 0.0
    total_rec_prncp = float(df["total_rec_prncp"].sum()) if "total_rec_prncp" in df.columns else 0.0
    total_rec_int = float(df["total_rec_int"].sum()) if "total_rec_int" in df.columns else 0.0
    total_rec_late_fee = float(df["total_rec_late_fee"].sum()) if "total_rec_late_fee" in df.columns else 0.0
    total_recoveries = float(df["recoveries"].sum()) if "recoveries" in df.columns else 0.0

    avg_loan_amnt = float(df["loan_amnt"].mean())
    avg_funded_amnt = float(df["funded_amnt"].mean())
    avg_int_rate = float(df["int_rate"].mean())
    avg_installment = float(df["installment"].mean()) if "installment" in df.columns else 0.0
    
    avg_tenure = float(df["term_months"].mean()) if "term_months" in df.columns else 36.0

    # Categorical counts
    status_counts = df["loan_status_standard"].value_counts().to_dict() if "loan_status_standard" in df.columns else {}
    
    fully_paid_count = int(status_counts.get("Fully Paid", 0))
    charged_off_count = int(status_counts.get("Charged Off", 0))
    default_count = int(status_counts.get("Default", 0))
    current_count = int(status_counts.get("Current", 0))
    late_31_120_count = int(status_counts.get("Late (31-120 days)", 0))
    late_16_30_count = int(status_counts.get("Late (16-30 days)", 0))
    in_grace_count = int(status_counts.get("In Grace Period", 0))

    active_late_count = late_31_120_count + late_16_30_count
    total_bad_loans = charged_off_count + default_count

    # 1. Closed/Matured Loans Cohort (for terminal Default Rate)
    closed_loans_count = fully_paid_count + total_bad_loans
    terminal_default_rate = (total_bad_loans / closed_loans_count * 100) if closed_loans_count > 0 else 0.0
    
    # 2. Portfolio Default Rate (total portfolio basis)
    portfolio_default_rate = (total_bad_loans / total_loans * 100) if total_loans > 0 else 0.0

    # 3. Delinquency Rate (Active performing & delinquent population basis)
    active_loans_count = current_count + active_late_count + in_grace_count
    delinquency_rate_active = (active_late_count / active_loans_count * 100) if active_loans_count > 0 else 0.0
    delinquency_rate_portfolio = (active_late_count / total_loans * 100) if total_loans > 0 else 0.0

    # 4. Fully Paid Rate
    fully_paid_rate_closed = (fully_paid_count / closed_loans_count * 100) if closed_loans_count > 0 else 0.0
    fully_paid_rate_portfolio = (fully_paid_count / total_loans * 100) if total_loans > 0 else 0.0

    # 5. Monetary Charge-off and Recovery Rates
    co_filter = df["loan_status_standard"].isin(["Charged Off", "Default"]) if "loan_status_standard" in df.columns else pd.Series(False, index=df.index)
    charged_off_funded = float(df.loc[co_filter, "funded_amnt"].sum())
    charge_off_rate_portfolio = (charged_off_funded / total_funded_amnt * 100) if total_funded_amnt > 0 else 0.0
    
    recovery_rate = (total_recoveries / charged_off_funded * 100) if charged_off_funded > 0 else 0.0
    outstanding_ratio = (total_out_prncp / total_funded_amnt * 100) if total_funded_amnt > 0 else 0.0

    return {
        "total_loans": total_loans,
        "total_loan_amnt": total_loan_amnt,
        "total_funded_amnt": total_funded_amnt,
        "total_out_prncp": total_out_prncp,
        "total_pymnt": total_pymnt,
        "total_rec_prncp": total_rec_prncp,
        "total_rec_int": total_rec_int,
        "total_rec_late_fee": total_rec_late_fee,
        "total_recoveries": total_recoveries,
        "avg_loan_amnt": avg_loan_amnt,
        "avg_funded_amnt": avg_funded_amnt,
        "avg_int_rate": avg_int_rate,
        "avg_installment": avg_installment,
        "avg_tenure_months": avg_tenure,
        "fully_paid_count": fully_paid_count,
        "current_count": current_count,
        "charged_off_count": charged_off_count,
        "default_count": default_count,
        "late_loans_count": active_late_count,
        "in_grace_period_count": in_grace_count,
        "active_loans_count": active_loans_count,
        "closed_loans_count": closed_loans_count,
        "terminal_default_rate_pct": round(terminal_default_rate, 2),
        "portfolio_default_rate_pct": round(portfolio_default_rate, 2),
        "delinquency_rate_active_pct": round(delinquency_rate_active, 2),
        "delinquency_rate_portfolio_pct": round(delinquency_rate_portfolio, 2),
        "fully_paid_rate_closed_pct": round(fully_paid_rate_closed, 2),
        "fully_paid_rate_portfolio_pct": round(fully_paid_rate_portfolio, 2),
        "charged_off_funded_amnt": charged_off_funded,
        "charge_off_rate_pct": round(charge_off_rate_portfolio, 2),
        "recovery_rate_pct": round(recovery_rate, 2),
        "outstanding_portfolio_ratio_pct": round(outstanding_ratio, 2)
    }

def analyze_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Compute financial and credit risk metrics aggregated by a specific dimension
    (e.g., grade, sub_grade, purpose, home_ownership, term_months, income_band, dti_band).
    """
    if dimension not in df.columns:
        raise ValueError(f"Dimension '{dimension}' not found in dataframe columns.")

    def agg_funcs(group):
        n = len(group)
        funded = group["funded_amnt"].sum()
        out_prn = group["out_prncp"].sum() if "out_prncp" in group.columns else 0.0
        pymnt = group["total_pymnt"].sum() if "total_pymnt" in group.columns else 0.0
        rec_prn = group["total_rec_prncp"].sum() if "total_rec_prncp" in group.columns else 0.0
        rec_int = group["total_rec_int"].sum() if "total_rec_int" in group.columns else 0.0
        recoveries = group["recoveries"].sum() if "recoveries" in group.columns else 0.0

        fp_count = (group["loan_status_standard"] == "Fully Paid").sum()
        co_count = (group["loan_status_standard"] == "Charged Off").sum()
        df_count = (group["loan_status_standard"] == "Default").sum()
        curr_count = (group["loan_status_standard"] == "Current").sum()
        late_count = group["loan_status_standard"].isin(["Late (31-120 days)", "Late (16-30 days)"]).sum()

        bad_count = co_count + df_count
        closed_count = fp_count + bad_count
        active_count = curr_count + late_count + (group["loan_status_standard"] == "In Grace Period").sum()

        co_funded = group.loc[group["loan_status_standard"].isin(["Charged Off", "Default"]), "funded_amnt"].sum()

        return pd.Series({
            "total_loans": n,
            "total_funded_amnt": funded,
            "avg_loan_amnt": group["loan_amnt"].mean(),
            "avg_int_rate": group["int_rate"].mean(),
            "total_out_prncp": out_prn,
            "total_pymnt": pymnt,
            "total_rec_prncp": rec_prn,
            "total_rec_int": rec_int,
            "total_recoveries": recoveries,
            "fully_paid_loans": fp_count,
            "charged_off_loans": co_count,
            "default_loans": df_count,
            "current_loans": curr_count,
            "late_loans": late_count,
            "portfolio_share_pct": round(n / len(df) * 100, 2),
            "terminal_default_rate_pct": round((bad_count / closed_count * 100) if closed_count > 0 else 0.0, 2),
            "portfolio_default_rate_pct": round((bad_count / n * 100) if n > 0 else 0.0, 2),
            "delinquency_rate_pct": round((late_count / active_count * 100) if active_count > 0 else 0.0, 2),
            "charge_off_rate_pct": round((co_funded / funded * 100) if funded > 0 else 0.0, 2),
            "recovery_rate_pct": round((recoveries / co_funded * 100) if co_funded > 0 else 0.0, 2),
            "outstanding_ratio_pct": round((out_prn / funded * 100) if funded > 0 else 0.0, 2)
        })

    result = df.groupby(dimension, observed=True).apply(agg_funcs, include_groups=False).reset_index()
    return result

def analyze_vintages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Origination vintage cohort analysis (by issue_year and issue_month).
    """
    if "issue_year" not in df.columns:
        raise ValueError("issue_year column required for vintage analysis.")
        
    vintage_df = analyze_by_dimension(df, "issue_year")
    return vintage_df.sort_values("issue_year")
