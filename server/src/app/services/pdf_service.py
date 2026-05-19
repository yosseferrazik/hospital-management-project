from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.services.report_service import (
    summary_report, doctor_workload_report, medications_report,
    financial_report, radiology_report, admissions_report, surgeries_report,
)

LM = 25
RM = 25
PW = 210
TW = PW - LM - RM
BLUE = (37, 99, 235)
DARK = (15, 23, 42)
GRAY = (100, 116, 139)
LGRAY = (241, 243, 247)
WHITE = (255, 255, 255)
GREEN = (5, 150, 105)
ORANGE = (245, 158, 11)
PURPLE = (124, 58, 237)
RED = (220, 38, 38)


def _avg_stay(recs):
    ds = [r.get("stay_days") for r in recs if r.get("stay_days") is not None]
    return round(sum(ds) / len(ds), 1) if ds else 0


class ReportPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Sa Palomera Hospital  |  {self.page_no()}/{{nb}}", align="C")

    def dark_bar(self, h):
        self.set_fill_color(*DARK)
        self.rect(0, 0, PW, h, "F")
        self.set_y(h - 11)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WHITE)
        self.cell(0, 6, "", align="C", ln=True)

    def section(self, title):
        self.ln(3)
        self.set_x(LM)
        self.set_fill_color(*BLUE)
        r = self.get_y()
        self.rect(LM, r, 3, 7, "F")
        self.set_x(LM + 8)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.cell(0, 7, title, ln=True)
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.3)
        self.line(LM, self.get_y() + 2, PW - RM, self.get_y() + 2)
        self.ln(4)

    def th(self, cols, ws):
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 7)
        self.set_draw_color(*DARK)
        for i, c in enumerate(cols):
            self.cell(ws[i], 7, c, border=1, fill=True, align="C")
        self.ln()

    def tr(self, vs, ws, alt=False):
        if alt:
            self.set_fill_color(*LGRAY)
        else:
            self.set_fill_color(*WHITE)
        self.set_text_color(*DARK)
        self.set_font("Helvetica", "", 7.5)
        self.set_draw_color(209, 213, 219)
        for i, v in enumerate(vs):
            self.cell(ws[i], 6.5, str(v), border=1, fill=True, align="C" if i else "L")
        self.ln()

    def kpi_card(self, label, value, x, y, w, color=None):
        self.set_fill_color(*LGRAY)
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.3)
        self.rect(x, y, w, 28, "DF")
        c = color or DARK
        self.set_xy(x, y + 3)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRAY)
        self.cell(w, 4, label.upper(), align="C", ln=True)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*c)
        self.cell(w, 10, str(value), align="C", ln=True)

    def space_for(self, needed):
        return self.get_y() + needed < self.h - self.b_margin

    def table_block(self, title, headers, widths, rows, limit=15):
        if not rows:
            return
        est = 12 + 7 + min(len(rows), limit) * 6.5
        if not self.space_for(est):
            self.add_page()
        if title:
            self.section(title)
        self.th(headers, widths)
        for i, r in enumerate(rows[:limit]):
            self.tr(r, widths, i % 2)


