# Power BI Interactive Dashboard Construction Guide
## LendingClub Loan Portfolio & Credit Risk Analytics

This guide provides end-to-end instructions for assembling the 4-page executive and analytical Power BI report suite using the provided star schema dataset and DAX measures.

---

## 1. Visual Theme & Palette Configuration

In Power BI Desktop, navigate to **View > Themes > Customize Current Theme**:
- **Primary Color:** `#1F4E79` (Deep Banking Navy)
- **Secondary Color:** `#00A88F` (Vibrant Corporate Teal)
- **Positive / Performing:** `#2CA02C` (Credit Green)
- **Warning / Moderate Risk:** `#F0AD4E` (Amber)
- **High Risk / Charge-Off:** `#D9534F` (Crimson Red)
- **Neutral Background:** `#F8F9FA` (Soft Off-White)
- **Card Background:** `#FFFFFF` with soft 4px drop shadow
- **Font Family:** `Segoe UI Semibold` (Headers: 14pt-18pt, KPI Values: 24pt-28pt, Axis/Data Labels: 9pt-10pt)

---

## 2. Global Slicers & Filtering Pane

Place a top-bar or left-rail filter panel across all pages (or sync across pages):
1. **Origination Date Range:** Between slicer on `'Dim_Date'[Date]`
2. **Credit Grade:** Horizontal tile slicer on `'Dim_Grade'[Grade]` (A, B, C, D, E, F, G)
3. **Loan Term:** Radio selection `'Fact_Loans'[term_months]` (36 vs 60 Months)
4. **Loan Status:** Multi-select dropdown on `'Fact_Loans'[loan_status_standard]`
5. **Loan Purpose:** Dropdown search slicer on `'Dim_LoanPurpose'[PurposeName]`

---

## 3. Page 1: Executive Overview

### A. Headline KPI Banner (Top Row - 8 Cards)
| Card Label | DAX Measure | Format String |
| :--- | :--- | :--- |
| **Total Originations** | `[Total Loans]` | `#,##0` |
| **Total Capital Funded** | `[Total Funded Amount]` | `$#,##0` / `$0.00M` |
| **Outstanding Balance** | `[Total Outstanding Principal]` | `$#,##0` / `$0.00M` |
| **Payments Collected** | `[Total Payments]` | `$#,##0` / `$0.00M` |
| **Terminal Default Rate** | `[Default Rate (Closed Cohort)]` | `0.00%` |
| **Active Delinquency Rate** | `[Delinquency Rate]` | `0.00%` |
| **Weighted Avg Interest** | `[Average Interest Rate]` | `0.00%` |
| **Fully Paid Rate** | `[Fully Paid Rate]` | `0.00%` |

### B. Core Visuals Grid (2 Rows x 3 Columns)
1. **Loan Status Composition:**
   - *Visual:* Donut Chart
   - *Legend:* `'Fact_Loans'[loan_status_standard]`
   - *Values:* `[Total Loans]`
   - *Data Labels:* Category, Percent of Total
2. **Monthly Origination Trajectory:**
   - *Visual:* Line Chart
   - *X-Axis:* `'Dim_Date'[YearMonth]`
   - *Y-Axis:* `[Total Funded Amount]` (Left Axis), `[Total Loans]` (Right Secondary Axis)
3. **Capital Funded by Credit Grade:**
   - *Visual:* Clustered Bar Chart
   - *Y-Axis:* `'Dim_Grade'[Grade]`
   - *X-Axis:* `[Total Funded Amount]`
   - *Data Labels:* Currency ($M)
4. **Loan Purpose Distribution:**
   - *Visual:* Treemap
   - *Category:* `'Dim_LoanPurpose'[PurposeName]`
   - *Values:* `[Total Funded Amount]`
5. **Outstanding Principal Exposure by Grade:**
   - *Visual:* 100% Stacked Column Chart
   - *X-Axis:* `'Dim_Grade'[Grade]`
   - *Y-Axis:* `[Total Outstanding Principal]` vs `[Total Principal Recovered]`
6. **Loan Principal vs. Interest Rate Distribution:**
   - *Visual:* Scatter Plot or Grouped Column
   - *X-Axis:* `'Fact_Loans'[int_rate]` (Binned 2%)
   - *Y-Axis:* `[Average Loan Amount]`

---

## 4. Page 2: Credit Risk Analysis

### A. Risk Analysis Visuals
1. **Default Rate by Credit Grade (A to G):**
   - *Visual:* Clustered Column Chart
   - *X-Axis:* `'Dim_Grade'[Grade]`
   - *Y-Axis:* `[Default Rate (Closed Cohort)]`
   - *Conditional Formatting:* Rule-based bar colors (Green <15%, Orange 15-25%, Red >25%)
