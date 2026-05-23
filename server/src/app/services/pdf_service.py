from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.services.report_service import (
    admissions_report,
    doctor_workload_report,
    financial_report,
    medications_report,
    radiology_report,
    summary_report,
    surgeries_report,
)



BLUE   = (37,  99,  235)
DARK   = (15,  23,   42)
GRAY   = (100, 116, 139)
LGRAY  = (241, 243, 247)
WHITE  = (255, 255, 255)
GREEN  = (5,   150, 105)
ORANGE = (245, 158,  11)
PURPLE = (124,  58, 237)
RED    = (220,  38,  38)

PW   = 210   # A4 page width (mm)
LM   = 20    # left margin (mm)
RM   = 20    # right margin (mm)
TW   = PW - LM - RM   # usable content width (mm)

FONT_XS   = 6.5
FONT_SM   = 7.5
FONT_BASE = 8.5
FONT_MD   = 10
FONT_LG   = 15
FONT_XL   = 22

ROW_H    = 6.5   # table row height
HEADER_H = 7     # table header height
KPI_H    = 28    # KPI card height
KPI_GAP  = 5     # gap between KPI cards
SECTION_GAP = 3  # vertical gap before a section title


def _avg_stay(records: list[dict]) -> float:
    """Return the average stay in days for a list of admission records."""
    days = [r["stay_days"] for r in records if r.get("stay_days") is not None]
    return round(sum(days) / len(days), 1) if days else 0



class ReportPDF(FPDF):
    """Custom FPDF subclass with reusable layout helpers."""

    def header(self) -> None:
        """No automatic page header (handled manually per page)."""
        pass

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", FONT_XS)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Sa Palomera Hospital  |  {self.page_no()}/{{nb}}", align="C")

    def dark_bar(self, height: int) -> None:
        """Dark banner at the top of a page."""
        self.set_fill_color(*DARK)
        self.rect(0, 0, PW, height, "F")
        self.set_y(height - 11)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.cell(0, 6, "", align="C", ln=True)

    def section(self, title: str) -> None:
        """Coloured section heading with a thin divider line below."""
        self.ln(SECTION_GAP)
        y = self.get_y()

        # Accent bar
        self.set_fill_color(*BLUE)
        self.rect(LM, y, 3, 7, "F")

        # Title text
        self.set_x(LM + 8)
        self.set_font("Helvetica", "B", FONT_MD)
        self.set_text_color(*DARK)
        self.cell(0, 7, title, ln=True)

        # Divider
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.3)
        self.line(LM, self.get_y() + 2, PW - RM, self.get_y() + 2)
        self.ln(5)

    def table_header(self, columns: list[str], widths: list[float]) -> None:
        """Render a dark table header row."""
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", FONT_XS)
        self.set_draw_color(*DARK)
        for col, width in zip(columns, widths):
            self.cell(width, HEADER_H, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, values: list, widths: list[float], alternate: bool = False) -> None:
        """Render a single data row with optional zebra-striping."""
        self.set_fill_color(*LGRAY if alternate else WHITE)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "", FONT_SM)
        self.set_draw_color(209, 213, 219)
        for i, (value, width) in enumerate(zip(values, widths)):
            align = "C" if i > 0 else "L"
            self.cell(width, ROW_H, str(value), border=1, fill=True, align=align)
        self.ln()

    def kpi_card(
        self,
        label: str,
        value,
        x: float,
        y: float,
        width: float,
        color: tuple = None,
    ) -> None:
        """Draw a single KPI tile."""
        self.set_fill_color(*WHITE)
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.3)
        self.rect(x, y, width, KPI_H, "DF")

        # Label
        self.set_xy(x + 1, y + 3)
        self.set_font("Helvetica", "", FONT_XS)
        self.set_text_color(*GRAY)
        self.cell(width - 2, 4, label.upper(), align="C", ln=True)

        # Value
        self.set_x(x + 1)
        self.set_font("Helvetica", "B", FONT_LG)
        self.set_text_color(*(color or DARK))
        self.cell(width - 2, 9, str(value), align="C", ln=True)

    def has_room_for(self, needed_height: float) -> bool:
        """Return True when *needed_height* mm still fits on the current page."""
        return self.get_y() + needed_height < self.h - self.b_margin

    def table_block(
        self,
        title: str,
        headers: list[str],
        widths: list[float],
        rows: list[list],
        limit: int = 15,
    ) -> None:
        """Render an optional section heading followed by a full table."""
        if not rows:
            return

        # Estimate height; break page early if needed
        est_height = 12 + HEADER_H + min(len(rows), limit) * ROW_H
        if not self.has_room_for(est_height):
            self.add_page()

        if title:
            self.section(title)

        self.set_x(LM)
        self.table_header(headers, widths)
        for i, row in enumerate(rows[:limit]):
            self.set_x(LM)
            self.table_row(row, widths, alternate=bool(i % 2))



