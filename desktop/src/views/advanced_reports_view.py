"""Comprehensive analytics dashboard with multi-tab reports."""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta

from services.api_client import APIClient
from utils.session import Session
from utils.ui_style import UIStyle


class AdvancedReportsView:
    """Multi-tab advanced reporting with summary, visits, surgeries, admissions, medications, financial, radiology, and workload views."""

    def __init__(self, parent, app):
        """Initialize advanced reports view and build the UI."""
        self.parent = parent
        self.app = app
        self.api_client = APIClient(Session())
        self._is_destroyed = False
        self._pending_refresh = False

        self.page = UIStyle.page(self.parent)
        UIStyle.configure_ttk(self.page)
        self._build_ui()

    def _build_ui(self):
        """Build the filter bar, notebook tabs, and trigger initial data load."""
        UIStyle.section_header(
            self.page,
            "Advanced Reports",
            "Comprehensive hospital analytics and business intelligence",
        )

        filter_bar = tk.Frame(self.page, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1)
        filter_bar.pack(fill="x", padx=24, pady=(0, 16))
        inner = tk.Frame(filter_bar, bg=UIStyle.CARD_BG)
        inner.pack(fill="x", padx=20, pady=14)

        tk.Label(inner, text="From:", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK, font=UIStyle.FONT).pack(side="left")
        self.start_entry = UIStyle.form_entry(inner)
        self.start_entry.pack(side="left", padx=(6, 16))
        self.start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        tk.Label(inner, text="To:", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK, font=UIStyle.FONT).pack(side="left")
        self.end_entry = UIStyle.form_entry(inner)
        self.end_entry.pack(side="left", padx=(6, 16))
        self.end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        UIStyle.filled_button(inner, "Refresh All Reports", self.refresh_all).pack(side="left", padx=(6, 0))
        sep = tk.Frame(inner, bg=UIStyle.BORDER, width=1, height=24)
        sep.pack(side="left", padx=10)
        UIStyle.secondary_button(inner, "Download PDF", self.download_pdf).pack(side="left", padx=(0, 6))
        tk.Label(inner, text="(YYYY-MM-DD)", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, font=UIStyle.SMALL_FONT).pack(side="left", padx=(6, 0))

        self.notebook = ttk.Notebook(self.page)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        categories = [
            ("summary", "Summary", self._build_summary_tab),
            ("visits", "Visits", self._build_visits_tab),
            ("surgeries", "Surgeries", self._build_surgeries_tab),
            ("admissions", "Admissions", self._build_admissions_tab),
            ("medications", "Medications", self._build_medications_tab),
            ("financial", "Financial", self._build_financial_tab),
            ("radiology", "Radiology", self._build_radiology_tab),
            ("workload", "Doctor Workload", self._build_workload_tab),
        ]
        self.tabs = {}
        for key, label, builder in categories:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=label)
            builder(frame)
            self.tabs[key] = frame

        self._load_all()

    def _capture_date_params(self):
        """Return the start and end date from the filter entries."""
        return (self.start_entry.get().strip(), self.end_entry.get().strip())

    def _build_summary_tab(self, parent):
        """Build the summary tab with stat cards and extra panels."""
        self.summary_scroll, self.summary_content = UIStyle.create_scrollable_area(parent, bg=UIStyle.BG)
        self.summary_cards = tk.Frame(self.summary_content, bg=UIStyle.BG)
        self.summary_cards.pack(fill="x", padx=24, pady=(16, 8))
        self.summary_extra = tk.Frame(self.summary_content, bg=UIStyle.BG)
        self.summary_extra.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def _make_stat_card(self, parent, title, value, color, row, col):
        """Create a single stat display card with title, value, and color."""
        card = tk.Frame(parent, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1, width=200, height=110)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        card.grid_propagate(False)
        inner = tk.Frame(card, bg=UIStyle.CARD_BG)
        inner.pack(fill="both", expand=True, padx=16, pady=12)
        tk.Label(inner, text=title, font=UIStyle.SMALL_FONT, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, anchor="w").pack(anchor="w")
        tk.Label(inner, text=str(value), font=("Segoe UI", 22, "bold"), bg=UIStyle.CARD_BG, fg=color, anchor="w").pack(anchor="w", pady=(4, 0))

    def _build_filtered_tab(self, parent, labels, callback, count_label_attr, tree_attr):
        """Build a generic filtered tab with filter entries and a result tree."""
        top = tk.Frame(parent, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1)
        top.pack(fill="x", padx=24, pady=(16, 8))
        inner = tk.Frame(top, bg=UIStyle.CARD_BG)
        inner.pack(fill="x", padx=16, pady=10)

        entries = {}
        for text, attr in labels:
            tk.Label(inner, text=text, bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_DARK, font=UIStyle.FONT).pack(side="left")
            e = UIStyle.form_entry(inner)
            e.pack(side="left", padx=(6, 16), fill="x", expand=(text != ""))
            entries[attr] = e

        btn = UIStyle.filled_button(inner, "Filter", callback)
        btn.pack(side="left")

        cl = tk.Label(inner, text="", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, font=UIStyle.SMALL_FONT)
        cl.pack(side="right", padx=8)
        setattr(self, count_label_attr, cl)

        tree_frame = tk.Frame(parent, bg=UIStyle.BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(8, 24))
        setattr(self, tree_attr, tree_frame)
        return entries

    def _build_visits_tab(self, parent):
        """Build the visits report tab with specialty filter."""
        entries = self._build_filtered_tab(parent, [("Specialty:", "visits_spec")], self._filter_visits, "_visits_count", "_visits_tree")
        self._visits_spec = entries["visits_spec"]

    def _build_surgeries_tab(self, parent):
        """Build the surgeries report tab with procedure filter."""
        entries = self._build_filtered_tab(parent, [("Procedure:", "surg_proc")], self._filter_surgeries, "_surgeries_count", "_surgeries_tree")
        self._surg_proc = entries["surg_proc"]

    def _build_admissions_tab(self, parent):
        """Build the admissions report tab with floor filter."""
        entries = self._build_filtered_tab(parent, [("Floor ID:", "adm_floor")], self._filter_admissions, "_admissions_count", "_admissions_tree")
        self._adm_floor = entries["adm_floor"]

    def _build_medications_tab(self, parent):
        """Build the medications report tab."""
        top = tk.Frame(parent, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1)
        top.pack(fill="x", padx=24, pady=(16, 8))
        inner = tk.Frame(top, bg=UIStyle.CARD_BG)
        inner.pack(fill="x", padx=16, pady=10)
        self._med_count = tk.Label(inner, text="", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, font=UIStyle.SMALL_FONT)
        self._med_count.pack(side="right", padx=8)
        self._med_tree = tk.Frame(parent, bg=UIStyle.BG)
        self._med_tree.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def _build_financial_tab(self, parent):
        """Build the financial report tab with total cost display."""
        top = tk.Frame(parent, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1)
        top.pack(fill="x", padx=24, pady=(16, 8))
        inner = tk.Frame(top, bg=UIStyle.CARD_BG)
        inner.pack(fill="x", padx=16, pady=10)
        self._fin_total = tk.Label(inner, text="", bg=UIStyle.CARD_BG, fg=UIStyle.SUCCESS_GREEN, font=("Segoe UI", 14, "bold"))
        self._fin_total.pack(side="right", padx=8)
        self._fin_sub = tk.Label(inner, text="", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, font=UIStyle.SMALL_FONT)
        self._fin_sub.pack(side="right", padx=8)
        self._fin_tree = tk.Frame(parent, bg=UIStyle.BG)
        self._fin_tree.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def _build_radiology_tab(self, parent):
        """Build the radiology report tab with status filter."""
        entries = self._build_filtered_tab(parent, [("Status:", "rad_status")], self._filter_radiology, "_rad_count", "_rad_tree")
        self._rad_status = entries["rad_status"]

    def _build_workload_tab(self, parent):
        """Build the doctor workload report tab."""
        top = tk.Frame(parent, bg=UIStyle.CARD_BG, highlightbackground=UIStyle.BORDER, highlightthickness=1)
        top.pack(fill="x", padx=24, pady=(16, 8))
        inner = tk.Frame(top, bg=UIStyle.CARD_BG)
        inner.pack(fill="x", padx=16, pady=10)
        self._wl_count = tk.Label(inner, text="", bg=UIStyle.CARD_BG, fg=UIStyle.TEXT_LIGHT, font=UIStyle.SMALL_FONT)
        self._wl_count.pack(side="right", padx=8)
        self._wl_tree = tk.Frame(parent, bg=UIStyle.BG)
        self._wl_tree.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def refresh_all(self):
        """Reload all report data from the API."""
        self._load_all()

    def download_pdf(self):
        """Download the summary report as a PDF file."""
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="hospital_summary_report.pdf",
        )
        if not path:
            return

        def worker():
            try:
                result, error = self.api_client.download_summary_pdf(
                    start_date=start or None,
                    end_date=end or None,
                    save_path=path,
                )
                if self._is_destroyed:
                    return
                if error:
                    self.page.after(0, lambda: messagebox.showerror("Download Error", error))
                else:
                    self.page.after(0, lambda: messagebox.showinfo("Download Complete", "PDF saved to:\n" + result))
            except Exception as e:
                self.page.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _load_all(self):
        """Fetch all report data in parallel background threads."""
        dates = self._capture_date_params()
        self._call_async(self.api_client.get_report_summary, dates, self._render_summary)
        self._call_async(self.api_client.get_report_visits, dates, self._render_visits)
        self._call_async(self.api_client.get_report_surgeries, dates, self._render_surgeries)
        self._call_async(self.api_client.get_report_admissions, dates, self._render_admissions)
        self._call_async(self.api_client.get_report_medications, dates, self._render_medications)
        self._call_async(self.api_client.get_report_financial, dates, self._render_financial)
        self._call_async(self.api_client.get_report_radiology, dates, self._render_radiology)
        self._call_async(self.api_client.get_report_doctor_workload, dates, self._render_workload)

    def _call_async(self, api_method, dates, render_fn):
        """Execute an API method in a background thread and call render on completion."""
        start, end = dates

        def worker(s, e):
            try:
                data, error = api_method(start_date=s, end_date=e)
                if self._is_destroyed:
                    return
                if error:
                    self.page.after(0, lambda err=error: messagebox.showerror("Report Error", err))
                    return
                self.page.after(0, lambda d=data: render_fn(d))
            except Exception as e:
                if not self._is_destroyed:
                    self.page.after(0, lambda err=str(e): messagebox.showerror("Report Error", err))

        threading.Thread(target=worker, args=(start, end), daemon=True).start()

    def _filter_visits(self):
        """Filter visits report by specialty."""
        dates = self._capture_date_params()
        spec = self._visits_spec.get().strip() or None

        def worker(s, e, sp):
            try:
                data, error = self.api_client.get_report_visits(start_date=s, end_date=e, specialty=sp)
                if not error and not self._is_destroyed:
                    self.page.after(0, lambda d=data: self._render_visits(d))
            except Exception:
                pass

        threading.Thread(target=worker, args=(dates[0], dates[1], spec), daemon=True).start()

    def _filter_surgeries(self):
        """Filter surgeries report by procedure type."""
        dates = self._capture_date_params()
        proc = self._surg_proc.get().strip() or None

        def worker(s, e, p):
            try:
                data, error = self.api_client.get_report_surgeries(start_date=s, end_date=e, procedure_type=p)
                if not error and not self._is_destroyed:
                    self.page.after(0, lambda d=data: self._render_surgeries(d))
            except Exception:
                pass

        threading.Thread(target=worker, args=(dates[0], dates[1], proc), daemon=True).start()

    def _filter_admissions(self):
        """Filter admissions report by floor ID."""
        dates = self._capture_date_params()
        f = self._adm_floor.get().strip()
        floor_id = int(f) if f.isdigit() else None

        def worker(s, e, fid):
            try:
                data, error = self.api_client.get_report_admissions(start_date=s, end_date=e, floor_id=fid)
                if not error and not self._is_destroyed:
                    self.page.after(0, lambda d=data: self._render_admissions(d))
            except Exception:
                pass

        threading.Thread(target=worker, args=(dates[0], dates[1], floor_id), daemon=True).start()

    def _filter_radiology(self):
        """Filter radiology report by status."""
        dates = self._capture_date_params()
        status = self._rad_status.get().strip() or None

        def worker(s, e, st):
            try:
                data, error = self.api_client.get_report_radiology(start_date=s, end_date=e, status=st)
                if not error and not self._is_destroyed:
                    self.page.after(0, lambda d=data: self._render_radiology(d))
            except Exception:
                pass

        threading.Thread(target=worker, args=(dates[0], dates[1], status), daemon=True).start()

    def _fill_tree(self, tree_frame, columns, records, col_widths=None):
        """Render records into a Treeview widget within a container frame."""
        for widget in tree_frame.winfo_children():
            widget.destroy()
        if not records:
            tk.Label(tree_frame, text="No data available", font=UIStyle.SUBTITLE_FONT, bg=UIStyle.BG, fg=UIStyle.TEXT_LIGHT).pack(pady=20)
            return
        tree = ttk.Treeview(tree_frame, columns=columns, height=18, show="headings")
        for col in columns:
            w = (col_widths or {}).get(col, 150)
            h = col.replace("_", " ").title()
            tree.column(col, width=w, anchor="w")
            tree.heading(col, text=h)
        for rec in records:
            tree.insert("", "end", values=[rec.get(c, "") for c in columns])
        tree.pack(fill="both", expand=True)

        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        y_scroll.pack(side="right", fill="y")
        tree.configure(yscrollcommand=y_scroll.set)

    def _render_summary(self, data):
        """Render summary data with stat cards and top diagnoses/surgeries tables."""
        for w in self.summary_cards.winfo_children():
            w.destroy()
        for w in self.summary_extra.winfo_children():
            w.destroy()
        if not data:
            return

        period = data.get("period", {})
        tk.Label(self.summary_cards, text="Period: " + period.get('start', '') + "  to  " + period.get('end', ''),
                 font=UIStyle.SUBTITLE_FONT, bg=UIStyle.BG, fg=UIStyle.TEXT_LIGHT).pack(anchor="w", pady=(0, 8))

        c1 = tk.Frame(self.summary_cards, bg=UIStyle.BG)
        c1.pack(fill="x")
        for i in range(4):
            c1.columnconfigure(i, weight=1)

        t = data.get("totals", {})
        a = data.get("activity", {})
        o = data.get("occupancy", {})
        occ = o.get("occupancy_rate", 0)
        occ_color = UIStyle.SUCCESS_GREEN if occ < 80 else UIStyle.WARNING_ORANGE if occ < 95 else UIStyle.DANGER

        self._make_stat_card(c1, "Total Patients", t.get("patients", 0), UIStyle.ACCENT, 0, 0)
        self._make_stat_card(c1, "Total Staff", t.get("staff", 0), UIStyle.ACCENT, 0, 1)
        self._make_stat_card(c1, "Occupancy Rate", str(occ) + "%", occ_color, 0, 2)
        self._make_stat_card(c1, "Active Admissions", o.get("active_admissions", 0), UIStyle.WARNING_ORANGE, 0, 3)

        c2 = tk.Frame(self.summary_cards, bg=UIStyle.BG)
        c2.pack(fill="x", pady=(8, 0))
        for i in range(3):
            c2.columnconfigure(i, weight=1)
        self._make_stat_card(c2, "Visits (period)", a.get("visits", 0), UIStyle.ACCENT, 0, 0)
        self._make_stat_card(c2, "Surgeries (period)", a.get("surgeries", 0), "#7c3aed", 0, 1)
        self._make_stat_card(c2, "Admissions (period)", a.get("admissions", 0), UIStyle.WARNING_ORANGE, 0, 2)

        left = tk.Frame(self.summary_extra, bg=UIStyle.BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(self.summary_extra, bg=UIStyle.BG)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        tk.Label(left, text="Top Diagnoses", font=UIStyle.CARD_TITLE, bg=UIStyle.BG, fg=UIStyle.TEXT_DARK).pack(anchor="w", pady=(8, 8))
        dt = ttk.Treeview(left, columns=("Diagnosis", "Count"), height=10, show="headings")
        dt.column("Diagnosis", width=250, anchor="w"); dt.column("Count", width=80, anchor="center")
        dt.heading("Diagnosis", text="Diagnosis"); dt.heading("Count", text="Cases")
        for d in data.get("top_diagnoses", []):
            dt.insert("", "end", values=(d.get("diagnosis", ""), d.get("count", 0)))
        dt.pack(fill="both", expand=True)

        tk.Label(right, text="Surgeries by Type", font=UIStyle.CARD_TITLE, bg=UIStyle.BG, fg=UIStyle.TEXT_DARK).pack(anchor="w", pady=(8, 8))
        st = ttk.Treeview(right, columns=("Procedure", "Count"), height=10, show="headings")
        st.column("Procedure", width=250, anchor="w"); st.column("Count", width=80, anchor="center")
        st.heading("Procedure", text="Procedure Type"); st.heading("Count", text="Count")
        for s in data.get("surgeries_by_type", []):
            st.insert("", "end", values=(s.get("procedure", ""), s.get("count", 0)))
        st.pack(fill="both", expand=True)

    def _render_visits(self, data):
        """Render visits report data in the visits tab tree."""
        records = data.get("records", [])
        getattr(self, "_visits_count").config(text="Total: " + str(data.get('total', 0)) + " visits")
        self._fill_tree(getattr(self, "_visits_tree"),
                        ["date", "patient", "doctor", "specialty", "diagnosis"],
                        records, {"date": 140, "patient": 180, "doctor": 180, "specialty": 140, "diagnosis": 250})

    def _render_surgeries(self, data):
        """Render surgeries report data in the surgeries tab tree."""
        records = data.get("records", [])
        getattr(self, "_surgeries_count").config(text="Total: " + str(data.get('total', 0)) + " surgeries")
        self._fill_tree(getattr(self, "_surgeries_tree"),
                        ["date", "procedure", "patient", "surgeon", "theater", "duration"],
                        records, {"date": 110, "procedure": 200, "patient": 180, "surgeon": 180, "theater": 100, "duration": 90})

    def _render_admissions(self, data):
        """Render admissions report data in the admissions tab tree."""
        records = data.get("records", [])
        getattr(self, "_admissions_count").config(text="Total: " + str(data.get('total', 0)) + " admissions")
        self._fill_tree(getattr(self, "_admissions_tree"),
                        ["admission_date", "patient", "room", "floor", "expected_discharge", "actual_discharge", "stay_days"],
                        records, {"admission_date": 120, "patient": 180, "room": 80, "floor": 70, "expected_discharge": 120, "actual_discharge": 120, "stay_days": 80})

    def _render_medications(self, data):
        """Render medications report data in the medications tab tree."""
        records = data.get("records", [])
        self._med_count.config(text="Total medications: " + str(data.get('total', 0)))
        self._fill_tree(self._med_tree, ["medication", "prescriptions", "visits"],
                        records, {"medication": 300, "prescriptions": 120, "visits": 120})

    def _render_financial(self, data):
        """Render financial report data with total cost in the financial tab tree."""
        records = data.get("records", [])
        tc = data.get("total_cost", 0)
        self._fin_total.config(text="Total Cost: $" + "{:,.2f}".format(tc))
        self._fin_sub.config(text="Dispensations: " + str(data.get('total', 0)) + "  |")
        self._fill_tree(self._fin_tree, ["date", "patient", "total_cost"],
                        records, {"date": 140, "patient": 250, "total_cost": 120})

    def _render_radiology(self, data):
        """Render radiology report data in the radiology tab tree."""
        records = data.get("records", [])
        getattr(self, "_rad_count").config(text="Total: " + str(data.get('total', 0)) + " exams")
        self._fill_tree(getattr(self, "_rad_tree"),
                        ["exam_type", "status", "patient", "requesting_doctor", "requested_at", "performed_at", "has_report"],
                        records, {"exam_type": 150, "status": 100, "patient": 180, "requesting_doctor": 180, "requested_at": 150, "performed_at": 150, "has_report": 80})

    def _render_workload(self, data):
        """Render doctor workload report data in the workload tab tree."""
        records = data.get("records", [])
        self._wl_count.config(text="Doctors: " + str(data.get('total', 0)))
        self._fill_tree(self._wl_tree, ["doctor", "specialty", "visits", "surgeries", "patients"],
                        records, {"doctor": 200, "specialty": 150, "visits": 80, "surgeries": 90, "patients": 90})

    def destroy(self):
        """Clean up advanced reports view resources."""
        self._is_destroyed = True
        if hasattr(self, "page") and self.page.winfo_exists():
            self.page.destroy()
