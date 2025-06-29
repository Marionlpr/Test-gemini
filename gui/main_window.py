# Fichier : gui/main_window.py (Version Stable)
# Description : Vue principale de l'application après connexion.

import customtkinter as ctk
from .dashboard_view import DashboardView
from .professionnals_list import ProfessionalsView
from .services_list import ServicesView
from .youngs_list import YoungsView
from .agenda_view import AgendaView 
from .transmissions_list import TransmissionsView
from .report_list import ReportsView
from .projet_p_list import ProjetPView
from .task_dashboard_view import TasksDashboardView
from .vehicle_list import VehicleListView
from .trip_list import TripListView
from .settings_view import SettingsView
from .daily_life_dashboard_view import DailyLifeDashboardView

class MainView(ctk.CTkFrame):
    def __init__(self, parent, user_info, logout_callback):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        self.logout_callback = logout_callback 
        self.views = {}
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.setup_ui()

    def setup_ui(self):
        """Crée et configure tous les widgets de l'interface principale."""
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_columnconfigure(0, weight=1) # Le menu ne s'étire pas en largeur

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  MENU", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        current_row = 1

        # --- Section Principale ---
        self.dashboard_button = self.create_nav_button("Tableau de Bord", self.show_dashboard_view)
        self.dashboard_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.agenda_button = self.create_nav_button("Agenda", self.show_agenda_view)
        self.agenda_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.daily_life_button = self.create_nav_button("Vie Quotidienne", self.show_daily_life_view)
        self.daily_life_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.tasks_button = self.create_nav_button("Gestion des Tâches", self.show_tasks_view)
        self.tasks_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.transmissions_button = self.create_nav_button("Transmissions", self.show_transmissions_view)
        self.transmissions_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.trips_button = self.create_nav_button("Trajets", self.show_trips_view)
        self.trips_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.youngs_button = self.create_nav_button("Suivi des Jeunes", self.show_youngs_view)
        self.youngs_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        
        # --- Section Écrits Professionnels ---
        self.ecrits_label = ctk.CTkLabel(self.navigation_frame, text="Écrits Professionnels", font=ctk.CTkFont(size=12, weight="bold"))
        self.ecrits_label.grid(row=current_row, column=0, padx=20, pady=(20, 5), sticky="w"); current_row += 1
        self.reports_button = self.create_nav_button("Rapports", self.show_reports_view)
        self.reports_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        self.projets_button = self.create_nav_button("Projets Personnalisés", self.show_projets_view)
        self.projets_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1

        # --- Section Gestion administrative ---
        if self.user_info[1] == 'gestion administrative':
            self.admin_label = ctk.CTkLabel(self.navigation_frame, text="Gestion Administrative", font=ctk.CTkFont(size=12, weight="bold"))
            self.admin_label.grid(row=current_row, column=0, padx=20, pady=(20, 5), sticky="w"); current_row += 1
            self.professionals_button = self.create_nav_button("Gestion Professionnels", self.show_professionals_view)
            self.professionals_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
            self.services_button = self.create_nav_button("Gestion Services", self.show_services_view)
            self.services_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
            self.vehicles_button = self.create_nav_button("Gestion Véhicules", self.show_vehicles_view)
            self.vehicles_button.grid(row=current_row, column=0, sticky="ew"); current_row += 1
        
        # --- Boutons du bas (Paramètres et Déconnexion) ---
        self.navigation_frame.grid_rowconfigure(current_row, weight=1) 
        
        self.settings_button = self.create_nav_button("⚙️ Paramètres", self.show_settings_view)
        self.settings_button.grid(row=current_row + 1, column=0, sticky="sw")
        
        # CORRECTION : Utilisation de grid au lieu de pack
        self.logout_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                           text="Déconnexion", fg_color="#D32F2F", text_color="white",
                                           hover_color="#B71C1C", anchor="w", command=self.logout_callback)
        self.logout_button.grid(row=current_row + 2, column=0, sticky="sew", pady=(5,0))
        
        # --- Conteneur pour la vue principale ---
        self.main_view_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_view_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_view_container.grid_rowconfigure(0, weight=1)
        self.main_view_container.grid_columnconfigure(0, weight=1)

        self.show_dashboard_view()

    def create_nav_button(self, text, command):
        return ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                             text=text, fg_color="transparent", text_color=("gray10", "gray90"),
                             hover_color=("gray70", "gray30"), anchor="w", command=command)

    def show_view(self, view_class_constructor, name):
        for view in self.views.values():
            view.grid_forget()
        
        if name not in self.views:
            self.views[name] = view_class_constructor(self.main_view_container)
        
        self.views[name].grid(row=0, column=0, sticky="nsew")
        if hasattr(self.views[name], 'refresh_list') and callable(getattr(self.views[name], 'refresh_list')):
            self.views[name].refresh_list()

    def show_dashboard_view(self): self.show_view(lambda parent: DashboardView(parent, self.user_info), "dashboard")
    def show_agenda_view(self): self.show_view(lambda parent: AgendaView(parent, self.user_info), "agenda")
    def show_daily_life_view(self): self.show_view(lambda parent: DailyLifeDashboardView(parent, self.user_info), "daily_life")
    def show_tasks_view(self): self.show_view(lambda parent: TasksDashboardView(parent, self.user_info), "tasks_dashboard")
    def show_transmissions_view(self): self.show_view(lambda parent: TransmissionsView(parent, self.user_info), "transmissions")
    def show_trips_view(self): self.show_view(lambda parent: TripListView(parent, self.user_info), "trips")
    def show_youngs_view(self): self.show_view(lambda parent: YoungsView(parent, self.user_info), "youngs")
    def show_reports_view(self): self.show_view(lambda parent: ReportsView(parent, self.user_info), "reports")
    def show_projets_view(self): self.show_view(lambda parent: ProjetPView(parent, self.user_info), "projets_p")
    def show_professionals_view(self): self.show_view(lambda parent: ProfessionalsView(parent, self.user_info), "professionals")
    def show_services_view(self): self.show_view(lambda parent: ServicesView(parent, self.user_info), "services")
    def show_vehicles_view(self): self.show_view(lambda parent: VehicleListView(parent, self.user_info), "vehicles")
    def show_settings_view(self): self.show_view(lambda parent: SettingsView(parent, self.user_info), "settings")

