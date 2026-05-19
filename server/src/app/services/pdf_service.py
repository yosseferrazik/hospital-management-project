from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.services.report_service import summary_report


PDF_MARGIN = 20
PAGE_W = 210
TABLE_W = PAGE_W - 2 * PDF_MARGIN


def _header_row(pdf, cols, widths):
    pdf.set_fill_color(31, 41, 55)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    for i, col in enumerate(cols):
        pdf.cell(widths[i], 7, col, border=1, fill=True, align="C")
    pdf.ln()


def _data_row(pdf, vals, widths, fill=False):
    if fill:
        pdf.set_fill_color(243, 244, 246)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(31, 41, 55)
    pdf.set_font("Helvetica", "", 9)
    for i, v in enumerate(vals):
        pdf.cell(widths[i], 6, str(v), border=1, fill=True, align="C" if i > 0 else "L")
    pdf.ln()


def make_summary_pdf(start_date=None, end_date=None):
    data = summary_report(start_date, end_date)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Page 1: Cover / Summary ──
    pdf.add_page()
    pdf.set_fill_color(31, 41, 55)
    pdf.rect(0, 0, PAGE_W, 40, "F")
    pdf.set_y(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Sa Palomera Hospital", align="C", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Executive Summary Report", align="C", ln=True)

    pdf.set_y(50)
    pdf.set_text_color(107, 114, 128)
    pdf.set_font("Helvetica", "", 10)
    period = data.get("period", {})
    pdf.cell(0, 6, f"Period:  {period.get('start', 'N/A')}   to   {period.get('end', 'N/A')}", align="C", ln=True)

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(0, 6, f"Generated:  {now_str}", align="C", ln=True)

    # ── KPI cards ──
    totals = data.get("totals", {})
    activity = data.get("activity", {})
    occupancy = data.get("occupancy", {})

    pdf.set_y(75)
    card_w = TABLE_W / 4

    def kpi_card(pdf, label, value, x, y):
        pdf.set_xy(x, y)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(209, 213, 219)
        pdf.rect(x, y, card_w - 3, 28, "DF")
        pdf.set_xy(x, y + 4)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(card_w - 3, 5, label, align="C", ln=True)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(card_w - 3, 8, str(value), align="C", ln=True)

    kpi_card(pdf, "Total Patients", totals.get("patients", 0), PDF_MARGIN, 75)
    kpi_card(pdf, "Total Staff", totals.get("staff", 0), PDF_MARGIN + card_w, 75)
    kpi_card(pdf, "Occupancy", f'{occupancy.get("occupancy_rate", 0)}%', PDF_MARGIN + card_w * 2, 75)
    kpi_card(pdf, "Active Admissions", occupancy.get("active_admissions", 0), PDF_MARGIN + card_w * 3, 75)

    pdf.set_y(110)
    kpi_card(pdf, "Visits (period)", activity.get("visits", 0), PDF_MARGIN, 110)
    kpi_card(pdf, "Surgeries (period)", activity.get("surgeries", 0), PDF_MARGIN + card_w, 110)
    kpi_card(pdf, "Admissions (period)", activity.get("admissions", 0), PDF_MARGIN + card_w * 2, 110)

    # ── Tables ──
    pdf.set_y(150)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, "Top Diagnoses", ln=True)
    pdf.ln(2)

    top_diag = data.get("top_diagnoses", [])
    if top_diag:
        widths = [TABLE_W * 0.7, TABLE_W * 0.3]
        _header_row(pdf, ["Diagnosis", "Cases"], widths)
        for i, d in enumerate(top_diag):
            _data_row(pdf, [d.get("diagnosis", ""), d.get("count", 0)], widths, fill=i % 2 == 0)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 6, "No diagnosis data available", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, "Surgeries by Type", ln=True)
    pdf.ln(2)

    surg_types = data.get("surgeries_by_type", [])
    if surg_types:
        widths2 = [TABLE_W * 0.7, TABLE_W * 0.3]
        _header_row(pdf, ["Procedure Type", "Count"], widths2)
        for i, s in enumerate(surg_types):
            _data_row(pdf, [s.get("procedure", ""), s.get("count", 0)], widths2, fill=i % 2 == 0)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 6, "No surgery data available", ln=True)

    # ── Footer ──
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(156, 163, 175)
    pdf.cell(0, 10, f"Sa Palomera Hospital - Executive Summary - Page {pdf.page_no()}/{{nb}}", align="C")

    pdf.alias_nb_pages()

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
