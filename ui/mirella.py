import customtkinter as ctk

class LoginScreen:
    def __init__(self, data):
        self.root = ctk.CTk()
        self.root.title("Robo Login")
        self.root.geometry("400x400")

        self.data = data  # JSON com info de médico, paciente, etc.
        self.entries = {}  # Para armazenar os campos editáveis

        self.build_ui()

        self.root.mainloop()

    def build_ui(self):
        row = 0
        for key, value in self.data.items():
            # Label com nome da tag
            label = ctk.CTkLabel(self.root, text=key)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Campo de texto com valor atual do JSON
            entry = ctk.CTkEntry(self.root, width=200)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

            self.entries[key] = entry
            row += 1

        # Botão para salvar as alterações
        save_button = ctk.CTkButton(self.root, text="Salvar", command=self.save_data)
        save_button.grid(row=row, column=0, columnspan=2, pady=20)

    def save_data(self):
        for key, entry in self.entries.items():
            self.data[key] = entry.get()
        print("Dados atualizados:")
        print(self.data)

# Dados simulados (JSON)
data = {
    "Nome do Médico": "Dra. Tatiane",
    "Nome do Paciente": "Fabio Kawakami",
    "Data da Consulta": "2025-04-08",
    "Especialidade": "Neurologia"
}

# Roda a tela
LoginScreen(data)