def make_summary_pdf(start_date=None, end_date=None):
    data = summary_report(start_date, end_date)
    wl = doctor_workload_report(start_date, end_date)
    med = medications_report(start_date, end_date)
    fin = financial_report(start_date, end_date)
    rad = radiology_report(start_date, end_date)
    adm = admissions_report(start_date, end_date)
    surg = surgeries_report(start_date, end_date)

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.alias_nb_pages()

    p = data.get("period", {})
    ps, pe = p.get("start", ""), p.get("end", "")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    t = data.get("totals", {})
    a = data.get("activity", {})
    o = data.get("occupancy", {})
    occ_r = o.get("occupancy_rate", 0)
    total_cost = fin.get("total_cost", 0)
    avg_st = _avg_stay(adm.get("records", []))

    # ----------------------------------------------------------------
    #  PAGE 1  -  EXECUTIVE DASHBOARD
    # ----------------------------------------------------------------
    pdf.add_page()
    pdf.dark_bar(58)
    pdf.set_y(16)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, "Sa Palomera Hospital", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"{ps}  -  {pe}", align="C", ln=True)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(200, 210, 220)
    pdf.cell(0, 5, f"Generated {now}", align="C", ln=True)

    pdf.set_y(68)
    pdf.section("Executive Summary")
    overview = (
        f"Hospital activity for the period {ps} - {pe}: "
        f"{a.get('visits',0)} visits, {a.get('surgeries',0)} surgeries, "
        f"{a.get('admissions',0)} admissions. "
        f"Patient base: {t.get('patients',0)}. "
        f"Staff: {t.get('staff',0)} ({t.get('doctors',0)} physicians, "
        f"{t.get('nurses',0)} nurses). "
        f"Occupancy rate: {occ_r}% ({o.get('active_admissions',0)} of "
        f"{o.get('total_rooms',0)} beds occupied). "
        f"Average length of stay: {avg_st} days. "
        f"Total pharmacy cost: ${total_cost:,.2f}."
    )
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*GRAY)
    pdf.multi_cell(0, 5, overview, align="J")
    pdf.ln(4)

    ky = max(pdf.get_y(), 98)
    gap = 6
    cw = (TW - 3 * gap) / 4
    x0 = LM
    x1 = x0 + cw + gap
    x2 = x1 + cw + gap
    x3 = x2 + cw + gap

    occ_c = GREEN if occ_r < 80 else ORANGE if occ_r < 95 else RED

    pdf.kpi_card("Patients", t.get("patients", 0), x0, ky, cw)
    pdf.kpi_card("Staff", t.get("staff", 0), x1, ky, cw)
    pdf.kpi_card("Occupancy", f"{occ_r}%", x2, ky, cw, occ_c)
    pdf.kpi_card("Active Adm.", o.get("active_admissions", 0), x3, ky, cw, ORANGE)

    ky2 = ky + 34
    pdf.kpi_card("Visits", a.get("visits", 0), x0, ky2, cw)
    pdf.kpi_card("Surgeries", a.get("surgeries", 0), x1, ky2, cw, PURPLE)
    pdf.kpi_card("Admissions", a.get("admissions", 0), x2, ky2, cw, ORANGE)
    pdf.kpi_card("Pharmacy Cost", f"${total_cost:,.0f}", x3, ky2, cw, GREEN)

    after_kpi = ky2 + 34
    if pdf.space_for(50):
        pdf.set_y(after_kpi)

    dd = data.get("top_diagnoses", [])
    dd_rows = [[d.get("diagnosis", ""), str(d.get("count", 0))] for d in dd[:10]]
    pdf.table_block("Top Diagnoses", ["Diagnosis", "Cases"], [TW * 0.72, TW * 0.28], dd_rows, 10)

    st = data.get("surgeries_by_type", [])
    st_rows = [[s.get("procedure", ""), str(s.get("count", 0))] for s in st[:10]]
    pdf.table_block("Surgeries by Type", ["Procedure", "Count"], [TW * 0.72, TW * 0.28], st_rows, 10)

    # ----------------------------------------------------------------
    #  PAGE 2  -  CLINICAL ACTIVITY
    # ----------------------------------------------------------------
    pdf.add_page()
    pdf.dark_bar(14)

    docs = wl.get("records", [])
    doc_rows = [
        [d.get("doctor", ""), d.get("specialty", ""),
         str(d.get("visits", 0)), str(d.get("surgeries", 0)), str(d.get("patients", 0))]
        for d in docs[:15]
    ]
    pdf.table_block(
        "Physician Workload",
        ["Physician", "Specialty", "Visits", "Surg.", "Patients"],
        [TW * 0.30, TW * 0.22, TW * 0.14, TW * 0.14, TW * 0.20],
        doc_rows, 15,
    )

    mds = med.get("records", [])
    md_rows = [
        [m.get("medication", ""), str(m.get("prescriptions", 0)), str(m.get("visits", 0))]
        for m in mds[:15]
    ]
    pdf.table_block(
        "Prescribed Medications",
        ["Medication", "Prescriptions", "Visits"],
        [TW * 0.50, TW * 0.25, TW * 0.25],
        md_rows, 15,
    )

    rr = rad.get("records", [])
    if rr:
        sc = {}
        for r in rr:
            s = r.get("status", "UNKNOWN")
            sc[s] = sc.get(s, 0) + 1
        rad_rows = [[st, str(cnt)] for st, cnt in sorted(sc.items())]
        pdf.table_block("Radiology Exams", ["Status", "Count"],
                        [TW * 0.70, TW * 0.30], rad_rows, 10)
        if pdf.space_for(8):
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*GRAY)
            pdf.cell(0, 5, f"Total exams in the period: {rad.get('total', 0)}", ln=True)

    # ----------------------------------------------------------------
    #  PAGE 3  -  FINANCIAL & OPERATIONS
    # ----------------------------------------------------------------
    pdf.add_page()
    pdf.dark_bar(14)

    pdf.section("Pharmacy Dispensations")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 6, f"Total: ${total_cost:,.2f}  -  {fin.get('total', 0)} dispensation(s)", ln=True)
    pdf.ln(2)
    fins = fin.get("records", [])
    fin_rows = [
        [r.get("date", ""), r.get("patient", ""), f"${r.get('total_cost', 0):.2f}"]
        for r in fins[:15]
    ]
    pdf.table_block(
        "",
        ["Date", "Patient", "Amount"],
        [TW * 0.22, TW * 0.48, TW * 0.30],
        fin_rows, 15,
    )

    ar = adm.get("records", [])
    active = sum(1 for r in ar if not r.get("actual_discharge"))
    disch = sum(1 for r in ar if r.get("actual_discharge"))
    pdf.section("Admissions")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(
        0, 5,
        f"Period: {adm.get('total', 0)}  -  Active: {active}  -  "
        f"Discharged: {disch}  -  Avg stay: {avg_st}d",
        ln=True,
    )
    pdf.ln(2)
    adm_rows = [
        [r.get("admission_date", ""), r.get("patient", ""), r.get("room", ""),
         r.get("floor", ""), str(r.get("stay_days", "") or "")]
        for r in ar[:15]
    ]
    pdf.table_block(
        "",
        ["Date", "Patient", "Room", "Floor", "Stay (d)"],
        [TW * 0.22, TW * 0.28, TW * 0.16, TW * 0.12, TW * 0.12],
        adm_rows, 15,
    )

    sr = surg.get("records", [])
    sr_rows = [
        [r.get("date", ""), r.get("procedure", ""), r.get("patient", ""),
         r.get("surgeon", ""), r.get("duration", "")]
        for r in sr[:15]
    ]
    pdf.table_block(
        "Recent Surgeries",
        ["Date", "Procedure", "Patient", "Surgeon", "Duration"],
        [TW * 0.18, TW * 0.28, TW * 0.22, TW * 0.22, TW * 0.10],
        sr_rows, 15,
    )

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