2. **Delinquency Rate by Grade (Active Loans):**
   - *Visual:* Clustered Column Chart
   - *X-Axis:* `'Dim_Grade'[Grade]`
   - *Y-Axis:* `[Delinquency Rate]`
3. **Monetary Charge-Off Rate by Loan Purpose:**
   - *Visual:* Horizontal Bar Chart (Sorted Descending)
   - *Y-Axis:* `'Dim_LoanPurpose'[PurposeName]`
   - *X-Axis:* `[Charge-Off Rate]`
4. **Risk Distribution by Loan Tenure (36 vs 60 Months):**
   - *Visual:* 100% Stacked Bar Chart
   - *Y-Axis:* `'Fact_Loans'[term_months]`
   - *Values:* Count of Fully Paid vs Default / Charged Off
5. **DTI Band vs. Default Rate:**
   - *Visual:* Line & Clustered Column Chart
   - *X-Axis:* `'Fact_Loans'[dti_bracket]` (`<10%`, `10-20%`, `20-30%`, `30%+`)
   - *Columns:* `[Total Loans]`
   - *Lines:* `[Default Rate (Closed Cohort)]`
6. **Subgrade Credit Risk Heatmap:**
   - *Visual:* Matrix
   - *Rows:* `'Dim_Grade'[Grade]`
   - *Columns:* Subgrade Number (1 to 5)
   - *Values:* `[Default Rate (Closed Cohort)]`
   - *Formatting:* Red-to-Green color scale gradient

---

## 5. Page 3: Loan Repayment Analysis

### A. Repayment KPI Summary Cards
- `[Total Payments]` ($)
- `[Total Principal Recovered]` ($)
- `[Total Interest Received]` ($)
- `[Total Recoveries]` ($)
- `[Total Late Fees]` ($)
- `[Recovery Rate]` (%)

### B. Analytical Charts
1. **Cumulative Repayment Cashflow Waterfall:**
   - *Visual:* Waterfall Chart
   - *Category:* Funded Principal -> Principal Repaid -> Interest Collected -> Late Fees -> Recoveries
2. **Repayment Performance across Origination Vintages:**
   - *Visual:* Area Chart
   - *X-Axis:* `'Dim_Date'[Year]`
   - *Values:* `[Total Principal Recovered]`, `[Total Interest Received]`
3. **Recovery Efficiency on Defaulted Portfolios:**
   - *Visual:* Scatter / Clustered Column
   - *X-Axis:* Origination Year
   - *Y-Axis:* `[Recovery Rate]` (%)
4. **Outstanding Balance Liquidation Profile:**
   - *Visual:* Stacked Area Chart over time showing balance runoff.

---

## 6. Page 4: Borrower Segmentation & Underwriting Profile

### A. Segmentation Charts
1. **Default Rate by Annual Income Tier:**
   - *Visual:* Clustered Column Chart
   - *X-Axis:* `'Fact_Loans'[income_bracket]` (`< $35K`, `$35K - $60K`, `$60K - $90K`, `$90K - $120K`, `$120K+`)
   - *Y-Axis:* `[Default Rate (Closed Cohort)]`
2. **Loan Distribution & Default Risk by Employment Tenure:**
   - *Visual:* Line & Clustered Column
   - *X-Axis:* `'Fact_Loans'[emp_length_years]` (0 to 10+ years)
   - *Columns:* `[Total Loans]`
   - *Line:* `[Default Rate (Closed Cohort)]`
3. **Credit Risk by Residential Home Ownership:**
   - *Visual:* Clustered Bar Chart
   - *Category:* `'Fact_Loans'[home_ownership]` (MORTGAGE, RENT, OWN)
   - *Values:* `[Default Rate (Closed Cohort)]` and `[Average Loan Amount]`
4. **Geographic Risk & Origination Distribution:**
   - *Visual:* Filled Map / Shape Map
   - *Location:* `'Dim_Geography'[StateCode]`
   - *Color Saturation:* `[Default Rate (Closed Cohort)]`
   - *Tooltips:* `[Total Funded Amount]`, `[Total Loans]`, `[Delinquency Rate]`
5. **Loan Purpose vs. Credit Grade Cross-Tabulation:**
   - *Visual:* Matrix with conditional data bars.

---

## 7. Interactive Drill-Through & Navigation Setup

1. **Drill-Through on Credit Grade:**
   - Right-click any Grade bar (e.g., Grade "D") -> **Drill Through to Credit Risk Detail**.
   - Target page filters automatically to Grade D subgrades (D1 to D5).
2. **Interactive Tooltips:**
   - Hovering over any chart element displays:
     - Total Originations
     - Total Funded Principal
     - Closed Cohort Default Rate
     - Delinquency Rate
3. **Sync Slicers:**
   - Ensure the Year and Grade slicers are synchronized across all four pages under **View > Sync Slicers**.
