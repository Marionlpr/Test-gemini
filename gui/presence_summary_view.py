# Fichier : gui/presence_summary_view.py
# Description : Vue pour afficher une synthèse des présences sur une période.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
from models.daily_life.daily_life import get_presence_summary
from utils import date_util
from .calendar_popup import CalendarPopup # Importer le widget calendrier

class PresenceSummaryView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        self.service_id_filter = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cadre de contrôle ---
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # --- Sélecteur de date de début ---
        ctk.CTkLabel(control_frame, text="Du:").pack(side="left", padx=(10,5))
        start_date_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        start_date_frame.pack(side="left", padx=5)
        self.start_date_entry = ctk.CTkEntry(start_date_frame, placeholder_text="JJ-MM-AAAA")
        self.start_date_entry.insert(0, start_of_month.strftime('%d-%m-%Y'))
        self.start_date_entry.pack(side="left")
        ctk.CTkButton(start_date_frame, text="🗓️", width=35, command=lambda: self.open_calendar_for(self.start_date_entry)).pack(side="left", padx=5)
        
        # --- Sélecteur de date de fin ---
        ctk.CTkLabel(control_frame, text="Au:").pack(side="left", padx=(10,5))
        end_date_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        end_date_frame.pack(side="left", padx=5)
        self.end_date_entry = ctk.CTkEntry(end_date_frame, placeholder_text="JJ-MM-AAAA")
        self.end_date_entry.insert(0, today.strftime('%d-%m-%Y'))
        self.end_date_entry.pack(side="left")
        ctk.CTkButton(end_date_frame, text="🗓️", width=35, command=lambda: self.open_calendar_for(self.end_date_entry)).pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="Générer la Synthèse", command=self.populate_summary_table).pack(side="left", padx=10)

        # --- Tableau des résultats ---
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Synthèse des Présences")
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.populate_summary_table()
        
    def open_calendar_for(self, entry_widget):
        """Ouvre le popup calendrier pour un champ de saisie spécifique."""
        CalendarPopup(self, entry_widget=entry_widget)

    def set_service_filter(self, service_id):
        self.service_id_filter = service_id
        self.populate_summary_table()

    def populate_summary_table(self):
        """Remplit le tableau avec la synthèse des présences."""
        for widget in self.table_frame.winfo_children(): widget.destroy()

        try:
            start_date = date_util.format_date_to_iso(self.start_date_entry.get())
            end_date = date_util.format_date_to_iso(self.end_date_entry.get())
            if not start_date or not end_date:
                raise ValueError("Dates invalides")
        except (ValueError, TypeError):
            messagebox.showerror("Erreur", "Veuillez entrer des dates valides au format JJ-MM-AAAA.", parent=self)
            return

        summary_data = get_presence_summary(start_date, end_date, service_id=self.service_id_filter)
        
        headers = ["Jeune", "Présent", "Absent", "Permis Famille", "Fugue", "Hôpital"]
        for i, header in enumerate(headers):
            self.table_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=10, pady=5)
            
        for i, young_summary in enumerate(summary_data, start=1):
            ctk.CTkLabel(self.table_frame, text=young_summary.get('name')).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(young_summary.get('Présent', 0))).grid(row=i, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.table_frame, text=str(young_summary.get('Absent (journée)', 0))).grid(row=i, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.table_frame, text=str(young_summary.get('Permis famille', 0))).grid(row=i, column=3, padx=10, pady=5)
            ctk.CTkLabel(self.table_frame, text=str(young_summary.get('Fugue', 0))).grid(row=i, column=4, padx=10, pady=5)
            ctk.CTkLabel(self.table_frame, text=str(young_summary.get('Hôpital', 0))).grid(row=i, column=5, padx=10, pady=5)

    def refresh_list(self):
        self.populate_summary_table()
