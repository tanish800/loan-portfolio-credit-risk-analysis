# Power BI DAX Measures Reference Guide
## Loan Portfolio & Credit Risk Analytics Engine

This document provides production-grade Data Analysis Expressions (DAX) measures developed for the **Loan Portfolio & Credit Risk Analysis** dashboard. All calculations adhere to standard financial and banking accounting standards, featuring explicit denominators, safe division (`DIVIDE`), and filter-safe aggregations.

---

## 1. Core Portfolio KPIs

### Total Loans
```dax
Total Loans = 
COUNTROWS('Fact_Loans')
```
*Description:* Total number of originated loan accounts in the selected filter context.

---

### Total Loan Amount
```dax
Total Loan Amount = 
SUM('Fact_Loans'[loan_amnt])
```
*Description:* Total principal amount requested by borrowers at origination.

---

### Total Funded Amount
```dax
Total Funded Amount = 
SUM('Fact_Loans'[funded_amnt])
```
*Description:* Total monetary capital funded by investors across the portfolio.

---

### Total Outstanding Principal
```dax
Total Outstanding Principal = 
SUM('Fact_Loans'[out_prncp])
```
*Description:* Current unpaid principal balance remaining across active loan contracts.

---

### Total Payments Received
```dax
Total Payments = 
SUM('Fact_Loans'[total_pymnt])
```
*Description:* Cumulative gross cash inflow received from borrowers (principal + interest + late fees).

---

### Total Principal Recovered
```dax
Total Principal Recovered = 
SUM('Fact_Loans'[total_rec_prncp])
```
*Description:* Cumulative loan principal repaid by borrowers to date.

---

### Total Interest Received
```dax
Total Interest Received = 
SUM('Fact_Loans'[total_rec_int])
```
*Description:* Total gross contractual interest revenue collected.

---

### Total Late Fees Received
```dax
Total Late Fees = 
SUM('Fact_Loans'[total_rec_late_fee])
```
*Description:* Cumulative penalty late charges assessed and collected.

---

### Total Recoveries
```dax
Total Recoveries = 
SUM('Fact_Loans'[recoveries])
```
*Description:* Gross post-charge-off recoveries obtained through internal collections or third-party debt recovery agencies.

---

### Average Loan Amount
```dax
Average Loan Amount = 
AVERAGE('Fact_Loans'[loan_amnt])
```
*Description:* Mean principal size per loan listing.

---

### Average Interest Rate
```dax
Average Interest Rate = 
DIVIDE(
    AVERAGE('Fact_Loans'[int_rate]),
    100,
    0
)
```
*Description:* Mean contractual interest rate, formatted as a percentage.

---

### Average Monthly Installment
```dax
Average Monthly Installment = 
AVERAGE('Fact_Loans'[installment])
```
*Description:* Mean monthly amortized obligation due from borrowers.

---

## 2. Loan Status & Volume Counts

### Fully Paid Loans Count
```dax
Fully Paid Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] = "Fully Paid"
)
```

### Charged-Off Loans Count
```dax
Charged-Off Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] = "Charged Off"
)
```

### Defaulted Loans Count
```dax
Defaulted Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] = "Default"
)
```

### Current Performing Loans Count
```dax
Current Performing Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] = "Current"
)
```

### Current Late Loans Count
```dax
Current Late Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] IN {"Late (31-120 days)", "Late (16-30 days)"}
)
```

### In Grace Period Loans Count
```dax
In Grace Period Loans = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] = "In Grace Period"
)
```

### Closed Loans Count (Matured Population)
```dax
Closed Loans Count = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] IN {"Fully Paid", "Charged Off", "Default"}
)
```

### Active Loans Count (Performing & Delinquent)
```dax
Active Loans Count = 
CALCULATE(
    COUNTROWS('Fact_Loans'),
    'Fact_Loans'[loan_status_standard] IN {"Current", "Late (31-120 days)", "Late (16-30 days)", "In Grace Period"}
)
```

