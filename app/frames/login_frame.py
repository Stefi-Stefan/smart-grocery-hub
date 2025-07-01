import tkinter as tk
from tkinter import messagebox
from app.managers.user_manager import UserManager

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login_success, user_manager, save_session):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.user_manager = user_manager
        self.save_session = save_session
        self.is_register_mode = False
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Email:").pack(pady=(10, 0))
        self.email_entry = tk.Entry(self)
        self.email_entry.pack()

        tk.Label(self, text="Password:").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        if self.is_register_mode:
            tk.Label(self, text="Confirm Password:").pack(pady=(10, 0))
            self.confirm_password_entry = tk.Entry(self, show="*")
            self.confirm_password_entry.pack()

        self.message_label = tk.Label(self, text="", fg="red")
        self.message_label.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        if self.is_register_mode:
            tk.Button(btn_frame, text="Register", command=self.register).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Back to Login", command=self.toggle_mode).pack(side="left", padx=5)
        else:
            tk.Button(btn_frame, text="Login", command=self.login).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Create Account", command=self.toggle_mode).pack(side="left", padx=5)

    def toggle_mode(self):
        self.is_register_mode = not self.is_register_mode
        self.build_ui()
        self.message_label.config(text="")

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        if not email or not password:
            self.message_label.config(text="Please enter email and password.")
            return
        if self.user_manager.authenticate_user(email, password):
            self.save_session(email)
            self.on_login_success(email)
        else:
            self.message_label.config(text="Invalid credentials.")

    def register(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if not email or not password or not confirm_password:
            self.message_label.config(text="All fields required.")
            return
        if password != confirm_password:
            self.message_label.config(text="Passwords do not match.")
            return
        try:
            self.user_manager.register_user(email, password)
            messagebox.showinfo("Registration Successful", "You can now log in.")
            self.toggle_mode()
        except ValueError as e:
            self.message_label.config(text=str(e))