# Fichier : gui/settings.py
# Description : Interface graphique pour la gestion des paramètres.

import customtkinter as ctk
from tkinter import messagebox
from models.settings import settings

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        self.grid_columnconfigure(0, weight=1)
        self.current_settings = settings.load_settings()

        # Cadre pour les options, centré
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=40, padx=80, fill="both", expand=True)
        self.options_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(self.options_frame, text="Paramètres de l'Application", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10)

        # --- Sélection du thème d'apparence (Clair/Sombre) ---
        appearance_label = ctk.CTkLabel(self.options_frame, text="Apparence :")
        appearance_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.appearance_menu = ctk.CTkOptionMenu(self.options_frame, values=["Light", "Dark", "System"])
        self.appearance_menu.set(self.current_settings.get("appearance_mode", "System"))
        self.appearance_menu.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # --- Sélection du thème de couleur (simplifiée) ---
        color_label = ctk.CTkLabel(self.options_frame, text="Thème de couleur :")
        color_label.grid(row=2, column=0, padx=20, pady=20, sticky="e")
        
        available_themes = settings.get_available_themes()
        self.color_theme_menu = ctk.CTkOptionMenu(self.options_frame, values=available_themes)
        self.color_theme_menu.set(self.current_settings.get("color_theme", "blue"))
        self.color_theme_menu.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # --- Bouton de sauvegarde ---
        save_button = ctk.CTkButton(self.options_frame, text="Appliquer et Enregistrer", command=self.save_and_apply_settings)
        save_button.grid(row=3, column=0, columnspan=2, pady=40, padx=20)

    def save_and_apply_settings(self):
        """Sauvegarde les nouveaux paramètres et les applique immédiatement."""
        new_settings = {
            "appearance_mode": self.appearance_menu.get(),
            "color_theme": self.color_theme_menu.get()
        }
        
        if settings.save_settings(new_settings):
            settings.apply_settings(new_settings)
            messagebox.showinfo("Paramètres Enregistrés", "Les paramètres ont été mis à jour.")
        else:
            messagebox.showerror("Erreur", "Impossible de sauvegarder les paramètres.")

    def refresh_list(self):
        """Méthode de compatibilité, non utilisée ici."""
        pass
