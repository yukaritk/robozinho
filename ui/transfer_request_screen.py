from tkinter import filedialog
import customtkinter as ctk
from utils.option_provider import OperationProvider

class TransferRequestScreen:
    def __init__(self, parent_root):
        self.window = ctk.CTkToplevel(parent_root)
        self.window.title("Price Update")
        x = parent_root.winfo_x()
        y = parent_root.winfo_y()
        self.window.geometry(f"400x400+{x}+{y}")
        self.window.lift()
        self.window.grab_set()

        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self.window, corner_radius=10)
        frame.pack(padx=20, pady=40, fill="both", expand=True)

        title = ctk.CTkLabel(frame, text="Upload Transfer Excel", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(10, 20))

        self.entry_file_path = ctk.CTkEntry(frame, placeholder_text="Path to Excel File")
        self.entry_file_path.pack(pady=10, fill="x", padx=20)

        browse_button = ctk.CTkButton(
            frame,
            text="Browse",
            fg_color="#ec008c",
            hover_color="#bf0073",
            command=self.browse_file
        )
        browse_button.pack(pady=(10, 20))

        # Option dropdown BELOW file path
        self.dropdown = ctk.CTkComboBox(frame, values=OperationProvider.get_operations(), width=240)
        self.dropdown.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            self.entry_file_path.delete(0, "end")
            self.entry_file_path.insert(0, file_path)