"""
Advanced Excel Workbook Generator for Loan Portfolio & Credit Risk Analysis.
Creates 'Loan_Portfolio_Analysis.xlsx' with 8 distinct analytical worksheets,
live Excel formulas (SUMIFS, COUNTIFS, AVERAGEIFS, IFERROR),
KPI summary cards, and native Excel charts.
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import (
    EXCEL_DIR,
    METADATA_DIR,
    PROCESSED_DATA_PATH,
    PROCESSED_CSV_PATH,
    RAW_DATA_PATH
)

# Professional Palette
COLOR_NAVY_DARK = "1F4E79"
COLOR_NAVY_LIGHT = "2C3E50"
COLOR_TEAL = "00A88F"
COLOR_WHITE = "FFFFFF"
COLOR_GRAY_LIGHT = "F4F6F7"
COLOR_GRAY_BORDER = "D5D8DC"
COLOR_RED_SOFT = "FDEDEC"
COLOR_GREEN_SOFT = "EAFAF1"
COLOR_AMBER_SOFT = "FEF9E7"

font_title = Font(name="Segoe UI", size=16, bold=True, color=COLOR_WHITE)
font_subtitle = Font(name="Segoe UI", size=11, italic=True, color=COLOR_WHITE)
font_sec_header = Font(name="Segoe UI", size=12, bold=True, color=COLOR_NAVY_DARK)
font_tbl_header = Font(name="Segoe UI", size=10, bold=True, color=COLOR_WHITE)
font_kpi_num = Font(name="Segoe UI", size=16, bold=True, color=COLOR_NAVY_DARK)
font_kpi_lbl = Font(name="Segoe UI", size=9, bold=True, color="566573")
font_data = Font(name="Segoe UI", size=10)
font_total = Font(name="Segoe UI", size=10, bold=True, color=COLOR_NAVY_DARK)

fill_navy_dark = PatternFill(start_color=COLOR_NAVY_DARK, end_color=COLOR_NAVY_DARK, fill_type="solid")
fill_navy_light = PatternFill(start_color=COLOR_NAVY_LIGHT, end_color=COLOR_NAVY_LIGHT, fill_type="solid")
fill_teal = PatternFill(start_color=COLOR_TEAL, end_color=COLOR_TEAL, fill_type="solid")
fill_gray_light = PatternFill(start_color=COLOR_GRAY_LIGHT, end_color=COLOR_GRAY_LIGHT, fill_type="solid")
fill_kpi_card = PatternFill(start_color="F8F9F9", end_color="F8F9F9", fill_type="solid")

thin_border_side = Side(border_style="thin", color=COLOR_GRAY_BORDER)
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
border_total = Border(top=Side(border_style="thin", color=COLOR_NAVY_DARK), bottom=Side(border_style="double", color=COLOR_NAVY_DARK))

def apply_title_banner(ws, title: str, subtitle: str, max_col: int = 12):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
    cell = ws.cell(row=1, column=1, value=title)
    cell.font = font_title
    cell.fill = fill_navy_dark
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)
    cell2 = ws.cell(row=2, column=1, value=subtitle)
    cell2.font = font_subtitle
    cell2.fill = fill_navy_light
    cell2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

def create_kpi_card(ws, start_row: int, start_col: int, label: str, value_formula: str, num_format: str):
    # Card spans 2 rows x 2 cols
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=start_col + 1)
    lbl_cell = ws.cell(row=start_row, column=start_col, value=label)
    lbl_cell.font = font_kpi_lbl
    lbl_cell.fill = fill_kpi_card
    lbl_cell.alignment = Alignment(horizontal="center", vertical="center")

    ws.merge_cells(start_row=start_row + 1, start_column=start_col, end_row=start_row + 1, end_column=start_col + 1)
    val_cell = ws.cell(row=start_row + 1, column=start_col, value=value_formula)
    val_cell.font = font_kpi_num
    val_cell.fill = fill_kpi_card
    val_cell.alignment = Alignment(horizontal="center", vertical="center")
    val_cell.number_format = num_format

    for r in range(start_row, start_row + 2):
        for c in range(start_col, start_col + 2):
            ws.cell(row=r, column=c).border = border_cell

def build_excel_workbook():
    """Assemble all 8 worksheets and output the production workbook."""
    EXCEL_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EXCEL_DIR / "Loan_Portfolio_Analysis.xlsx"
    print(f"Generating Excel workbook: {out_file}...")

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # 1. Load summary metrics data from CSVs
    grade_df = pd.read_csv(METADATA_DIR / "summary_grade.csv") if (METADATA_DIR / "summary_grade.csv").exists() else None
    purpose_df = pd.read_csv(METADATA_DIR / "summary_purpose.csv") if (METADATA_DIR / "summary_purpose.csv").exists() else None
    term_df = pd.read_csv(METADATA_DIR / "summary_term.csv") if (METADATA_DIR / "summary_term.csv").exists() else None
    vintage_df = pd.read_csv(METADATA_DIR / "summary_vintage.csv") if (METADATA_DIR / "summary_vintage.csv").exists() else None
    income_df = pd.read_csv(METADATA_DIR / "summary_income.csv") if (METADATA_DIR / "summary_income.csv").exists() else None
    dti_df = pd.read_csv(METADATA_DIR / "summary_dti.csv") if (METADATA_DIR / "summary_dti.csv").exists() else None
    home_df = pd.read_csv(METADATA_DIR / "summary_home.csv") if (METADATA_DIR / "summary_home.csv").exists() else None

    # Load representative cleaned sample (15,000 records for Excel interactive tables)
    sample_df = None
    if PROCESSED_DATA_PATH.exists():
        full_df = pd.read_parquet(PROCESSED_DATA_PATH)
        sample_df = full_df.sample(n=min(15000, len(full_df)), random_state=42)
    elif PROCESSED_CSV_PATH.exists():
        sample_df = pd.read_csv(PROCESSED_CSV_PATH, nrows=15000)

    # Sheet 1: Executive Dashboard
    ws_dash = wb.create_sheet(title="Executive Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_dash, "LENDINGCLUB PORTFOLIO & CREDIT RISK EXECUTIVE DASHBOARD", "Executive Performance, Liquidity, and Delinquency Analysis (Authentic LendingClub Archive)", max_col=14)

    # Top KPI Cards (Row 4-5)
    create_kpi_card(ws_dash, 4, 1, "TOTAL CAPITAL FUNDED", "=SUM('Portfolio Analysis'!C12:C18)", "$#,##0")
    create_kpi_card(ws_dash, 4, 3, "TOTAL LOAN ACCOUNTS", "=SUM('Portfolio Analysis'!B12:B18)", "#,##0")
    create_kpi_card(ws_dash, 4, 5, "OUTSTANDING BALANCE", "=SUM('Portfolio Analysis'!D12:D18)", "$#,##0")
    create_kpi_card(ws_dash, 4, 7, "TOTAL PAYMENTS COLLECTED", "=SUM('Portfolio Analysis'!E12:E18)", "$#,##0")
    create_kpi_card(ws_dash, 4, 9, "CLOSED DEFAULT RATE", "='Credit Risk Analysis'!F14", "0.00%")
    create_kpi_card(ws_dash, 4, 11, "ACTIVE DELINQUENCY RATE", "='Credit Risk Analysis'!G14", "0.00%")
    create_kpi_card(ws_dash, 4, 13, "PORTFOLIO CHARGE-OFF RATE", "='Credit Risk Analysis'!H14", "0.00%")

    # Add summary tables for Dashboard Charts
    # Status Breakdown Table
    ws_dash.cell(row=7, column=1, value="Portfolio Composition by Loan Status").font = font_sec_header
    headers_status = ["Loan Status", "Account Count", "Capital Funded ($)", "Share (%)"]
    for c_idx, h in enumerate(headers_status, start=1):
        cell = ws_dash.cell(row=8, column=c_idx, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark
        cell.alignment = Alignment(horizontal="center")

    statuses = [
        ("Fully Paid", "='Portfolio Analysis'!B12", "='Portfolio Analysis'!C12"),
        ("Current", "='Portfolio Analysis'!B13", "='Portfolio Analysis'!C13"),
        ("Charged Off", "='Portfolio Analysis'!B14", "='Portfolio Analysis'!C14"),
        ("Late (31-120 days)", "='Portfolio Analysis'!B15", "='Portfolio Analysis'!C15"),
        ("Late (16-30 days)", "='Portfolio Analysis'!B16", "='Portfolio Analysis'!C16"),
        ("In Grace Period", "='Portfolio Analysis'!B17", "='Portfolio Analysis'!C17"),
        ("Default", "='Portfolio Analysis'!B18", "='Portfolio Analysis'!C18")
    ]
    for r_idx, (st, cnt_ref, fnd_ref) in enumerate(statuses, start=9):
        ws_dash.cell(row=r_idx, column=1, value=st).font = font_data
        ws_dash.cell(row=r_idx, column=2, value=cnt_ref).number_format = "#,##0"
        ws_dash.cell(row=r_idx, column=3, value=fnd_ref).number_format = "$#,##0"
        ws_dash.cell(row=r_idx, column=4, value=f"=IFERROR(B{r_idx}/$B$16, 0)").number_format = "0.00%"
        for c in range(1, 5):
            ws_dash.cell(row=r_idx, column=c).border = border_cell

    # Total row
    ws_dash.cell(row=16, column=1, value="Total Portfolio").font = font_total
    ws_dash.cell(row=16, column=2, value="=SUM(B9:B15)").font = font_total
    ws_dash.cell(row=16, column=2).number_format = "#,##0"
    ws_dash.cell(row=16, column=3, value="=SUM(C9:C15)").font = font_total
    ws_dash.cell(row=16, column=3).number_format = "$#,##0"
    ws_dash.cell(row=16, column=4, value="=SUM(D9:D15)").font = font_total
    ws_dash.cell(row=16, column=4).number_format = "0.00%"
    for c in range(1, 5):
        ws_dash.cell(row=16, column=c).border = border_total

    # Grade Risk Table on Dashboard
    ws_dash.cell(row=7, column=6, value="Credit Grade Risk & Pricing Matrix").font = font_sec_header
    headers_grd = ["Grade", "Funded Amount ($)", "Avg Interest", "Default Rate (%)"]
    for c_idx, h in enumerate(headers_grd, start=6):
        cell = ws_dash.cell(row=8, column=c_idx, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark
        cell.alignment = Alignment(horizontal="center")

    for idx, gr in enumerate(["A", "B", "C", "D", "E", "F", "G"], start=9):
        gr_row = 6 + (idx - 9)
        ws_dash.cell(row=idx, column=6, value=gr).font = font_data
        ws_dash.cell(row=idx, column=7, value=f"='Credit Risk Analysis'!C{gr_row}").number_format = "$#,##0"
        ws_dash.cell(row=idx, column=8, value=f"='Credit Risk Analysis'!E{gr_row}").number_format = "0.00%"
        ws_dash.cell(row=idx, column=9, value=f"='Credit Risk Analysis'!F{gr_row}").number_format = "0.00%"
        for c in range(6, 10):
            ws_dash.cell(row=idx, column=c).border = border_cell

    # Native Excel Chart 1: Status Distribution
    chart1 = BarChart()
    chart1.type = "col"
    chart1.style = 10
    chart1.title = "Loan Account Volume by Status"
    chart1.y_axis.title = "Number of Loans"
    chart1.x_axis.title = "Loan Status"
    data1 = Reference(ws_dash, min_col=2, min_row=8, max_row=15)
    cats1 = Reference(ws_dash, min_col=1, min_row=9, max_row=15)
    chart1.add_data(data1, titles_from_data=True)
    chart1.set_categories(cats1)
    chart1.legend = None
    chart1.width = 16
    chart1.height = 9
    ws_dash.add_chart(chart1, "A18")

    # Native Excel Chart 2: Grade Default Rate
    chart2 = BarChart()
    chart2.type = "col"
    chart2.style = 11
    chart2.title = "Default Rate by Credit Grade (A to G)"
    chart2.y_axis.title = "Closed Default Rate (%)"
    chart2.x_axis.title = "Credit Grade"
    data2 = Reference(ws_dash, min_col=9, min_row=8, max_row=15)
    cats2 = Reference(ws_dash, min_col=6, min_row=9, max_row=15)
    chart2.add_data(data2, titles_from_data=True)
    chart2.set_categories(cats2)
    chart2.legend = None
    chart2.width = 16
    chart2.height = 9
    ws_dash.add_chart(chart2, "H18")

    # Sheet 2: Raw Data (Schema & Extract Information)
    ws_raw = wb.create_sheet(title="Raw Data")
    ws_raw.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_raw, "RAW DATASET PROVENANCE & SCHEMA DIRECTORY", "Authentic LendingClub Loan Accepted Dataset (codesignal/lending-club-loan-accepted)", max_col=8)

    raw_meta_rows = [
        ("Dataset Repository", "codesignal/lending-club-loan-accepted"),
        ("Source URL", "https://huggingface.co/datasets/codesignal/lending-club-loan-accepted"),
        ("Raw File Name", "accepted_2007_to_2018Q4.csv"),
        ("Original Uncompressed Size", "1,675,133,810 bytes (~1.675 GB)"),
        ("Total Original Columns", "151 attributes"),
        ("Historical Record Scope", "2007 - 2018 Q4 (Origination to Terminal/Active states)"),
        ("Authenticity Status", "Authentic historical records from LendingClub Corporation. Zero synthetic rows.")
    ]
    ws_raw.cell(row=4, column=1, value="Dataset Provenance Specification").font = font_sec_header
    for r_i, (k, v) in enumerate(raw_meta_rows, start=5):
        c1 = ws_raw.cell(row=r_i, column=1, value=k)
        c1.font = font_tbl_header
        c1.fill = fill_navy_light
        c2 = ws_raw.cell(row=r_i, column=2, value=v)
        c2.font = font_data
        c1.border = border_cell
        c2.border = border_cell

    # Sheet 3: Cleaned Data
    ws_clean = wb.create_sheet(title="Cleaned Data")
    ws_clean.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_clean, "CLEANED LOAN PORTFOLIO EXTRACT", "Validated, Standardized Financial Records (Reference Data for Excel Formulas)", max_col=16)

    clean_cols = [
        "id", "loan_amnt", "funded_amnt", "term_months", "int_rate", "installment",
        "grade", "sub_grade", "emp_length_years", "home_ownership", "annual_inc",
        "loan_status_standard", "issue_year", "purpose", "dti", "out_prncp",
        "total_pymnt", "total_rec_prncp", "total_rec_int", "total_rec_late_fee", "recoveries"
    ]
    for c_idx, col_name in enumerate(clean_cols, start=1):
        cell = ws_clean.cell(row=4, column=c_idx, value=col_name)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark
        cell.alignment = Alignment(horizontal="center")

    if sample_df is not None:
        sub_sample = sample_df[[c for c in clean_cols if c in sample_df.columns]].copy()
        for r_i, row in enumerate(sub_sample.itertuples(index=False), start=5):
            for c_i, val in enumerate(row, start=1):
                cell = ws_clean.cell(row=r_i, column=c_i, value=val if not pd.isna(val) else "")
                cell.font = font_data
                cell.border = border_cell
                # Currency format
                if c_i in [2, 3, 6, 11, 16, 17, 18, 19, 20, 21]:
                    cell.number_format = "$#,##0"
                elif c_i in [5, 15]:
                    cell.number_format = "0.00"

    # Sheet 4: Portfolio Analysis
    ws_port = wb.create_sheet(title="Portfolio Analysis")
    ws_port.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_port, "PORTFOLIO PERFORMANCE & CASHFLOW ANALYSIS", "Origination Capital, Repayment Distribution, and Principal Runoff", max_col=10)

    ws_port.cell(row=4, column=1, value="Core Portfolio Financial Formulas").font = font_sec_header
    port_headers = ["Status Category", "Loan Count", "Funded Principal ($)", "Outstanding Balance ($)", "Payments Received ($)", "Principal Repaid ($)", "Interest Collected ($)", "Late Fees ($)", "Recoveries ($)"]
    for c_idx, h in enumerate(port_headers, start=1):
        cell = ws_port.cell(row=5, column=c_idx, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark

    # Formulaic rows targeting Cleaned Data
    formula_statuses = [
        ("Fully Paid", 12),
        ("Current", 13),
        ("Charged Off", 14),
        ("Late (31-120 days)", 15),
        ("Late (16-30 days)", 16),
        ("In Grace Period", 17),
        ("Default", 18)
    ]
    for st, r_num in formula_statuses:
        ws_port.cell(row=r_num, column=1, value=st).font = font_data
        ws_port.cell(row=r_num, column=2, value=f'=COUNTIF(\'Cleaned Data\'!$L:$L, "{st}")').number_format = "#,##0"
        ws_port.cell(row=r_num, column=3, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$C:$C)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=4, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$P:$P)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=5, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$Q:$Q)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=6, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$R:$R)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=7, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$S:$S)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=8, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$T:$T)').number_format = "$#,##0"
        ws_port.cell(row=r_num, column=9, value=f'=SUMIF(\'Cleaned Data\'!$L:$L, "{st}", \'Cleaned Data\'!$U:$U)').number_format = "$#,##0"
        for c in range(1, 10):
            ws_port.cell(row=r_num, column=c).border = border_cell

    # Total row
    ws_port.cell(row=19, column=1, value="Total Portfolio").font = font_total
    for c in range(2, 10):
        col_let = get_column_letter(c)
        cell = ws_port.cell(row=19, column=c, value=f"=SUM({col_let}12:{col_let}18)")
        cell.font = font_total
        cell.border = border_total
        cell.number_format = "#,##0" if c == 2 else "$#,##0"

    # Sheet 5: Credit Risk Analysis
    ws_risk = wb.create_sheet(title="Credit Risk Analysis")
    ws_risk.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_risk, "CREDIT RISK & DEFAULT ANALYSIS BY GRADE", "Empirical Default Rates, Active Delinquency, and Charge-Off Severity", max_col=10)

    risk_headers = ["Credit Grade", "Total Loans", "Funded Amount ($)", "Avg Loan ($)", "Avg Int Rate (%)", "Closed Default Rate (%)", "Delinquency Rate (%)", "Charge-Off Rate (%)", "Recovery Rate (%)"]
    for c_idx, h in enumerate(risk_headers, start=1):
        cell = ws_risk.cell(row=5, column=c_idx, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark

    for idx, gr in enumerate(["A", "B", "C", "D", "E", "F", "G"], start=6):
        ws_risk.cell(row=idx, column=1, value=gr).font = font_data
        ws_risk.cell(row=idx, column=2, value=f'=COUNTIF(\'Cleaned Data\'!$G:$G, "{gr}")').number_format = "#,##0"
        ws_risk.cell(row=idx, column=3, value=f'=SUMIF(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$C:$C)').number_format = "$#,##0"
        ws_risk.cell(row=idx, column=4, value=f"=IFERROR(C{idx}/B{idx}, 0)").number_format = "$#,##0"
        ws_risk.cell(row=idx, column=5, value=f'=AVERAGEIF(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$E:$E)/100').number_format = "0.00%"
        # Closed Default Rate = Bad Loans / Closed Loans
        bad_f = f'(COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Charged Off") + COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Default"))'
        closed_f = f'(COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Fully Paid") + {bad_f})'
        ws_risk.cell(row=idx, column=6, value=f"=IFERROR({bad_f}/{closed_f}, 0)").number_format = "0.00%"
        # Delinquency Rate = Late Loans / Active Loans
        late_f = f'(COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Late (31-120 days)") + COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Late (16-30 days)"))'
        active_f = f'(COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Current") + {late_f} + COUNTIFS(\'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "In Grace Period"))'
        ws_risk.cell(row=idx, column=7, value=f"=IFERROR({late_f}/{active_f}, 0)").number_format = "0.00%"
        # Charge-Off Rate = Charged-off funded / Total funded
        co_fnd = f'SUMIFS(\'Cleaned Data\'!$C:$C, \'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Charged Off")'
        ws_risk.cell(row=idx, column=8, value=f"=IFERROR({co_fnd}/C{idx}, 0)").number_format = "0.00%"
        # Recovery Rate = Recoveries / Charged-off funded
        rec_f = f'SUMIFS(\'Cleaned Data\'!$U:$U, \'Cleaned Data\'!$G:$G, "{gr}", \'Cleaned Data\'!$L:$L, "Charged Off")'
        ws_risk.cell(row=idx, column=9, value=f"=IFERROR({rec_f}/{co_fnd}, 0)").number_format = "0.00%"

        for c in range(1, 10):
            ws_risk.cell(row=idx, column=c).border = border_cell

    # Total Row for Risk
    ws_risk.cell(row=14, column=1, value="Portfolio Weighted").font = font_total
    ws_risk.cell(row=14, column=2, value="=SUM(B6:B12)").font = font_total
    ws_risk.cell(row=14, column=2).number_format = "#,##0"
    ws_risk.cell(row=14, column=3, value="=SUM(C6:C12)").font = font_total
    ws_risk.cell(row=14, column=3).number_format = "$#,##0"
    ws_risk.cell(row=14, column=4, value="=IFERROR(C14/B14, 0)").font = font_total
    ws_risk.cell(row=14, column=4).number_format = "$#,##0"
    ws_risk.cell(row=14, column=5, value="=AVERAGE('Cleaned Data'!$E:$E)/100").font = font_total
    ws_risk.cell(row=14, column=5).number_format = "0.00%"
    # Portfolio total default rate
    ws_risk.cell(row=14, column=6, value="=IFERROR((COUNTIF('Cleaned Data'!$L:$L, \"Charged Off\")+COUNTIF('Cleaned Data'!$L:$L, \"Default\"))/(COUNTIF('Cleaned Data'!$L:$L, \"Fully Paid\")+COUNTIF('Cleaned Data'!$L:$L, \"Charged Off\")+COUNTIF('Cleaned Data'!$L:$L, \"Default\")), 0)").font = font_total
    ws_risk.cell(row=14, column=6).number_format = "0.00%"
    ws_risk.cell(row=14, column=7, value="=IFERROR((COUNTIF('Cleaned Data'!$L:$L, \"Late (31-120 days)\")+COUNTIF('Cleaned Data'!$L:$L, \"Late (16-30 days)\"))/(COUNTIF('Cleaned Data'!$L:$L, \"Current\")+COUNTIF('Cleaned Data'!$L:$L, \"Late (31-120 days)\")+COUNTIF('Cleaned Data'!$L:$L, \"Late (16-30 days)\")+COUNTIF('Cleaned Data'!$L:$L, \"In Grace Period\")), 0)").font = font_total
    ws_risk.cell(row=14, column=7).number_format = "0.00%"
    ws_risk.cell(row=14, column=8, value="=IFERROR(SUMIF('Cleaned Data'!$L:$L, \"Charged Off\", 'Cleaned Data'!$C:$C)/C14, 0)").font = font_total
    ws_risk.cell(row=14, column=8).number_format = "0.00%"
    ws_risk.cell(row=14, column=9, value="=IFERROR(SUM('Cleaned Data'!$U:$U)/SUMIF('Cleaned Data'!$L:$L, \"Charged Off\", 'Cleaned Data'!$C:$C), 0)").font = font_total
    ws_risk.cell(row=14, column=9).number_format = "0.00%"

    for c in range(1, 10):
        ws_risk.cell(row=14, column=c).border = border_total

    # Sheet 6: Borrower Analysis
    ws_borrower = wb.create_sheet(title="Borrower Analysis")
    ws_borrower.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_borrower, "BORROWER RISK SEGMENTATION & DEMOGRAPHICS", "Underwriting Risk Profiles across Income, DTI, and Home Ownership", max_col=8)

    # Home ownership breakdown
    ws_borrower.cell(row=4, column=1, value="Risk by Home Ownership").font = font_sec_header
    h_heads = ["Home Ownership", "Loan Count", "Capital Funded ($)", "Avg Annual Income ($)", "Default Rate (%)"]
    for c_i, h in enumerate(h_heads, start=1):
        cell = ws_borrower.cell(row=5, column=c_i, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark

    for idx, ho in enumerate(["MORTGAGE", "RENT", "OWN"], start=6):
        ws_borrower.cell(row=idx, column=1, value=ho).font = font_data
        ws_borrower.cell(row=idx, column=2, value=f'=COUNTIF(\'Cleaned Data\'!$J:$J, "{ho}")').number_format = "#,##0"
        ws_borrower.cell(row=idx, column=3, value=f'=SUMIF(\'Cleaned Data\'!$J:$J, "{ho}", \'Cleaned Data\'!$C:$C)').number_format = "$#,##0"
        ws_borrower.cell(row=idx, column=4, value=f'=AVERAGEIF(\'Cleaned Data\'!$J:$J, "{ho}", \'Cleaned Data\'!$K:$K)').number_format = "$#,##0"
        bad_f = f'(COUNTIFS(\'Cleaned Data\'!$J:$J, "{ho}", \'Cleaned Data\'!$L:$L, "Charged Off") + COUNTIFS(\'Cleaned Data\'!$J:$J, "{ho}", \'Cleaned Data\'!$L:$L, "Default"))'
        cls_f = f'(COUNTIFS(\'Cleaned Data\'!$J:$J, "{ho}", \'Cleaned Data\'!$L:$L, "Fully Paid") + {bad_f})'
        ws_borrower.cell(row=idx, column=5, value=f"=IFERROR({bad_f}/{cls_f}, 0)").number_format = "0.00%"
        for c in range(1, 6):
            ws_borrower.cell(row=idx, column=c).border = border_cell

    # Loan tenure breakdown (36 vs 60)
    ws_borrower.cell(row=11, column=1, value="Risk by Loan Tenure (Term)").font = font_sec_header
    t_heads = ["Tenure", "Loan Count", "Capital Funded ($)", "Avg Interest Rate (%)", "Default Rate (%)"]
    for c_i, h in enumerate(t_heads, start=1):
        cell = ws_borrower.cell(row=12, column=c_i, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark

    for idx, term in enumerate([36, 60], start=13):
        ws_borrower.cell(row=idx, column=1, value=f"{term} Months").font = font_data
        ws_borrower.cell(row=idx, column=2, value=f'=COUNTIF(\'Cleaned Data\'!$D:$D, {term})').number_format = "#,##0"
        ws_borrower.cell(row=idx, column=3, value=f'=SUMIF(\'Cleaned Data\'!$D:$D, {term}, \'Cleaned Data\'!$C:$C)').number_format = "$#,##0"
        ws_borrower.cell(row=idx, column=4, value=f'=AVERAGEIF(\'Cleaned Data\'!$D:$D, {term}, \'Cleaned Data\'!$E:$E)/100').number_format = "0.00%"
        bad_f = f'(COUNTIFS(\'Cleaned Data\'!$D:$D, {term}, \'Cleaned Data\'!$L:$L, "Charged Off") + COUNTIFS(\'Cleaned Data\'!$D:$D, {term}, \'Cleaned Data\'!$L:$L, "Default"))'
        cls_f = f'(COUNTIFS(\'Cleaned Data\'!$D:$D, {term}, \'Cleaned Data\'!$L:$L, "Fully Paid") + {bad_f})'
        ws_borrower.cell(row=idx, column=5, value=f"=IFERROR({bad_f}/{cls_f}, 0)").number_format = "0.00%"
        for c in range(1, 6):
            ws_borrower.cell(row=idx, column=c).border = border_cell

    # Sheet 7: Vintage Analysis
    ws_vin = wb.create_sheet(title="Vintage Analysis")
    ws_vin.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_vin, "LOAN ORIGINATION VINTAGE ANALYSIS (2007 - 2018)", "Cohort Maturation, Default Seasoning, and Capital Liquidation", max_col=9)

    v_heads = ["Origination Year", "Originated Loans", "Funded Amount ($)", "Principal Repaid ($)", "Interest Collected ($)", "Outstanding Balance ($)", "Default Rate (%)", "Recovery Rate (%)"]
    for c_i, h in enumerate(v_heads, start=1):
        cell = ws_vin.cell(row=5, column=c_i, value=h)
        cell.font = font_tbl_header
        cell.fill = fill_navy_dark

    for idx, yr in enumerate(range(2007, 2019), start=6):
        ws_vin.cell(row=idx, column=1, value=yr).font = font_data
        ws_vin.cell(row=idx, column=2, value=f'=COUNTIF(\'Cleaned Data\'!$M:$M, {yr})').number_format = "#,##0"
        ws_vin.cell(row=idx, column=3, value=f'=SUMIF(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$C:$C)').number_format = "$#,##0"
        ws_vin.cell(row=idx, column=4, value=f'=SUMIF(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$R:$R)').number_format = "$#,##0"
        ws_vin.cell(row=idx, column=5, value=f'=SUMIF(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$S:$S)').number_format = "$#,##0"
        ws_vin.cell(row=idx, column=6, value=f'=SUMIF(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$P:$P)').number_format = "$#,##0"
        bad_f = f'(COUNTIFS(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$L:$L, "Charged Off") + COUNTIFS(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$L:$L, "Default"))'
        cls_f = f'(COUNTIFS(\'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$L:$L, "Fully Paid") + {bad_f})'
        ws_vin.cell(row=idx, column=7, value=f"=IFERROR({bad_f}/{cls_f}, 0)").number_format = "0.00%"
        co_fnd = f'SUMIFS(\'Cleaned Data\'!$C:$C, \'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$L:$L, "Charged Off")'
        rec_f = f'SUMIFS(\'Cleaned Data\'!$U:$U, \'Cleaned Data\'!$M:$M, {yr}, \'Cleaned Data\'!$L:$L, "Charged Off")'
        ws_vin.cell(row=idx, column=8, value=f"=IFERROR({rec_f}/{co_fnd}, 0)").number_format = "0.00%"

        for c in range(1, 9):
            ws_vin.cell(row=idx, column=c).border = border_cell

    # Sheet 8: Methodology
    ws_meth = wb.create_sheet(title="Methodology")
    ws_meth.views.sheetView[0].showGridLines = True
    apply_title_banner(ws_meth, "FINANCIAL METHODOLOGY & CALCULATION STANDARDS", "Mathematical Definitions, Population Scopes, and Banking Standards", max_col=6)

    methodology_sections = [
        ("1. Total Origination / Funded Capital", "=SUM(funded_amnt)", "Aggregate cash deployed by investors into borrower notes. Used as denominator for portfolio charge-off rates."),
        ("2. Outstanding Portfolio Ratio", "=Total Outstanding / Total Funded", "Percentage of origination capital remaining unliquidated and subject to ongoing credit/default risk."),
        ("3. Closed Cohort Default Rate", "=(Charged Off + Default) / (Fully Paid + Charged Off + Default)", "Measures terminal default incidence among matured loans that have reached an unalterable final state."),
        ("4. Active Delinquency Rate", "=(Late 16-30 + Late 31-120) / (Current + Late + In Grace Period)", "Point-in-time proportion of active repayment accounts currently in arrears."),
        ("5. Portfolio Charge-Off Rate", "=Charged-Off Funded Amount / Total Funded Amount", "Cumulative monetary capital lost to non-performing debt write-downs."),
        ("6. Debt Recovery Rate", "=Gross Post-Default Recoveries / Charged-Off Funded Amount", "Efficiency of internal and third-party recovery efforts in salvaging write-down losses."),
        ("7. Vintage Maturation Caveat", "Immature Vintages != Matured Vintages", "Recent cohorts (e.g. 2017-2018 60-month notes) have incomplete seasoning; observed default rates reflect early life-cycle stages.")
    ]
    ws_meth.cell(row=4, column=1, value="Metric Name").font = font_tbl_header
    ws_meth.cell(row=4, column=1).fill = fill_navy_dark
    ws_meth.cell(row=4, column=2, value="Mathematical Formulation").font = font_tbl_header
    ws_meth.cell(row=4, column=2).fill = fill_navy_dark
    ws_meth.cell(row=4, column=3, value="Banking & Underwriting Definition").font = font_tbl_header
    ws_meth.cell(row=4, column=3).fill = fill_navy_dark

    for r_i, (m, f, d) in enumerate(methodology_sections, start=5):
        c1 = ws_meth.cell(row=r_i, column=1, value=m)
        c2 = ws_meth.cell(row=r_i, column=2, value=f)
        c3 = ws_meth.cell(row=r_i, column=3, value=d)
        c1.font = font_data
        c2.font = font_data
        c3.font = font_data
        c1.border = border_cell
        c2.border = border_cell
        c3.border = border_cell

    # Adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col[:30])
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(out_file)
    print(f"Excel workbook successfully generated and saved to {out_file}")
    return out_file

if __name__ == "__main__":
    build_excel_workbook()
