# Fichier : gui/daily_presence_view.py
# Description : Interface pour gérer la présence et les repas des jeunes et des professionnels.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
from models.daily_life.daily_life import get_presence_for_date, save_day_presence, save_professional_meals
from models.permissions.permissions import get_all_users, get_users_for_service
from utils import date_util
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")

class DailyPresenceView(ctk.CTkFrame):
    def __init__(self, parent, user_info, refresh_callback=None):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        self.refresh_callback = refresh_callback 
        self.service_id_filter = None

        self.current_date = date.today()
        self.young_row_widgets = []
        self.pro_row_widgets = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Cadre des jeunes
        self.grid_rowconfigure(2, weight=1) # Cadre des pros

        # --- Cadre de navigation de date ---
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        nav_frame.grid_columnconfigure(1, weight=1)

        prev_day_button = ctk.CTkButton(nav_frame, text="<", width=40, command=self.go_to_previous_day)
        prev_day_button.pack(side="left", padx=10, pady=10)
        
        self.date_label = ctk.CTkLabel(nav_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.date_label.pack(side="left", expand=True)

        next_day_button = ctk.CTkButton(nav_frame, text=">", width=40, command=self.go_to_next_day)
        next_day_button.pack(side="right", padx=10, pady=10)

        # --- Cadres principaux pour les listes ---
        self.young_scroll_frame = ctk.CTkScrollableFrame(self, label_text="Présences et Repas des Jeunes")
        self.young_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.young_scroll_frame.grid_columnconfigure((1, 2, 3), weight=1)
        
        self.pro_scroll_frame = ctk.CTkScrollableFrame(self, label_text="Repas des Professionnels")
        self.pro_scroll_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.pro_scroll_frame.grid_columnconfigure((1, 2), weight=1)
        
        # --- Bouton de sauvegarde unique ---
        save_button = ctk.CTkButton(self, text="Enregistrer Toutes les Modifications", command=self.save_all_changes)
        save_button.grid(row=3, column=0, padx=10, pady=10)

        self.refresh_view()
        
    def set_service_filter(self, service_id):
        self.service_id_filter = service_id
        self.refresh_view()

    def refresh_view(self):
        """Met à jour l'affichage pour la date sélectionnée."""
        self.date_label.configure(text=self.current_date.strftime("%A %d %B %Y").capitalize())
        self.populate_youngs_presence()
        self.populate_pros_meals()
    
    def populate_youngs_presence(self):
        for widget in self.young_scroll_frame.winfo_children(): widget.destroy()
        self.young_row_widgets.clear()
        
        headers = ["Jeune", "Statut de Présence", "Repas Midi", "Repas Soir"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.young_scroll_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        day_data = get_presence_for_date(self.current_date.isoformat(), service_id=self.service_id_filter)
        presence_options = ['Présent (journée)', 'Présent (midi)', 'Présent (soir)', 'Absent (journée)', 'Permis famille', 'Fugue', 'Hôpital']
        meal_options = ['normal', 'sans_porc', 'vegetarien', 'aucun']

        for i, young_data in enumerate(day_data, start=1):
            row = {"young_id": young_data['young_id']}
            row['name_label'] = ctk.CTkLabel(self.young_scroll_frame, text=f"{young_data['prenom']} {young_data['nom'].upper()}")
            row['name_label'].grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            row['presence_menu'] = ctk.CTkOptionMenu(self.young_scroll_frame, values=presence_options, command=lambda c, y_id=row['young_id']: self.on_presence_change(c, y_id))
            status = young_data.get('presence_status', 'Présent (journée)')
            row['presence_menu'].set(status)
            row['presence_menu'].grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
            row['midi_menu'] = ctk.CTkOptionMenu(self.young_scroll_frame, values=meal_options)
            row['midi_menu'].set(young_data.get('repas_midi', 'normal'))
            row['midi_menu'].grid(row=i, column=2, padx=5, pady=5, sticky="ew")
            
            row['soir_menu'] = ctk.CTkOptionMenu(self.young_scroll_frame, values=meal_options)
            row['soir_menu'].set(young_data.get('repas_soir', 'normal'))
            row['soir_menu'].grid(row=i, column=3, padx=5, pady=5, sticky="ew")
            
            self.young_row_widgets.append(row)
            self.on_presence_change(status, young_data['young_id'])
            
    def populate_pros_meals(self):
        for widget in self.pro_scroll_frame.winfo_children(): widget.destroy()
        self.pro_row_widgets.clear()
        
        headers = ["Professionnel", "Repas Midi", "Repas Soir"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.pro_scroll_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        all_users = get_users_for_service(self.service_id_filter) if self.service_id_filter else get_all_users()
        meal_options = ['aucun', 'normal', 'sans_porc', 'vegetarien']
        for i, user in enumerate(all_users, start=1):
            widgets = {'user_id': user[0]}
            ctk.CTkLabel(self.pro_scroll_frame, text=f"{user[2]} {user[1].upper()}").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            widgets['midi_menu'] = ctk.CTkOptionMenu(self.pro_scroll_frame, values=meal_options); widgets['midi_menu'].grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            widgets['soir_menu'] = ctk.CTkOptionMenu(self.pro_scroll_frame, values=meal_options); widgets['soir_menu'].grid(row=i, column=2, padx=5, pady=5, sticky="ew")
            self.pro_row_widgets.append(widgets)

    def on_presence_change(self, choice, young_id):
        for row in self.young_row_widgets:
            if row['young_id'] == young_id:
                midi_state = "disabled"; soir_state = "disabled"
                if "Présent (journée)" in choice: midi_state = "normal"; soir_state = "normal"
                elif "Présent (midi)" in choice: midi_state = "normal"
                elif "Présent (soir)" in choice: soir_state = "normal"
                row['midi_menu'].configure(state=midi_state)
                row['soir_menu'].configure(state=soir_state)
                break

    def save_all_changes(self):
        """Récupère et sauvegarde toutes les données de la page."""
        youngs_data = []
        for row in self.young_row_widgets:
            status = row['presence_menu'].get()
            midi = row['midi_menu'].get() if row['midi_menu'].cget("state") == "normal" else 'aucun'
            soir = row['soir_menu'].get() if row['soir_menu'].cget("state") == "normal" else 'aucun'
            youngs_data.append({"young_id": row['young_id'], "presence_status": status, "repas_midi": midi, "repas_soir": soir})

        pros_data = []
        for row in self.pro_row_widgets:
            pros_data.append({'user_id': row['user_id'], 'repas_midi': row['midi_menu'].get(), 'repas_soir': row['soir_menu'].get()})

        success_youngs = save_day_presence(self.current_date.isoformat(), youngs_data)
        success_pros = save_professional_meals(self.current_date.isoformat(), pros_data)

        if success_youngs and success_pros:
            messagebox.showinfo("Succès", "Les informations ont été enregistrées.")
            if self.refresh_callback: self.refresh_callback()
        else:
            messagebox.showerror("Erreur", "Un problème est survenu lors de l'enregistrement.")

    def go_to_previous_day(self): self.current_date -= timedelta(days=1); self.refresh_view()
    def go_to_next_day(self): self.current_date += timedelta(days=1); self.refresh_view()
    def refresh_list(self): self.refresh_view()
