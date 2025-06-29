# Fichier : gui/login.py (Version CTkFrame Stable)
# Description : Cadre de connexion à l'application.

import customtkinter as ctk
from models.auth import auth 

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, login_callback):
        super().__init__(parent)
        
        self.login_callback = login_callback

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(main_frame, text="Authentification", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=(10, 20))

        self.username_entry = ctk.CTkEntry(main_frame, placeholder_text="Identifiant")
        self.username_entry.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Mot de passe", show="*")
        self.password_entry.grid(row=2, column=0, padx=30, pady=10, sticky="ew")

        login_button = ctk.CTkButton(main_frame, text="Se connecter", command=self.login_event)
        login_button.grid(row=3, column=0, padx=30, pady=20, sticky="ew")
        
        # Lier la touche Entrée à la fenêtre principale
        self.winfo_toplevel().bind('<Return>', lambda event: self.login_event())

        self.error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.error_label.grid(row=4, column=0, padx=10, pady=(0, 10))

        self.username_entry.focus()

    def login_event(self):
        """Gère la tentative de connexion."""
        identifiant = self.username_entry.get()
        password = self.password_entry.get()
        
        if not identifiant or not password:
            self.error_label.configure(text="Veuillez remplir tous les champs.")
            return

        user_data = auth.check_user(identifiant, password)

        if user_data:
            # Appelle la fonction de callback fournie par App
            self.login_callback(user_data)
        else:
            self.error_label.configure(text="Identifiant ou mot de passe incorrect.")