---

## 3. Financial & Credit Risk Ratios

### Terminal Default Rate (%)
```dax
Default Rate (Closed Cohort) = 
VAR BadLoans = [Charged-Off Loans] + [Defaulted Loans]
VAR ClosedLoans = [Closed Loans Count]
RETURN
DIVIDE(BadLoans, ClosedLoans, 0)
```
*Methodology Note:* Measures credit failure within the population of loans that have reached a definitive terminal resolution (`Fully Paid`, `Charged Off`, or `Default`). This eliminates censoring bias from recently originated performing loans.

---

### Portfolio Default Rate (%)
```dax
Default Rate (Total Portfolio) = 
VAR BadLoans = [Charged-Off Loans] + [Defaulted Loans]
VAR TotalPortfolio = [Total Loans]
RETURN
DIVIDE(BadLoans, TotalPortfolio, 0)
```
*Methodology Note:* Point-in-time default rate across the entire originated portfolio.

---

### Active Delinquency Rate (%)
```dax
Delinquency Rate = 
VAR LateLoans = [Current Late Loans]
VAR ActivePortfolio = [Active Loans Count]
RETURN
DIVIDE(LateLoans, ActivePortfolio, 0)
```
*Methodology Note:* Measures the share of active repayment obligations currently overdue (16–120 days) relative to all active performing accounts.

---

### Fully Paid Rate (%)
```dax
Fully Paid Rate = 
DIVIDE([Fully Paid Loans], [Closed Loans Count], 0)
```

---

### Charge-Off Rate (Monetary Principal Basis)
```dax
Charge-Off Rate = 
VAR ChargedOffFunded = 
    CALCULATE(
        SUM('Fact_Loans'[funded_amnt]),
        'Fact_Loans'[loan_status_standard] IN {"Charged Off", "Default"}
    )
VAR TotalFunded = [Total Funded Amount]
RETURN
DIVIDE(ChargedOffFunded, TotalFunded, 0)
```
*Methodology Note:* Monetary percentage of total funded capital that resulted in a contractual charge-off write-down.

---

### Recovery Rate (%)
```dax
Recovery Rate = 
VAR GrossRecoveries = [Total Recoveries]
VAR ChargedOffFunded = 
    CALCULATE(
        SUM('Fact_Loans'[funded_amnt]),
        'Fact_Loans'[loan_status_standard] IN {"Charged Off", "Default"}
    )
RETURN
DIVIDE(GrossRecoveries, ChargedOffFunded, 0)
```
*Methodology Note:* Proportion of charged-off principal recouped via post-default recovery collections.

---

### Outstanding Portfolio Ratio (%)
```dax
Outstanding Portfolio Ratio = 
DIVIDE([Total Outstanding Principal], [Total Funded Amount], 0)
```
*Methodology Note:* Percentage of origination capital currently outstanding and exposed to credit risk.

---

## 4. Page-Specific Dynamic Measures

### Page 1 Title (Dynamic Filter Context)
```dax
Dynamic Header Page 1 = 
"Executive Portfolio Overview | " & 
IF(
    ISFILTERED('Dim_Grade'[grade]),
    "Grade: " & SELECTEDVALUE('Dim_Grade'[grade]),
    "All Grades"
) & " | Vintages: " & 
IF(
    ISFILTERED('Dim_Date'[issue_year]),
    CONCATENATEX(VALUES('Dim_Date'[issue_year]), 'Dim_Date'[issue_year], ", "),
    "2007 - 2018"
)
```

### Risk Severity Indicator (Conditional Formatting)
```dax
Risk Color Code = 
SWITCH(
    TRUE(),
    [Default Rate (Closed Cohort)] >= 0.25, "#d9534f",  -- High Risk Red
    [Default Rate (Closed Cohort)] >= 0.15, "#f0ad4e",  -- Moderate Warning Amber
    "#2ca02c"                                          -- Healthy Green
)
```
