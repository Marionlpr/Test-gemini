# Fichier : gui/meal_count_view.py
# Description : Interface pour afficher le décompte des repas.

import customtkinter as ctk
from datetime import date, timedelta
from models.daily_life.daily_life import get_meal_counts_for_date
from .weekly_meal_summary_view import WeeklyMealSummaryView
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")

class MealCountView(ctk.CTkFrame):
    def __init__(self, parent, user_info, refresh_callback=None):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        self.current_date = date.today()
        self.service_id_filter = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cadre de navigation ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.create_nav_widgets()

        # --- Tableau des effectifs ---
        self.table_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray13"))
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.refresh_view()

    def set_service_filter(self, service_id):
        self.service_id_filter = service_id
        self.refresh_view()

    def create_nav_widgets(self):
        self.top_frame.grid_columnconfigure(1, weight=1)
        
        date_nav_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        date_nav_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        prev_day_button = ctk.CTkButton(date_nav_frame, text="< Jour Préc.", command=self.go_to_previous_day)
        prev_day_button.pack(side="left")
        next_day_button = ctk.CTkButton(date_nav_frame, text="Jour Suiv. >", command=self.go_to_next_day)
        next_day_button.pack(side="left", padx=10)

        self.date_label = ctk.CTkLabel(self.top_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.date_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        actions_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        weekly_summary_button = ctk.CTkButton(actions_frame, text="Récapitulatif Semaine", command=self.open_weekly_summary)
        weekly_summary_button.pack()

    def open_weekly_summary(self):
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        WeeklyMealSummaryView(self, start_of_week)

    def refresh_view(self):
        self.date_label.configure(text=self.current_date.strftime("%A %d %B %Y").capitalize())
        self.populate_meal_count_table()

    def populate_meal_count_table(self):
        for widget in self.table_frame.winfo_children(): widget.destroy()
        counts = get_meal_counts_for_date(self.current_date.isoformat(), service_id=self.service_id_filter)
        headers = ["Catégorie", "Normal", "Sans Porc", "Végétarien", "TOTAL"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=10, pady=5)
        
        for row_idx, cat_key, cat_name in [(1, 'jeunes', 'Jeunes'), (3, 'pros', 'Professionnels')]:
            for moment_idx, moment_key, moment_name in [(row_idx, 'midi', 'Midi'), (row_idx + 1, 'soir', 'Soir')]:
                ctk.CTkLabel(self.table_frame, text=f"{cat_name} ({moment_name})", font=ctk.CTkFont(weight="bold")).grid(row=moment_idx, column=0, padx=10, pady=5, sticky="w")
                moment_counts = counts.get(cat_key, {}).get(moment_key, {})
                for i, m_type in enumerate(['normal', 'sans_porc', 'vegetarien', 'total'], 1):
                    ctk.CTkLabel(self.table_frame, text=str(moment_counts.get(m_type, 0))).grid(row=moment_idx, column=i, padx=10, pady=5)
        
        total_font = ctk.CTkFont(weight="bold", size=14)
        for row_idx, moment_key, moment_name in [(5, 'midi', 'MIDI'), (6, 'soir', 'SOIR')]:
            ctk.CTkLabel(self.table_frame, text=f"TOTAL {moment_name}", font=total_font).grid(row=row_idx, column=0, padx=10, pady=(10,5), sticky="w")
            for i, m_type in enumerate(['normal', 'sans_porc', 'vegetarien', 'total'], 1):
                total_val = counts.get('jeunes', {}).get(moment_key, {}).get(m_type, 0) + counts.get('pros', {}).get(moment_key, {}).get(m_type, 0)
                ctk.CTkLabel(self.table_frame, text=str(total_val), font=total_font).grid(row=row_idx, column=i, padx=10, pady=(10,5))
        
        ctk.CTkFrame(self.table_frame, height=2, fg_color="gray50").grid(row=7, column=0, columnspan=5, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="TOTAL JOURNÉE", font=total_font).grid(row=8, column=0, padx=10, pady=5, sticky="w")
        for i, m_type in enumerate(['normal', 'sans_porc', 'vegetarien', 'total'], 1):
            total = sum(counts[cat][mom].get(m_type, 0) for cat in counts for mom in counts[cat])
            ctk.CTkLabel(self.table_frame, text=str(total), font=total_font).grid(row=8, column=i, padx=10, pady=5)

    def go_to_previous_day(self): self.current_date -= timedelta(days=1); self.refresh_view()
    def go_to_next_day(self): self.current_date += timedelta(days=1); self.refresh_view()
    def refresh_list(self): self.refresh_view()
