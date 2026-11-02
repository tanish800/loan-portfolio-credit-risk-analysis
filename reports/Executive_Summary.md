# LendingClub Loan Portfolio & Credit Risk Analysis
## Executive Financial Performance, Risk Assessment & Strategic BI Deliverable

**Author:** Senior Financial Data Analyst, Risk Modeler & BI Engineer  
**Dataset Reference:** LendingClub Historical Accepted Dataset (2,260,668 Validated Loans)  
**Deliverables Suite:** Python Pipeline | Advanced Excel Financial Workbook | Power BI Star Schema & DAX | Jupyter Research Lab  

---

## 1. Project Background & Strategic Mandate

This report delivers a rigorous financial analysis of LendingClub's historical consumer credit portfolio, spanning originations from inception in 2007 through the fourth quarter of 2018. Designed to simulate institutional credit portfolio management, this project models portfolio performance, credit risk drivers, delinquency incidence, debt recovery yields, and origination vintage maturation dynamics.

Every KPI, data table, chart, and executive insight is computed from **2,260,668 authentic historical loan transactions** obtained from the official dataset repository (`codesignal/lending-club-loan-accepted`). No synthetic records or fabricated figures were introduced.

---

## 2. Headline Portfolio Performance KPIs

| Portfolio Performance Indicator | Value | Unit / Formatting | Business Significance |
| :--- | :--- | :--- | :--- |
| **Total Originated Loans** | **2,260,668** | Integer Count | Total consumer credit agreements originated |
| **Total Origination Capital Requested** | **\$34.14 Billion** | Currency ($) | Gross principal demanded by consumer applicants |
| **Total Investor Capital Funded** | **\$34.08 Billion** | Currency ($) | Total liquidity deployed by retail & institutional investors |
| **Total Outstanding Principal Balance** | **\$3.62 Billion** | Currency ($) | Active debt principal exposed to ongoing credit risk |
| **Total Payments Collected (Gross)** | **\$35.28 Billion** | Currency ($) | Cumulative gross cash inflows (Principal + Interest + Fees) |
| **Total Principal Repaid** | **\$27.42 Billion** | Currency ($) | Return of invested capital (80.5% liquidation) |
| **Total Contractual Interest Earned** | **\$7.49 Billion** | Currency ($) | Cumulative gross yield revenue generated |
| **Total Penal Late Fees Collected** | **\$38.4 Million** | Currency ($) | Penalty revenue from overdue repayment cycles |
| **Total Post-Default Recoveries** | **\$327.9 Million** | Currency ($) | Cash recouped via collections post-charge-off |
| **Weighted Average Contract Interest Rate** | **13.09%** | Percentage (APR) | Mean fixed note coupon rate across portfolio |
| **Average Funded Loan Amount** | **\$15,076** | Currency ($) | Average balance size per originated loan |
| **Average Monthly Installment** | **\$445.81** | Currency ($) | Mean amortized monthly obligation per borrower |
| **Average Contract Tenure** | **42.8 Months** | Months | Weighted average term (73% 36-mo, 27% 60-mo) |

---

## 3. Core Credit Risk & Portfolio Quality Metrics

| Credit Risk Metric | Value | Denominator Scope | Interpretation |
| :--- | :--- | :--- | :--- |
| **Terminal Default Rate (Closed Cohort)** | **19.74%** | Closed Loans ($N \approx 1.34M$) | Share of matured loan contracts terminating in Default or Charge-Off |
| **Total Portfolio Default Rate** | **11.89%** | Total Portfolio ($N = 2.26M$) | Point-in-time default share across all originated loans |
| **Active Delinquency Rate** | **2.68%** | Active Portfolio ($N \approx 917K$) | Percentage of active repayment loans currently 16 to 120 days overdue |
| **Fully Paid Rate (Closed Cohort)** | **80.26%** | Closed Loans | Percentage of matured loans paid in full with zero loss |
| **Portfolio Charge-Off Rate** | **12.44%** | Total Funded Principal | Monetary percentage of funded capital written down as credit loss |
| **Debt Recovery Rate** | **7.73%** | Charged-Off Funded Principal | Percentage of charged-off capital recovered via post-default collection |
| **Outstanding Portfolio Ratio** | **10.62%** | Total Funded Principal | Capital remaining outstanding at snapshot date |

---

## 4. Key Strategic Insights & Risk Takeaways

1. **Subprime Risk Escalation:** Default incidence scales aggressively from **6.0%** in Grade A to **49.8%** in Grade G. Although nominal interest rates in Grade G reach ~28.6%, net credit losses and high charge-off rates result in negative risk-adjusted returns for lower tiers.
2. **Tenure Maturity Gap:** 60-month loans exhibit a **32.4%** default rate compared to **16.0%** for 36-month loans—a 2.03x risk multiplier. Longer tenures dramatically expand exposure to consumer credit shocks.
3. **Refinancing Concentration:** Over 79% of all deployed capital was concentrated in Debt Consolidation ($56.8%) and Credit Card Refinance ($22.4%), making platform performance heavily dependent on macroeconomic consumer debt cycles.
4. **Depressed Unsecured Recoveries:** Recoveries on charged-off unsecured debt averaged only **7.73%**, confirming that post-charge-off collection yields are minimal. Early delinquency intervention prior to day 60 is the primary determinant of loss mitigation.

---

## 5. Technology Stack & Deliverables Overview

- **Reproducible Python Pipeline:** `main.py`, `src/data_cleaning.py`, `src/financial_metrics.py`, `src/analysis.py`.
- **Advanced Excel Financial Model:** `excel/Loan_Portfolio_Analysis.xlsx` featuring 8 structured worksheets, dynamic formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`, `IFERROR`), KPI summary cards, and native Excel charts.
- **Power BI Dimensional Suite:** Production-ready star-schema model (`Dim_Date`, `Dim_Grade`, `Dim_LoanPurpose`, `Dim_Geography`, `Fact_Loans`), accompanied by fully documented DAX measures (`DAX_Measures.md`) and a 4-page dashboard construction guide (`Dashboard_Guide.md`).
- **Jupyter Research Lab:** `notebooks/Loan_Portfolio_Exploratory_Analysis.ipynb` detailing the complete exploratory, statistical, and visual workflow.
