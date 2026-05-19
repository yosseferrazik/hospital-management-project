from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.services.report_service import (
    summary_report, doctor_workload_report, medications_report,
    financial_report, radiology_report, admissions_report, surgeries_report,
)

M = 20
PW = 210
TW = PW - 2 * M
BLUE = (37, 99, 235)
DARK = (15, 23, 42)
GRAY = (100, 116, 139)
LGRAY = (241, 243, 247)
WHITE = (255, 255, 255)
GREEN = (5, 150, 105)
ORANGE = (245, 158, 11)
PURPLE = (124, 58, 237)
RED = (220, 38, 38)


def _section(pdf, title, y=None):
    if y:
        pdf.set_y(y)
    pdf.set_x(M)
    pdf.set_fill_color(*BLUE)
    pdf.rect(M, pdf.get_y(), 3, 7, "F")
    pdf.set_x(M + 8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 7, title, ln=True)
    pdf.set_draw_color(209, 213, 219)
    pdf.set_line_width(0.3)
    pdf.line(M, pdf.get_y() + 2, PW - M, pdf.get_y() + 2)
    pdf.ln(5)


def _th(pdf, cols, ws):
    pdf.set_fill_color(*DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_draw_color(*DARK)
    for i, c in enumerate(cols):
        pdf.cell(ws[i], 6, c, border=1, fill=True, align="C")
    pdf.ln()


def _tr(pdf, vs, ws, alt=False):
    if alt:
        pdf.set_fill_color(*LGRAY)
    else:
        pdf.set_fill_color(*WHITE)
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_draw_color(209, 213, 219)
    for i, v in enumerate(vs):
        pdf.cell(ws[i], 5.5, str(v), border=1, fill=True, align="C" if i else "L")
    pdf.ln()


def _kpi(pdf, label, value, x, y, w, color=None):
    pdf.set_xy(x, y)
    pdf.set_fill_color(*WHITE)
    pdf.set_draw_color(209, 213, 219)
    pdf.rect(x, y, w, 26, "DF")
    c = color or DARK
    pdf.set_xy(x, y + 2.5)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    pdf.cell(w, 4, label.upper(), align="C", ln=True)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*c)
    pdf.cell(w, 8, str(value), align="C", ln=True)


def _avg_stay(recs):
    ds = [r.get("stay_days") for r in recs if r.get("stay_days") is not None]
    return round(sum(ds) / len(ds), 1) if ds else 0


def _page_header(pdf, title, h=36):
    pdf.set_fill_color(*DARK)
    pdf.rect(0, 0, PW, h, "F")
    if title:
        pdf.set_y(h - 10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*WHITE)
        pdf.cell(0, 6, title, align="C", ln=True)


def _page_number(pdf):
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 10, f"Sa Palomera Hospital  |  {pdf.page_no()}/{{nb}}", align="C")


