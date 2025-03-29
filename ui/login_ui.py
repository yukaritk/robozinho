import customtkinter as ctk
import os
from ui.action_selector_ui import ActionSelector

CREDENTIAL_FILE = "credentials.txt"

class LoginScreen:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Robo Login")
        self.root.geometry("400x400")

        self.login, self.password = self.load_credentials()

        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self.root, corner_radius=10)
        frame.pack(padx=20, pady=40, fill="both", expand=True)

        title = ctk.CTkLabel(frame, text="Login", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(20, 10))

        self.entry_login = ctk.CTkEntry(frame, placeholder_text="Usuario")
        self.entry_login.pack(pady=10)
        if self.login:
            self.entry_login.insert(0, self.login)

        self.entry_password = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        self.entry_password.pack(pady=10)
        if self.password:
            self.entry_password.insert(0, self.password)

        btn = ctk.CTkButton(frame,text="Confirm",command=self.confirm_credentials,fg_color="#ec008c",hover_color="#bf0073",text_color="white")
        btn.pack(pady=20)

    def load_credentials(self):
        if os.path.exists(CREDENTIAL_FILE):
            with open(CREDENTIAL_FILE, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    return lines[0].strip(), lines[1].strip()
        return "", ""

    def save_credentials(self):
        with open(CREDENTIAL_FILE, "w") as f:
            f.write(f"{self.entry_login.get()}\n{self.entry_password.get()}")

    def confirm_credentials(self):
        self.save_credentials()
        ActionSelector(self.root)
        self.root.withdraw()



    def run(self):
        self.root.mainloop()
