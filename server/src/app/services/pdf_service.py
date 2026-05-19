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


def _sec(pdf, t, y=None):
    if y: pdf.set_y(y)
    pdf.set_x(M)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 6, t, ln=True)
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    pdf.line(M, pdf.get_y() + 1, PW - M, pdf.get_y() + 1)
    pdf.ln(3)


def _th(pdf, cols, ws):
    pdf.set_fill_color(31, 41, 55)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7.5)
    for i, c in enumerate(cols):
        pdf.cell(ws[i], 5.5, c, border=1, fill=True, align="C")
    pdf.ln()


def _tr(pdf, vs, ws, fill=False):
    if fill:
        pdf.set_fill_color(245, 247, 250)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(31, 41, 55)
    pdf.set_font("Helvetica", "", 7.5)
    for i, v in enumerate(vs):
        a = "C" if i else "L"
        pdf.cell(ws[i], 5, str(v), border=1, fill=True, align=a)
    pdf.ln()


def _kpi(pdf, l, v, x, y, w, c=None):
    pdf.set_xy(x, y)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(209, 213, 219)
    pdf.rect(x, y, w, 24, "DF")
    pdf.set_xy(x, y + 2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(w, 4, l, align="C", ln=True)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*(c or (31, 41, 55)))
    pdf.cell(w, 8, str(v), align="C", ln=True)


