# Fichier : gui/tasks_dashboard_view.py
# Description : Vue principale pour la gestion des tâches avec onglets.

import customtkinter as ctk
from .task_list import TaskListView
from .task_hebdo_list import TaskHebdoListView

class TasksDashboardView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Système d'onglets
        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.grid(row=0, column=0, sticky="nsew")

        self.tab_view.add("Tâches Ponctuelles")
        self.tab_view.add("Gestion Tâches Hebdomadaires")
        
        # Créer les vues pour chaque onglet
        self.punctual_tasks_view = TaskListView(self.tab_view.tab("Tâches Ponctuelles"), self.user_info)
        self.punctual_tasks_view.pack(expand=True, fill="both")
        
        self.hebdo_tasks_view = TaskHebdoListView(self.tab_view.tab("Gestion Tâches Hebdomadaires"), self.user_info)
        self.hebdo_tasks_view.pack(expand=True, fill="both")

    def refresh_list(self):
        """Appelle la méthode de rafraîchissement des vues contenues."""
        if hasattr(self.punctual_tasks_view, 'refresh_list'):
            self.punctual_tasks_view.refresh_list()
        if hasattr(self.hebdo_tasks_view, 'refresh_list'):
            self.hebdo_tasks_view.refresh_list()