def make_summary_pdf(start_date=None, end_date=None):
    data = summary_report(start_date, end_date)
    wl = doctor_workload_report(start_date, end_date)
    med = medications_report(start_date, end_date)
    fin = financial_report(start_date, end_date)
    rad = radiology_report(start_date, end_date)
    adm = admissions_report(start_date, end_date)
    surg = surgeries_report(start_date, end_date)

    pdf = FPDF()
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

    # ── PAGE 1 ──
    pdf.add_page()
    _page_header(pdf, "EXECUTIVE SUMMARY")
    pdf.set_y(10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, "Sa Palomera Hospital", align="C", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, f"{ps}  -  {pe}", align="C", ln=True)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(0, 4, f"Generated {now}", align="C", ln=True)

    pdf.set_y(44)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 5, "Hospital at a Glance", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GRAY)
    overview = (
        f"Hospital activity for the period {ps} - {pe}: "
        f"{a.get('visits',0)} visits, {a.get('surgeries',0)} surgeries, "
        f"{a.get('admissions',0)} admissions. "
        f"Patient base: {t.get('patients',0)}. "
        f"Staff: {t.get('staff',0)} ({t.get('doctors',0)} physicians, "
        f"{t.get('nurses',0)} nurses). "
        f"Occupancy: {occ_r}% ({o.get('active_admissions',0)} of "
        f"{o.get('total_rooms',0)} beds). "
        f"Avg stay: {avg_st} days. "
        f"Pharmacy costs: ${total_cost:,.2f}."
    )
    pdf.multi_cell(0, 4.5, overview, align="J")
    pdf.ln(2)

    cw = TW / 4
    ky = pdf.get_y()
    occ_c = GREEN if occ_r < 80 else ORANGE if occ_r < 95 else RED
    _kpi(pdf, "Patients", t.get("patients", 0), M, ky, cw)
    _kpi(pdf, "Staff", t.get("staff", 0), M + cw, ky, cw)
    _kpi(pdf, "Occupancy", f"{occ_r}%", M + cw * 2, ky, cw, occ_c)
    _kpi(pdf, "Active Adm.", o.get("active_admissions", 0), M + cw * 3, ky, cw, ORANGE)
    ky2 = ky + 30
    _kpi(pdf, "Visits", a.get("visits", 0), M, ky2, cw)
    _kpi(pdf, "Surgeries", a.get("surgeries", 0), M + cw, ky2, cw, PURPLE)
    _kpi(pdf, "Admissions", a.get("admissions", 0), M + cw * 2, ky2, cw, ORANGE)
    _kpi(pdf, "Disp. Costs", f"${total_cost:,.0f}", M + cw * 3, ky2, cw, GREEN)

    pdf.set_y(ky2 + 34)
    _section(pdf, "Top Diagnoses")
    dd = data.get("top_diagnoses", [])
    if dd:
        _th(pdf, ["Diagnosis", "Cases"], [TW * 0.7, TW * 0.3])
        for i, d in enumerate(dd[:10]):
            _tr(pdf, [d.get("diagnosis", ""), d.get("count", 0)], [TW * 0.7, TW * 0.3], i % 2)
    pdf.ln(2)

    _section(pdf, "Surgeries by Type")
    st = data.get("surgeries_by_type", [])
    if st:
        _th(pdf, ["Procedure Type", "Count"], [TW * 0.7, TW * 0.3])
        for i, s in enumerate(st[:10]):
            _tr(pdf, [s.get("procedure", ""), s.get("count", 0)], [TW * 0.7, TW * 0.3], i % 2)

    _page_number(pdf)

    # ── PAGE 2 ──
    pdf.add_page()
    _page_header(pdf, "CLINICAL ACTIVITY", 14)

    pdf.set_y(20)
    _section(pdf, "Physician Workload")
    docs = wl.get("records", [])
    if docs:
        _th(pdf, ["Physician", "Specialty", "Visits", "Surg.", "Patients"],
            [TW * 0.3, TW * 0.2, TW * 0.15, TW * 0.15, TW * 0.2])
        for i, d in enumerate(docs[:15]):
            _tr(pdf, [d.get("doctor", ""), d.get("specialty", ""),
                      d.get("visits", 0), d.get("surgeries", 0), d.get("patients", 0)],
                [TW * 0.3, TW * 0.2, TW * 0.15, TW * 0.15, TW * 0.2], i % 2)

    pdf.set_y(pdf.get_y() + 5)
    _section(pdf, "Prescribed Medications")
    mds = med.get("records", [])
    if mds:
        _th(pdf, ["Medication", "Prescriptions", "Visits"], [TW * 0.5, TW * 0.25, TW * 0.25])
        for i, m in enumerate(mds[:15]):
            _tr(pdf, [m.get("medication", ""), m.get("prescriptions", 0), m.get("visits", 0)],
                [TW * 0.5, TW * 0.25, TW * 0.25], i % 2)

    pdf.set_y(pdf.get_y() + 5)
    _section(pdf, "Radiology Exams")
    rr = rad.get("records", [])
    if rr:
        sc = {}
        for r in rr:
            s = r.get("status", "UNKNOWN")
            sc[s] = sc.get(s, 0) + 1
        _th(pdf, ["Status", "Count"], [TW * 0.7, TW * 0.3])
        for i, (st, cnt) in enumerate(sorted(sc.items())):
            _tr(pdf, [st, cnt], [TW * 0.7, TW * 0.3], i % 2)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 5, f"Total exams in period: {rad.get('total', 0)}", ln=True)

    _page_number(pdf)

    # ── PAGE 3 ──
    pdf.add_page()
    _page_header(pdf, "FINANCIAL & OPERATIONS", 14)

    pdf.set_y(20)
    _section(pdf, "Pharmacy Dispensations")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 6, f"Total: ${total_cost:,.2f}  -  {fin.get('total', 0)} dispensation(s)", ln=True)
    pdf.ln(2)
    fins = fin.get("records", [])
    if fins:
        _th(pdf, ["Date", "Patient", "Amount"], [TW * 0.2, TW * 0.5, TW * 0.3])
        for i, r in enumerate(fins[:15]):
            _tr(pdf, [r.get("date", ""), r.get("patient", ""),
                      f"${r.get('total_cost', 0):.2f}"],
                [TW * 0.2, TW * 0.5, TW * 0.3], i % 2)

    pdf.ln(4)
    _section(pdf, "Admissions")
    ar = adm.get("records", [])
    active = sum(1 for r in ar if not r.get("actual_discharge"))
    disch = sum(1 for r in ar if r.get("actual_discharge"))
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, f"Period: {adm.get('total', 0)}  -  Active: {active}  -  "
                   f"Discharged: {disch}  -  Avg stay: {avg_st}d", ln=True)
    pdf.ln(2)
    if ar:
        _th(pdf, ["Date", "Patient", "Room", "Floor", "Stay"],
            [TW * 0.2, TW * 0.3, TW * 0.15, TW * 0.1, TW * 0.1])
        for i, r in enumerate(ar[:15]):
            _tr(pdf, [r.get("admission_date", ""), r.get("patient", ""), r.get("room", ""),
                      r.get("floor", ""), r.get("stay_days", "") or ""],
                [TW * 0.2, TW * 0.3, TW * 0.15, TW * 0.1, TW * 0.1], i % 2)

    pdf.set_y(pdf.get_y() + 4)
    _section(pdf, "Recent Surgeries")
    sr = surg.get("records", [])
    if sr:
        _th(pdf, ["Date", "Procedure", "Patient", "Surgeon", "Dur."],
            [TW * 0.15, TW * 0.3, TW * 0.2, TW * 0.2, TW * 0.15])
        for i, r in enumerate(sr[:15]):
            _tr(pdf, [r.get("date", ""), r.get("procedure", ""), r.get("patient", ""),
                      r.get("surgeon", ""), r.get("duration", "")],
                [TW * 0.15, TW * 0.3, TW * 0.2, TW * 0.2, TW * 0.15], i % 2)

    _page_number(pdf)

    for i in range(1, pdf.pages_count + 1):
        pdf.page = i
        if i < 4:
            pdf.set_y(-15)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*GRAY)
            pdf.cell(0, 10, f"Sa Palomera Hospital  |  {i}/{{nb}}", align="C")

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