def _kpi_row(pdf: ReportPDF, cards: list[tuple], y: float, cw: float) -> None:
    """
    Render a horizontal row of KPI cards.

    Each item in *cards* is ``(label, value [, color])``.
    """
    n = len(cards)
    for i, card in enumerate(cards):
        x = LM + i * (cw + KPI_GAP)
        color = card[2] if len(card) == 3 else None
        pdf.kpi_card(card[0], card[1], x, y, cw, color)



def make_summary_pdf(start_date=None, end_date=None) -> bytes:
    """Build and return the full hospital summary report as raw PDF bytes."""

    data = summary_report(start_date, end_date)
    wl   = doctor_workload_report(start_date, end_date)
    med  = medications_report(start_date, end_date)
    fin  = financial_report(start_date, end_date)
    rad  = radiology_report(start_date, end_date)
    adm  = admissions_report(start_date, end_date)
    surg = surgeries_report(start_date, end_date)

    period     = data.get("period", {})
    ps, pe     = period.get("start", ""), period.get("end", "")
    generated  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    totals     = data.get("totals", {})
    activity   = data.get("activity", {})
    occupancy  = data.get("occupancy", {})
    occ_rate   = occupancy.get("occupancy_rate", 0)
    total_cost = fin.get("total_cost", 0)
    avg_stay   = _avg_stay(adm.get("records", []))

    occ_color  = GREEN if occ_rate < 80 else (ORANGE if occ_rate < 95 else RED)

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.alias_nb_pages()

    # KPI card geometry (4 cards per row)
    cw = (TW - 3 * KPI_GAP) / 4


    pdf.add_page()

    # Cover banner
    pdf.dark_bar(56)
    pdf.set_y(12)
    pdf.set_font("Helvetica", "B", FONT_XL)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "Sa Palomera Hospital", align="C", ln=True)
    pdf.set_font("Helvetica", "", FONT_MD)
    pdf.cell(0, 7, f"{ps}  -  {pe}", align="C", ln=True)
    pdf.set_font("Helvetica", "", FONT_XS)
    pdf.set_text_color(190, 200, 210)
    pdf.cell(0, 5, f"Generated {generated}", align="C", ln=True)

    # Executive summary paragraph
    pdf.set_y(66)
    pdf.section("Executive Summary")
    overview = (
        f"Hospital activity for the period {ps} - {pe}: "
        f"{activity.get('visits', 0)} visits, {activity.get('surgeries', 0)} surgeries, "
        f"{activity.get('admissions', 0)} admissions. "
        f"Patient base: {totals.get('patients', 0)}. "
        f"Staff: {totals.get('staff', 0)} "
        f"({totals.get('doctors', 0)} physicians, {totals.get('nurses', 0)} nurses). "
        f"Occupancy rate: {occ_rate}% "
        f"({occupancy.get('active_admissions', 0)} of {occupancy.get('total_rooms', 0)} beds). "
        f"Average length of stay: {avg_stay} days. "
        f"Total pharmacy cost: ${total_cost:,.2f}."
    )
    pdf.set_font("Helvetica", "", FONT_BASE)
    pdf.set_text_color(*GRAY)
    pdf.set_x(LM)
    pdf.multi_cell(TW, 5.5, overview, align="J")
    pdf.ln(5)

    # KPI rows
    ky = max(pdf.get_y(), 100)
    _kpi_row(pdf, [
        ("Patients",    totals.get("patients", 0)),
        ("Staff",       totals.get("staff", 0)),
        ("Occupancy",   f"{occ_rate}%",          occ_color),
        ("Active Adm.", occupancy.get("active_admissions", 0), ORANGE),
    ], ky, cw)

    ky2 = ky + KPI_H + 5
    _kpi_row(pdf, [
        ("Visits",        activity.get("visits", 0)),
        ("Surgeries",     activity.get("surgeries", 0),      PURPLE),
        ("Admissions",    activity.get("admissions", 0),     ORANGE),
        ("Pharmacy Cost", f"${total_cost:,.0f}",             GREEN),
    ], ky2, cw)

    pdf.set_y(ky2 + KPI_H + 6)

    # Summary tables
    diag_rows = [
        [d.get("diagnosis", ""), d.get("count", 0)]
        for d in data.get("top_diagnoses", [])[:10]
    ]
    pdf.table_block(
        "Top Diagnoses",
        ["Diagnosis", "Cases"],
        [TW * 0.72, TW * 0.28],
        diag_rows,
        limit=10,
    )

    surg_type_rows = [
        [s.get("procedure", ""), s.get("count", 0)]
        for s in data.get("surgeries_by_type", [])[:10]
    ]
    pdf.table_block(
        "Surgeries by Type",
        ["Procedure", "Count"],
        [TW * 0.72, TW * 0.28],
        surg_type_rows,
        limit=10,
    )


    pdf.add_page()
    pdf.dark_bar(14)

    doc_rows = [
        [
            d.get("doctor", ""),
            d.get("specialty", ""),
            d.get("visits", 0),
            d.get("surgeries", 0),
            d.get("patients", 0),
        ]
        for d in wl.get("records", [])[:15]
    ]
    pdf.table_block(
        "Physician Workload",
        ["Physician", "Specialty", "Visits", "Surg.", "Patients"],
        [TW * 0.30, TW * 0.22, TW * 0.14, TW * 0.14, TW * 0.20],
        doc_rows,
    )

    med_rows = [
        [m.get("medication", ""), m.get("prescriptions", 0), m.get("visits", 0)]
        for m in med.get("records", [])[:15]
    ]
    pdf.table_block(
        "Prescribed Medications",
        ["Medication", "Prescriptions", "Visits"],
        [TW * 0.50, TW * 0.25, TW * 0.25],
        med_rows,
    )

    rad_records = rad.get("records", [])
    if rad_records:
        status_counts: dict[str, int] = {}
        for r in rad_records:
            key = r.get("status", "UNKNOWN")
            status_counts[key] = status_counts.get(key, 0) + 1

        rad_rows = [[st, cnt] for st, cnt in sorted(status_counts.items())]
        pdf.table_block(
            "Radiology Exams",
            ["Status", "Count"],
            [TW * 0.70, TW * 0.30],
            rad_rows,
            limit=10,
        )
        if pdf.has_room_for(8):
            pdf.set_x(LM)
            pdf.set_font("Helvetica", "", FONT_SM)
            pdf.set_text_color(*GRAY)
            pdf.cell(0, 6, f"Total exams in the period: {rad.get('total', 0)}", ln=True)


    pdf.add_page()
    pdf.dark_bar(14)

    # Pharmacy summary line
    pdf.section("Pharmacy Dispensations")
    pdf.set_x(LM)
    pdf.set_font("Helvetica", "B", FONT_MD)
    pdf.set_text_color(*GREEN)
    pdf.cell(
        0, 7,
        f"Total: ${total_cost:,.2f}  -  {fin.get('total', 0)} dispensation(s)",
        ln=True,
    )
    pdf.ln(3)

    fin_rows = [
        [r.get("date", ""), r.get("patient", ""), f"${r.get('total_cost', 0):.2f}"]
        for r in fin.get("records", [])[:15]
    ]
    pdf.table_block(
        "",
        ["Date", "Patient", "Amount"],
        [TW * 0.22, TW * 0.48, TW * 0.30],
        fin_rows,
    )

    # Admissions summary
    adm_records = adm.get("records", [])
    active_count     = sum(1 for r in adm_records if not r.get("actual_discharge"))
    discharged_count = sum(1 for r in adm_records if r.get("actual_discharge"))

    pdf.section("Admissions")
    pdf.set_x(LM)
    pdf.set_font("Helvetica", "", FONT_BASE)
    pdf.set_text_color(*GRAY)
    pdf.cell(
        0, 6,
        (
            f"Period: {adm.get('total', 0)}  -  "
            f"Active: {active_count}  -  "
            f"Discharged: {discharged_count}  -  "
            f"Avg stay: {avg_stay} d"
        ),
        ln=True,
    )
    pdf.ln(3)

    adm_rows = [
        [
            r.get("admission_date", ""),
            r.get("patient", ""),
            r.get("room", ""),
            r.get("floor", ""),
            r.get("stay_days", "") or "",
        ]
        for r in adm_records[:15]
    ]
    pdf.table_block(
        "",
        ["Date", "Patient", "Room", "Floor", "Stay (d)"],
        [TW * 0.22, TW * 0.28, TW * 0.16, TW * 0.12, TW * 0.12],
        adm_rows,
    )

    surg_rows = [
        [
            r.get("date", ""),
            r.get("procedure", ""),
            r.get("patient", ""),
            r.get("surgeon", ""),
            r.get("duration", ""),
        ]
        for r in surg.get("records", [])[:15]
    ]
    pdf.table_block(
        "Recent Surgeries",
        ["Date", "Procedure", "Patient", "Surgeon", "Duration"],
        [TW * 0.18, TW * 0.28, TW * 0.22, TW * 0.22, TW * 0.10],
        surg_rows,
    )

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()