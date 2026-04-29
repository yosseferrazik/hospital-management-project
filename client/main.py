import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from views.login_view import LoginView


class HospitalApp:
    # Paleta de diseño
    BG = "#f0f2f5"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sa Palomera Hospital - Management System")
        self.root.geometry("900x700")
        self.root.configure(bg=self.BG)
        self.root.minsize(800, 600)  # evita que las tarjetas se deformen

        # Icono (opcional, descomenta si tienes un archivo .ico en la carpeta)
        # self.root.iconbitmap("assets/icon.ico")

        self.center_window()

        self.current_frame = None
        self.show_login()

    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        from views.login_view import LoginView

        self.current_frame = LoginView(self.root, self)

    def show_register(self):
        if self.current_frame:
            self.current_frame.destroy()
        from views.register_view import RegisterView

        self.current_frame = RegisterView(self.root, self)

    def show_main_menu(self):
        if self.current_frame:
            self.current_frame.destroy()
        from views.main_menu import MainMenu

        self.current_frame = MainMenu(self.root, self)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HospitalApp()
    app.run()