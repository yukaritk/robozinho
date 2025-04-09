import customtkinter as ctk
from tkinter import filedialog
import os
import pandas as pd
import subprocess
from utils.helper_methods import HelperMethods
from logic.price_update import PriceUpdate

class PriceUpdateScreen:
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

        title = ctk.CTkLabel(frame, text="Upload Price Excel", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(10, 20))

        # Novo frame horizontal para o entry + botão
        path_frame = ctk.CTkFrame(frame)
        path_frame.pack(pady=10, fill="x", padx=20)

        self.entry_file_path = ctk.CTkEntry(path_frame, placeholder_text="Path to Excel File")
        self.entry_file_path.pack(side="left", fill="x", expand=True)

        browse_button = ctk.CTkButton(path_frame, text="...", width=28, fg_color="#8b8b8b", hover_color="#767676", command=self.browse_file)
        browse_button.pack(side="left")

        layout_button = ctk.CTkButton(frame, text="Layout", fg_color="#ec008c", hover_color="#bf0073", command=self.download_layout)
        layout_button.pack(pady=(10, 0), anchor="e", padx=20)
        
        start_button = ctk.CTkButton(frame, text="Iniciar", fg_color="#13aa7d", hover_color="#1b7c5f", command=self.iniciar_processo)
        start_button.pack(pady=(10, 0), anchor="e", padx=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            self.entry_file_path.delete(0, "end")
            self.entry_file_path.insert(0, file_path)

    def download_layout(self):
        try:
            # Defina o nome do arquivo e o caminho para a pasta de downloads
            download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            file_path = os.path.join(download_folder, "Layout_alteracao_preco.xlsx")
            
            # Defina os nomes das colunas conforme a imagem
            colunas = [
                "Tipo do Codigo", "Produto/Grupo", "Vl. Custo", "Vl. Revenda", "Loja/Grupo", "Data inicio" ,"Status"
            ]

            # Cria um dataframe vazio com as colunas desejadas
            df = pd.DataFrame(columns=colunas)

            # Salva em Excel
            df.to_excel(file_path, index=False, engine='openpyxl')

            # Abre a pasta de downloads no Windows
            subprocess.Popen(f'explorer "{download_folder}"')

            print("Layout baixado com sucesso!")
        except Exception as e:
            print(f"Erro ao baixar o layout: {e}")

    def iniciar_processo(self):
        caminho = self.entry_file_path.get()
        if not caminho:
            HelperMethods.notificar("Erro", "⚠️ Selecione o arquivo e a operação!")
            return
        price_update = PriceUpdate(caminho)
        price_update.analisar_planilha()