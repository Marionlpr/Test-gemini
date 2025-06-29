# Fichier : app/main.py (Nouvelle Stratégie de Lancement Stable)
# Description : Point d'entrée et contrôleur principal de l'application.

import sys
import os
import customtkinter as ctk

# --- Correction Robuste du Chemin d'Importation ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ---------------------------------------------------

from gui.login import LoginFrame # On importe un Cadre (Frame) et non une Fenêtre
from gui.main_window import MainView
from models.database import database
from models.auth import auth
from models.settings import settings

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Appliquer les settings enregistrés
        loaded_settings = settings.load_settings()
        settings.apply_settings(loaded_settings)

        # Initialisation de la BDD
        database.initialize_database()
        auth.add_first_admin_user()

        self.current_frame = None
        self.show_login_view()
        
        # Gérer la fermeture de l'application
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_login_view(self):
        """Affiche la vue de connexion et configure la fenêtre pour elle."""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.title("Connexion - Gestionnaire MECS")
        
        # Centrage de la fenêtre de connexion
        window_width = 600
        window_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.resizable(False, False)
        self.state('normal') # S'assurer que la fenêtre est visible et non minimisée

        self.current_frame = LoginFrame(self, login_callback=self.show_main_view)
        self.current_frame.pack(expand=True, fill="both")

    def show_main_view(self, user_info):
        """Détruit la vue de connexion et affiche la vue principale."""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.title(f"Gestionnaire MECS - Connecté ({user_info[1]})")
        self.state('zoomed')
        self.minsize(600, 800)
        self.resizable(True, True)
        
        # Créer et afficher le nouveau cadre principal
        self.current_frame = MainView(self, user_info=user_info, logout_callback=self.logout)
        self.current_frame.pack(expand=True, fill="both")

    def logout(self):
        """Gère la déconnexion et retourne à l'écran de login."""
        self.show_login_view()
        window_width = 600
        window_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    def on_closing(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
