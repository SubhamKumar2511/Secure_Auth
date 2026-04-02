import tkinter as tk

from .auth_service import AuthService
from .database import DatabaseManager
from .gui.screens import AppUI
from .otp_service import OTPService


def run_app():
    db = DatabaseManager()
    otp_service = OTPService()
    auth_service = AuthService(db, otp_service)

    root = tk.Tk()
    root.option_add("*Font", "SegoeUI 10")
    AppUI(root, auth_service, db)
    root.mainloop()

