# LendingClub Loan Accepted Dataset — Data Source & Provenance

## 1. Dataset Overview

- **Dataset Name:** LendingClub Loan Accepted Dataset (2007 – 2018Q4)
- **Official Repository:** [Hugging Face: `codesignal/lending-club-loan-accepted`](https://huggingface.co/datasets/codesignal/lending-club-loan-accepted)
- **Direct Source File:** `accepted_2007_to_2018Q4.csv`
- **Authenticity Classification:** Genuine historical peer-to-peer loan records originated and published by LendingClub Corporation. No synthetic, simulated, or randomized borrower records are used.
- **File Format:** Comma-Separated Values (CSV), UTF-8 encoded
- **Original Uncompressed Size:** ~1.675 GB (1,675,133,810 bytes)
- **Total Columns:** 151 financial, credit, borrower, and repayment attributes
- **Total Historical Records:** ~2,260,701 loan listings

---

## 2. Provenance and Authenticity

LendingClub operated as a peer-to-peer (P2P) lending platform connecting retail and institutional investors with individual consumer borrowers. Between 2007 and 2020, LendingClub publicly disclosed anonymized loan-level performance data for transparency to retail investors. This dataset captures all accepted consumer loans from platform inception in 2007 through the fourth quarter of 2018 (2018Q4).

The dataset used in this project is directly downloaded from Hugging Face repository `codesignal/lending-club-loan-accepted`, preserving the historical records.

### Mandatory Compliance with Data Integrity Rules
1. **Zero Synthetic Records:** No synthetic borrowers, fake balances, or generated default labels have been introduced.
2. **Preservation of Raw Data:** The downloaded file is stored in `data/raw/` in its unmodified state.
3. **Reproducible Pipeline:** All filtering, missing value treatments, and transformations are executed programmatically via reproducible Python scripts (`src/data_download.py`, `src/data_cleaning.py`).

---

## 3. Data Schema and Key Attributes

The 151 attributes cover the full lifecycle of consumer credit:

| Category | Primary Attributes | Description |
| :--- | :--- | :--- |
| **Loan Identification** | `id`, `member_id` | Unique loan transaction identifier |
| **Origination & Terms** | `loan_amnt`, `funded_amnt`, `funded_amnt_inv`, `term`, `int_rate`, `installment`, `issue_d` | Loan principal requested, funded by investors, repayment tenure (36 or 60 months), fixed note interest rate, monthly amortized payment, and issuance date. |
| **Credit Risk & Grading** | `grade`, `sub_grade`, `fico_range_low`, `fico_range_high` | LendingClub's proprietary credit grade (A through G) and subgrade (A1 to G5), alongside credit bureau FICO score ranges. |
| **Borrower Profile** | `emp_title`, `emp_length`, `home_ownership`, `annual_inc`, `verification_status`, `dti`, `addr_state`, `purpose`, `title` | Stated employment, tenure, residential status (MORTGAGE, RENT, OWN), verified annual income, debt-to-income ratio, US state, and borrower-declared loan purpose. |
| **Credit History & Bureau** | `delinq_2yrs`, `earliest_cr_line`, `inq_last_6mths`, `open_acc`, `pub_rec`, `revol_bal`, `revol_util`, `total_acc` | 2-year delinquency count, credit age, recent credit inquiries, credit utilization, and public derogatory records. |
| **Repayment & Collections** | `loan_status`, `out_prncp`, `out_prncp_inv`, `total_pymnt`, `total_rec_prncp`, `total_rec_int`, `total_rec_late_fee`, `recoveries`, `collection_recovery_fee`, `last_pymnt_d`, `last_pymnt_amnt` | Point-in-time loan performance, remaining balance, cumulative payments received, principal vs. interest breakdown, late charges, and post-charge-off recoveries. |

---

## 4. Loan Status Classifications

The `loan_status` field reflects point-in-time terminal or performing states:
- **Fully Paid:** The borrower has satisfied all principal, interest, and applicable fees; no balance remains.
- **Current:** The loan is active, performing, and up-to-date with amortized monthly installments.
- **Charged Off:** The loan is deemed uncollectible (typically 120–150+ days delinquent) and written off as a credit loss.
- **Default:** Borrower has failed to fulfill contractual repayment terms.
- **Late (31-120 days):** Serious delinquency; loan is past due by more than one payment cycle.
- **Late (16-30 days):** Early-stage delinquency.
- **In Grace Period:** Payment is within the contractual grace period (15 days past due) prior to late fee assessment.

---

## 5. Analytical Limitations & Caveats

1. **Point-in-Time Snapshot:** The data represents loans observed through Q4 2018. It does not provide real-time updates or live bank account balances.
2. **Vintage Seasoning / Maturity:** Recent vintages (e.g., 2017–2018 60-month loans) were still active at snapshot time and had not reached full maturity. Comparing raw cumulative default rates of recent loans against seasoned 2011–2014 loans without accounting for loan age would introduce maturity bias.
3. **Survivor & Survivorship Reporting:** LendingClub accepted records only include loans that met initial underwriting thresholds. Rejected applications reside in a separate dataset.
4. **Discontinued Platform:** LendingClub ceased retail peer-to-peer origination in late 2020 following its acquisition of Radius Bank. This dataset is an empirical historical archive of retail credit performance.