def _avg_stay(recs):
    ds = [r.get("stay_days") for r in recs if r.get("stay_days") is not None]
    return round(sum(ds) / len(ds), 1) if ds else 0


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

    # PAGE 1
    pdf.add_page()
    pdf.set_fill_color(31, 41, 55)
    pdf.rect(0, 0, PW, 36, "F")
    pdf.set_y(7)
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "Sa Palomera Hospital", align="C", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Executive Summary Report", align="C", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(0, 5, f"{ps}  to  {pe}  |  Generated {now}", align="C", ln=True)

    pdf.set_y(44)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 5, "Executive Overview", ln=True)
    ov = (
        f"Period: {ps} to {pe}. "
        f"The hospital recorded {a.get('visits',0)} visits, {a.get('surgeries',0)} surgeries, "
        f"and {a.get('admissions',0)} admissions. "
        f"Serving {t.get('patients',0)} patients with {t.get('staff',0)} staff "
        f"({t.get('doctors',0)} doctors, {t.get('nurses',0)} nurses). "
        f"Bed occupancy: {occ_r}% ({o.get('active_admissions',0)} of {o.get('total_rooms',0)} beds, "
        f"avg stay {avg_st} days). "
        f"Pharmacy costs: ${total_cost:,.2f}."
    )
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(75, 85, 99)
    pdf.multi_cell(0, 4, ov, align="J")
    pdf.ln(2)

    cw = TW / 4
    ky = pdf.get_y()
    occ_c = (5, 150, 105) if occ_r < 80 else (245, 158, 11) if occ_r < 95 else (220, 38, 38)
    _kpi(pdf, "Patients", t.get("patients",0), M, ky, cw)
    _kpi(pdf, "Staff", t.get("staff",0), M+cw, ky, cw)
    _kpi(pdf, "Occupancy", f"{occ_r}%", M+cw*2, ky, cw, occ_c)
    _kpi(pdf, "Active Adm.", o.get("active_admissions",0), M+cw*3, ky, cw, (245,158,11))
    ky2 = ky + 28
    _kpi(pdf, f"Visits", a.get("visits",0), M, ky2, cw)
    _kpi(pdf, f"Surgeries", a.get("surgeries",0), M+cw, ky2, cw, (124,58,237))
    _kpi(pdf, f"Admissions", a.get("admissions",0), M+cw*2, ky2, cw, (245,158,11))
    _kpi(pdf, f"Costs", f"${total_cost:,.0f}", M+cw*3, ky2, cw, (5,150,105))

    pdf.set_y(ky2 + 34)
    _sec(pdf, "Top Diagnoses")
    dd = data.get("top_diagnoses", [])
    if dd:
        _th(pdf, ["Diagnosis", "Cases"], [TW*0.7, TW*0.3])
        for i, d in enumerate(dd[:10]):
            _tr(pdf, [d.get("diagnosis",""), d.get("count",0)], [TW*0.7, TW*0.3], i%2)
    pdf.ln(2)

    _sec(pdf, "Surgeries by Type")
    st = data.get("surgeries_by_type", [])
    if st:
        _th(pdf, ["Procedure", "Count"], [TW*0.7, TW*0.3])
        for i, s in enumerate(st[:10]):
            _tr(pdf, [s.get("procedure",""), s.get("count",0)], [TW*0.7, TW*0.3], i%2)

    # PAGE 2
    pdf.add_page()
    pdf.set_fill_color(31, 41, 55)
    pdf.rect(0, 0, PW, 14, "F")
    pdf.set_y(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "Clinical Activity Details", align="C", ln=True)

    pdf.set_y(20)
    _sec(pdf, "Top Doctors by Workload")
    docs = wl.get("records", [])
    if docs:
        _th(pdf, ["Doctor","Specialty","Visits","Surg.","Pts"],
            [TW*0.3, TW*0.2, TW*0.15, TW*0.15, TW*0.2])
        for i, d in enumerate(docs[:12]):
            _tr(pdf, [d.get("doctor",""), d.get("specialty",""),
                d.get("visits",0), d.get("surgeries",0), d.get("patients",0)],
                [TW*0.3, TW*0.2, TW*0.15, TW*0.15, TW*0.2], i%2)

    pdf.set_y(pdf.get_y() + 5)
    _sec(pdf, "Most Prescribed Medications")
    mds = med.get("records", [])
    if mds:
        _th(pdf, ["Medication", "Rx", "Visits"], [TW*0.5, TW*0.25, TW*0.25])
        for i, m in enumerate(mds[:12]):
            _tr(pdf, [m.get("medication",""), m.get("prescriptions",0), m.get("visits",0)],
                [TW*0.5, TW*0.25, TW*0.25], i%2)

    pdf.set_y(pdf.get_y() + 5)
    _sec(pdf, "Radiology Exams by Status")
    rr = rad.get("records", [])
    if rr:
        sc = {}
        for r in rr:
            s = r.get("status", "UNKNOWN")
            sc[s] = sc.get(s, 0) + 1
        _th(pdf, ["Status", "Count"], [TW*0.7, TW*0.3])
        for i, (st, cnt) in enumerate(sorted(sc.items())):
            _tr(pdf, [st, cnt], [TW*0.7, TW*0.3], i%2)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 5, f"Total exams: {rad.get('total',0)}", ln=True)

    # PAGE 3
    pdf.add_page()
    pdf.set_fill_color(31, 41, 55)
    pdf.rect(0, 0, PW, 14, "F")
    pdf.set_y(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "Financial & Operational Details", align="C", ln=True)

    pdf.set_y(20)
    _sec(pdf, "Pharmacy Dispensations")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(5, 150, 105)
    pdf.cell(0, 5, f"Total Cost: ${total_cost:,.2f}  ({fin.get('total',0)} dispensations)", ln=True)
    pdf.ln(2)
    fins = fin.get("records", [])
    if fins:
        _th(pdf, ["Date","Patient","Cost"], [TW*0.2, TW*0.5, TW*0.3])
        for i, r in enumerate(fins[:15]):
            _tr(pdf, [r.get("date",""), r.get("patient",""), f"${r.get('total_cost',0):.2f}"],
                [TW*0.2, TW*0.5, TW*0.3], i%2)

    pdf.ln(3)
    _sec(pdf, "Admissions Overview")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(75, 85, 99)
    ar = adm.get("records", [])
    active = sum(1 for r in ar if not r.get("actual_discharge"))
    disch = sum(1 for r in ar if r.get("actual_discharge"))
    pdf.cell(0, 5, f"Total: {adm.get('total',0)}  |  Active: {active}  |  Discharged: {disch}  |  Avg stay: {avg_st}d", ln=True)
    pdf.ln(2)
    if ar:
        _th(pdf, ["Date","Patient","Room","Floor","Stay(d)"],
            [TW*0.2, TW*0.3, TW*0.15, TW*0.1, TW*0.1])
        for i, r in enumerate(ar[:15]):
            _tr(pdf, [r.get("admission_date",""), r.get("patient",""), r.get("room",""),
                r.get("floor",""), r.get("stay_days","") or ""],
                [TW*0.2, TW*0.3, TW*0.15, TW*0.1, TW*0.1], i%2)

    pdf.set_y(pdf.get_y() + 4)
    _sec(pdf, "Recent Surgeries")
    sr = surg.get("records", [])
    if sr:
        _th(pdf, ["Date","Procedure","Patient","Surgeon","Dur."],
            [TW*0.15, TW*0.3, TW*0.2, TW*0.2, TW*0.15])
        for i, r in enumerate(sr[:15]):
            _tr(pdf, [r.get("date",""), r.get("procedure",""), r.get("patient",""),
                r.get("surgeon",""), r.get("duration","")],
                [TW*0.15, TW*0.3, TW*0.2, TW*0.2, TW*0.15], i%2)

    for i in range(1, pdf.pages_count + 1):
        pdf.page = i
        pdf.set_y(-15)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(156, 163, 175)
        pdf.cell(0, 10, f"Sa Palomera Hospital  |  Page {i}/{{nb}}", align="C")

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
