import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from modules import auth
from db import postgres as db
from db.cache import cache

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HospitalApp:
    def __init__(self):
        self.current_user = None
        self.root = ctk.CTk()
        self.root.title("Hospital Sa Palomera - Management System")
        
        # Set 16:9 Aspect Ratio
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        if not db.test_connection():
            messagebox.showerror("Conn Error", "Check .env and PostgreSQL status.")
            self.root.destroy()
            return
        
        self.setup_main_container()
        self.show_login()

    def setup_main_container(self):
        """Initialize main layout containers"""
        self.main_container = ctk.CTkFrame(self.root, fg_color="#f8f9fa", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

    def update_clock(self):
        """Live clock feature for header"""
        if hasattr(self, 'time_label'):
            now = datetime.now().strftime("%H:%M:%S")
            self.time_label.configure(text=now)
            self.root.after(1000, self.update_clock)

    def create_header(self, title_text):
        """Consistent header for all authenticated views"""
        header = ctk.CTkFrame(self.main_container, height=60, corner_radius=0, fg_color="#2c3e50")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text=title_text, font=("Segoe UI", 20, "bold"), text_color="white").pack(side="left", padx=20)
        
        # Session Info & Clock
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(side="right", padx=20)

        self.time_label = ctk.CTkLabel(info_frame, text="", font=("Segoe UI", 12), text_color="#bdc3c7")
        self.time_label.pack(side="right", padx=(10, 0))
        
        user_text = f"👤 {self.current_user['username']} ({self.current_user['role']})"
        ctk.CTkLabel(info_frame, text=user_text, font=("Segoe UI", 12, "bold"), text_color="#3498db").pack(side="right")
        
        self.update_clock()

    def show_login(self):
        """Clean login interface"""
        for widget in self.main_container.winfo_children(): widget.destroy()

        login_box = ctk.CTkFrame(self.main_container, width=400, height=500, corner_radius=15, fg_color="white")
        login_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(login_box, text="HOSPITAL SA PALOMERA", font=("Segoe UI", 22, "bold"), text_color="#2c3e50").pack(pady=(40, 5))
        ctk.CTkLabel(login_box, text="System Authentication", font=("Segoe UI", 12), text_color="#7f8c8d").pack(pady=(0, 30))

        self.username_entry = ctk.CTkEntry(login_box, width=300, height=45, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(login_box, width=300, height=45, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(login_box, text="Login", width=300, height=45, font=("Segoe UI", 14, "bold"), command=self.do_login)
        self.login_btn.pack(pady=30)

    def do_login(self):
        user, error = auth.login(self.username_entry.get(), self.password_entry.get())
        if user:
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showwarning("Auth Failed", error)

    def show_dashboard(self):
        """Primary tabbed interface for scalability"""
        for widget in self.main_container.winfo_children(): widget.destroy()
        
        self.create_header("MANAGEMENT DASHBOARD")

        # Tab Navigation System
        self.tabview = ctk.CTkTabview(self.main_container, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Define tabs based on role
        tabs = ["Overview", "Patients", "Appointments", "Reports"]
        if self.current_user['role'] == 'ADMIN':
            tabs.extend(["Staff Management", "System Settings"])
        
        for tab in tabs:
            self.tabview.add(tab)
            self.build_tab_content(tab)

        # Logout button in its own frame
        ctk.CTkButton(self.main_container, text="Logout", fg_color="#e74c3c", hover_color="#c0392b", 
                      width=100, command=self.logout).pack(side="bottom", pady=10)

    def build_tab_content(self, name):
        """Construct content for each tab dynamically"""
        parent = self.tabview.tab(name)
        
        # Placeholder for future development
        ctk.CTkLabel(parent, text=f"{name} Module", font=("Segoe UI", 24, "bold"), text_color="#2c3e50").pack(pady=20)
        
        if name == "Overview":
            self.draw_stats_grid(parent)
        else:
            ctk.CTkLabel(parent, text="Module content under construction...", font=("Segoe UI", 14), text_color="#7f8c8d").pack()

    def draw_stats_grid(self, parent):
        """Visual data cards for the Overview tab"""
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", padx=50, pady=20)

        stats = [("Staff", "156"), ("Patients", "1,234"), ("Active", "89")]
        for i, (label, val) in enumerate(stats):
            card = ctk.CTkFrame(grid, fg_color="white", width=250, height=150, corner_radius=12)
            card.grid(row=0, column=i, padx=20, pady=10)
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=val, font=("Segoe UI", 32, "bold"), text_color="#3498db").pack(pady=(30, 0))
            ctk.CTkLabel(card, text=label, font=("Segoe UI", 14), text_color="#7f8c8d").pack()

    def logout(self):
        if messagebox.askyesno("Logout", "Confirm session termination?"):
            cache.invalidate()
            self.current_user = None
            self.show_login()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HospitalApp()
    app.run()