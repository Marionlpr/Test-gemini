# Fichier : gui/dashboard_view.py
# Description : Interface graphique du tableau de bord dynamique et harmonieuse.

import customtkinter as ctk
from datetime import date, datetime
import locale

# CORRECTION GLOBALE: Imports directs et spécifiques des fonctions pour éviter les ambiguïtés
from models.events.events import get_events_for_period
from models.tasks.tasks import get_all_tasks_with_details
from models.transmissions.transmissions import get_latest_transmissions
from models.permissions.permissions import get_user_details
from utils import date_util

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        """
        Initialise la vue du tableau de bord.
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info
        
        user_details = get_user_details(user_id)
        self.user_service_id = user_details[9] if user_details and len(user_details) > 9 else None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.color_map = {"vert": "#2E7D32", "orange": "#FF8F00", "rouge": "#C62828", "gris": "gray50"}

        self.title_label = ctk.CTkLabel(self, text=f"Tableau de Bord - {date.today().strftime('%A %d %B %Y').capitalize()}",
                                        font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="w")

        self.agenda_frame = ctk.CTkScrollableFrame(self, label_text="🗓️  Agenda du Jour")
        self.agenda_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")
        
        self.right_column_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_column_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=0)
        self.right_column_frame.grid_columnconfigure(0, weight=1)
        self.right_column_frame.grid_rowconfigure(0, weight=1) 
        self.right_column_frame.grid_rowconfigure(1, weight=2) 

        self.urgent_tasks_frame = ctk.CTkScrollableFrame(self.right_column_frame, label_text="🔥  Tâches Ponctuelles Urgentes")
        self.urgent_tasks_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        self.transmissions_frame = ctk.CTkScrollableFrame(self.right_column_frame, label_text="💬  Dernières Transmissions")
        self.transmissions_frame.grid(row=1, column=0, sticky="nsew")

        self.refresh_list()

    def refresh_list(self):
        """Met à jour toutes les sections du tableau de bord."""
        service_filter = self.user_service_id if self.user_level == 'standard' else None
        
        self.populate_agenda_today(service_filter)
        self.populate_urgent_tasks(service_filter)
        self.populate_latest_transmissions(service_filter)

    def populate_agenda_today(self, service_id):
        for widget in self.agenda_frame.winfo_children():
            widget.destroy()
            
        today_iso = date.today().isoformat()
        events_data = get_events_for_period(today_iso, today_iso, service_id=service_id)
        
        if not events_data:
            ctk.CTkLabel(self.agenda_frame, text="Aucun événement pour votre service aujourd'hui.", text_color="gray").pack(pady=20)
            return

        for event in events_data:
            debut_dt = datetime.fromisoformat(event['debut_datetime'])
            nom = event['nom_evenement']
            young_names = event.get('young_names')
            
            text = f"{debut_dt.strftime('%H:%M')} - {nom}"
            if young_names:
                text += f"  ({young_names})"
                
            event_label = ctk.CTkLabel(self.agenda_frame, text=text, anchor="w")
            event_label.pack(fill="x", padx=10, pady=4)

    def populate_urgent_tasks(self, service_id):
        for widget in self.urgent_tasks_frame.winfo_children(): widget.destroy()
        all_tasks_data = get_all_tasks_with_details(service_id=service_id)
        urgent_tasks = [task for task in all_tasks_data if task.get('statut') == 'urgent']
        if not urgent_tasks:
            ctk.CTkLabel(self.urgent_tasks_frame, text="Aucune tâche urgente.", text_color="gray").pack(pady=20)
            return
        for task in urgent_tasks:
            date_limite_fr = date_util.format_date_to_french(task['date_limite'])
            task_frame = ctk.CTkFrame(self.urgent_tasks_frame, fg_color="transparent")
            task_frame.pack(fill="x", padx=5, pady=5)
            ctk.CTkLabel(task_frame, text=f"Limite au {date_limite_fr}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#D32F2F").pack(anchor="w", padx=10)
            ctk.CTkLabel(task_frame, text=task['tache_a_realiser'], anchor="w", justify="left").pack(fill="x", anchor="w", padx=10, pady=(0,5))
            
    def populate_latest_transmissions(self, service_id):
        for widget in self.transmissions_frame.winfo_children(): widget.destroy()
        latest_transmissions = get_latest_transmissions(limit=15, service_id=service_id)
        if not latest_transmissions:
            ctk.CTkLabel(self.transmissions_frame, text="Aucune transmission récente.", text_color="gray").pack(pady=20)
            return
        for trans in latest_transmissions:
            trans_frame = ctk.CTkFrame(self.transmissions_frame, fg_color="transparent")
            trans_frame.pack(fill="x", padx=5, pady=(5, 10))
            trans_frame.grid_columnconfigure(1, weight=1) 
            
            color_dot = ctk.CTkFrame(trans_frame, fg_color=self.color_map.get(trans.get('couleur'), "gray50"), width=10, height=10, corner_radius=5)
            color_dot.grid(row=0, column=0, rowspan=3, padx=(5,10), sticky="ns")

            dt_obj = datetime.fromisoformat(trans['datetime_transmission'])
            header_text = f"{dt_obj.strftime('%d/%m %H:%M')} - {trans['nom_service']} - par {trans['user_prenom']}"
            ctk.CTkLabel(trans_frame, text=header_text, font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").grid(row=0, column=1, sticky="w")
            
            ctk.CTkLabel(trans_frame, text=f"Concernés : {trans.get('linked_youngs', 'Général')}", font=ctk.CTkFont(size=11, weight="bold")).grid(row=1, column=1, sticky="w")
            ctk.CTkLabel(trans_frame, text=trans['contenu'], wraplength=300, justify="left", anchor="w").grid(row=2, column=1, sticky="w", pady=(2,0))
