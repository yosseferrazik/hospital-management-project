import tkinter as tk

from utils.ui_style import UIStyle
from views.main_interface import MainInterface


class HospitalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sa Palomera Hospital - Management System")
        self.root.configure(bg=UIStyle.BG)
        self.root.minsize(1280, 800)
        self.root.state("zoomed")
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.current_frame = None
        self.show_login()

    def toggle_fullscreen(self, _event=None):
        is_fullscreen = bool(self.root.attributes("-fullscreen"))
        if is_fullscreen:
            self.root.attributes("-fullscreen", False)
            self.root.state("zoomed")
        else:
            self.root.attributes("-fullscreen", True)

    def exit_fullscreen(self, _event=None):
        self.root.attributes("-fullscreen", False)
        self.root.state("zoomed")

    def _swap_frame(self, frame_factory):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_factory()

    def show_login(self):
        from views.login_view import LoginView

        self._swap_frame(lambda: LoginView(self.root, self))

    def show_register(self):
        from views.register_view import RegisterView

        self._swap_frame(lambda: RegisterView(self.root, self))

    def show_main_interface(self):
        self._swap_frame(lambda: MainInterface(self.root, self))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    HospitalApp().run()
