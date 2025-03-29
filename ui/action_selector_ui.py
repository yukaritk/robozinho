import customtkinter as ctk
from ui.price_update_screen import PriceUpdateScreen
from ui.transfer_request_screen import TransferRequestScreen

class ActionSelector:
    def __init__(self, parent_root):
        self.window = ctk.CTkToplevel(parent_root)
        self.window.title("Select Action")
        x = parent_root.winfo_x()
        y = parent_root.winfo_y()
        self.window.geometry(f"400x400+{x}+{y}")
        self.window.lift()
        self.window.protocol("WM_DELETE_WINDOW", parent_root.destroy)
        
        frame = ctk.CTkFrame(self.window, corner_radius=10)
        frame.pack(padx=20, pady=40, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Choose Action", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=(20, 10))

        btn_price = ctk.CTkButton(
            frame, text="Price Update", fg_color="#ec008c", hover_color="#bf0073",
            command=self.open_price_update_screen
        )
        btn_price.pack(pady=10)

        btn_transfer = ctk.CTkButton(
            frame, text="Transfer Request", fg_color="#ec008c", hover_color="#bf0073",
            command=self.open_transfer_request_screen
        )
        btn_transfer.pack(pady=10)



    def open_price_update_screen(self):
        PriceUpdateScreen(self.window)
        

    def open_transfer_request_screen(self):
        TransferRequestScreen(self.window)

        