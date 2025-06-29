# Fichier : gui/weekly_meal_summary_view.py
# Description : Fenêtre pop-up affichant la synthèse des repas pour une semaine.

import customtkinter as ctk
from datetime import timedelta, date
from models.daily_life.daily_life import get_weekly_meal_summary
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible. L'affichage des dates pourrait être en anglais.")


class WeeklyMealSummaryView(ctk.CTkToplevel):
    def __init__(self, parent, start_of_week):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        
        self.title(f"Récapitulatif des repas pour la semaine du {start_of_week.strftime('%d/%m/%Y')}")
        self.geometry("900x550")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Synthèse Hebdomadaire des Repas")
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.populate_view(start_of_week)
        
    def populate_view(self, start_of_week):
        """Remplit le tableau avec les données de la semaine."""
        end_of_week = start_of_week + timedelta(days=6)
        summary_data = get_weekly_meal_summary(start_of_week, end_of_week)
        
        # En-têtes du tableau
        headers = ["Jour", "Catégorie", "Normal", "Sans Porc", "Végétarien", "TOTAL"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.scroll_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            
        row_idx = 1
        days = [start_of_week + timedelta(days=i) for i in range(7)]
        
        # Initialisation des totaux hebdomadaires
        weekly_totals = {'normal': 0, 'sans_porc': 0, 'vegetarien': 0, 'total': 0}
        
        for day in days:
            day_str = day.isoformat()
            day_name = day.strftime("%A %d/%m").capitalize()
            
            day_label = ctk.CTkLabel(self.scroll_frame, text=day_name, font=ctk.CTkFont(weight="bold"))
            day_label.grid(row=row_idx, column=0, rowspan=4, padx=10, pady=10, sticky="ns")

            daily_counts = summary_data.get(day_str, {})
            
            # Lignes pour chaque catégorie (Jeunes/Pros, Midi/Soir)
            self.create_summary_row(row_idx, "Jeunes (Midi)", daily_counts.get('jeunes', {}).get('midi', {}))
            row_idx += 1
            self.create_summary_row(row_idx, "Jeunes (Soir)", daily_counts.get('jeunes', {}).get('soir', {}))
            row_idx += 1
            self.create_summary_row(row_idx, "Professionnels (Midi)", daily_counts.get('pros', {}).get('midi', {}))
            row_idx += 1
            self.create_summary_row(row_idx, "Professionnels (Soir)", daily_counts.get('pros', {}).get('soir', {}))
            row_idx += 1
            
            # Calcul des totaux pour le jour et ajout aux totaux de la semaine
            for m_type in ['normal', 'sans_porc', 'vegetarien', 'total']:
                midi_total = daily_counts.get('jeunes', {}).get('midi', {}).get(m_type, 0) + daily_counts.get('pros', {}).get('midi', {}).get(m_type, 0)
                soir_total = daily_counts.get('jeunes', {}).get('soir', {}).get(m_type, 0) + daily_counts.get('pros', {}).get('soir', {}).get(m_type, 0)
                weekly_totals[m_type] += midi_total + soir_total
            
            if day != end_of_week:
                separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray50")
                separator.grid(row=row_idx, column=0, columnspan=len(headers), sticky="ew", pady=5, padx=5)
                row_idx += 1

        # --- Ligne finale des totaux de la semaine ---
        final_separator = ctk.CTkFrame(self.scroll_frame, height=4, fg_color="gray30")
        final_separator.grid(row=row_idx, column=0, columnspan=len(headers), sticky="ew", pady=10, padx=5)
        row_idx += 1
        
        total_label_font = ctk.CTkFont(weight="bold", size=14)
        ctk.CTkLabel(self.scroll_frame, text="TOTAL SEMAINE", font=total_label_font).grid(row=row_idx, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        for i, m_type in enumerate(['normal', 'sans_porc', 'vegetarien', 'total'], 2):
            ctk.CTkLabel(self.scroll_frame, text=str(weekly_totals[m_type]), font=total_label_font).grid(row=row_idx, column=i, padx=10, pady=5)
    
    def create_summary_row(self, row, category_name, counts):
        """Crée une ligne de données dans le tableau de synthèse."""
        ctk.CTkLabel(self.scroll_frame, text=category_name).grid(row=row, column=1, sticky="w", padx=5)
        for i, m_type in enumerate(['normal', 'sans_porc', 'vegetarien', 'total'], 2):
            ctk.CTkLabel(self.scroll_frame, text=str(counts.get(m_type, 0))).grid(row=row, column=i, padx=10)
