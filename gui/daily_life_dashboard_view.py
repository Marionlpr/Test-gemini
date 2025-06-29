# Fichier : gui/daily_life_dashboard_view.py
# Description : Vue principale pour la gestion de la vie quotidienne avec onglets.

import customtkinter as ctk
from .daily_presence_view import DailyPresenceView
from .meal_count_view import MealCountView
from .presence_summary_view import PresenceSummaryView
from models.services.services import get_all_services_for_form

class DailyLifeDashboardView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- CORRECTION: Barre de filtre commune en haut ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.control_frame, text="Filtrer par service :").pack(side="left", padx=(10,5), pady=10)
        
        self.services_map = {name: s_id for s_id, name in get_all_services_for_form()}
        service_names = ["Tous les services"] + list(self.services_map.keys())
        self.service_filter_menu = ctk.CTkOptionMenu(self.control_frame, values=service_names, command=self.on_filter_change)
        self.service_filter_menu.pack(side="left", padx=10, pady=10)

        # --- Système d'onglets ---
        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.grid(row=1, column=0, sticky="nsew")

        self.tab_view.add("Présence Journalière")
        self.tab_view.add("Effectif Repas")
        self.tab_view.add("Synthèse des Présences")
        
        self.presence_view = DailyPresenceView(self.tab_view.tab("Présence Journalière"), self.user_info)
        self.presence_view.pack(expand=True, fill="both")
        
        self.meal_count_view = MealCountView(self.tab_view.tab("Effectif Repas"), self.user_info)
        self.meal_count_view.pack(expand=True, fill="both")
        
        self.summary_view = PresenceSummaryView(self.tab_view.tab("Synthèse des Présences"), self.user_info)
        self.summary_view.pack(expand=True, fill="both")
        
        # Appliquer le filtre initial
        self.on_filter_change()

    def on_filter_change(self, choice=None):
        """Met à jour toutes les vues avec le nouveau filtre de service."""
        selected_service_name = self.service_filter_menu.get()
        service_id_filter = self.services_map.get(selected_service_name) if selected_service_name != "Tous les services" else None
        
        # On passe le filtre à chaque vue
        self.presence_view.set_service_filter(service_id_filter)
        self.meal_count_view.set_service_filter(service_id_filter)
        self.summary_view.set_service_filter(service_id_filter)

    def refresh_list(self):
        """Appelle la méthode de rafraîchissement de toutes les vues contenues."""
        self.on_filter_change()
