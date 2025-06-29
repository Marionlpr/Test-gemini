# Fichier : gui/event_form.py
# Description : Fenêtre modale pour ajouter ou modifier un événement.

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
# CORRECTION: Imports directs et spécifiques pour éviter les conflits
from models.events.events import add_event, update_event, get_event_details
from models.youngs.youngs import get_all_youngs
from models.permissions.permissions import get_all_users

class EventForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, event_id=None, initial_date=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.event_id = event_id
        self.result = False

        self.title("Ajouter un Événement" if event_id is None else "Modifier un Événement")
        self.geometry("700x750")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        self.youngs_frame = ctk.CTkScrollableFrame(self, label_text="Jeunes concernés")
        self.youngs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=2, column=0, padx=20, pady=20)

        self.widgets = {}
        self.young_checkboxes = {}
        self.professionals_map = {}

        self.create_widgets()

        if self.event_id:
            self.load_event_data()
        elif initial_date:
            self.widgets['date_debut_entry'].insert(0, initial_date.strftime('%d-%m-%Y'))
            self.widgets['date_fin_entry'].insert(0, initial_date.strftime('%d-%m-%Y'))

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        row = 0
        
        self.add_entry(row, "nom_evenement_entry", "Nom de l'événement *")
        row += 1

        self.add_datetime_picker(row, "debut", "Début *")
        row += 1

        self.add_datetime_picker(row, "fin", "Fin *")
        row += 1

        types = ['soin, santé', 'scolarité', 'famille', 'suivi', 'activités extérieure', 'autres']
        self.add_option_menu(row, "type_evenement_menu", "Type d'événement *", types)
        row += 1

        professionals_data = get_all_users()
        self.professionals_map = {f"{user[2]} {user[1].upper()}": user[0] for user in professionals_data}
        pro_names = list(self.professionals_map.keys())
        self.add_option_menu(row, "user_id_menu", "Professionnel concerné (facultatif)", ["Aucun"] + pro_names)
        
        all_youngs_data = get_all_youngs()
        for i, young_data in enumerate(all_youngs_data):
            young_id, nom, prenom, _, _, _, _ = young_data
            var = ctk.StringVar(value="off")
            checkbox = ctk.CTkCheckBox(self.youngs_frame, text=f"{prenom} {nom.upper()}", variable=var, onvalue="on", offvalue="off")
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.young_checkboxes[young_id] = var

    def add_entry(self, row, name, label_text):
        label = ctk.CTkLabel(self.form_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry = ctk.CTkEntry(self.form_frame)
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        self.widgets[name] = entry

    def add_datetime_picker(self, row, name_prefix, label_text):
        label = ctk.CTkLabel(self.form_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")

        dt_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        dt_frame.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        
        date_entry = ctk.CTkEntry(dt_frame, placeholder_text="JJ-MM-AAAA", width=120)
        date_entry.pack(side="left", fill="x", expand=True)
        self.widgets[f"date_{name_prefix}_entry"] = date_entry

        heures = [f"{h:02}" for h in range(24)]
        minutes = [f"{m:02}" for m in range(0, 60, 5)]
        
        heure_menu = ctk.CTkOptionMenu(dt_frame, values=heures, width=80)
        heure_menu.pack(side="left", padx=(10, 5))
        self.widgets[f"heure_{name_prefix}_menu"] = heure_menu
        
        minute_menu = ctk.CTkOptionMenu(dt_frame, values=minutes, width=80)
        minute_menu.pack(side="left")
        self.widgets[f"minute_{name_prefix}_menu"] = minute_menu

    def add_option_menu(self, row, name, label_text, values):
        label = ctk.CTkLabel(self.form_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        menu = ctk.CTkOptionMenu(self.form_frame, values=values)
        menu.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        self.widgets[name] = menu

    def load_event_data(self):
        details, linked_youngs = get_event_details(self.event_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger les données de l'événement.")
            self.destroy()
            return
        
        self.widgets['nom_evenement_entry'].insert(0, details.get('nom_evenement', ''))
        
        if details.get('debut_datetime'):
            dt_debut = datetime.fromisoformat(details['debut_datetime'])
            self.widgets['date_debut_entry'].insert(0, dt_debut.strftime('%d-%m-%Y'))
            self.widgets['heure_debut_menu'].set(f"{dt_debut.hour:02}")
            self.widgets['minute_debut_menu'].set(f"{dt_debut.minute:02}")
        
        if details.get('fin_datetime'):
            dt_fin = datetime.fromisoformat(details['fin_datetime'])
            self.widgets['date_fin_entry'].insert(0, dt_fin.strftime('%d-%m-%Y'))
            self.widgets['heure_fin_menu'].set(f"{dt_fin.hour:02}")
            self.widgets['minute_fin_menu'].set(f"{dt_fin.minute:02}")

        self.widgets['type_evenement_menu'].set(details.get('type_evenement', ''))
        
        if details.get('user_id'):
            for pro_name, pro_id in self.professionals_map.items():
                if pro_id == details['user_id']:
                    self.widgets['user_id_menu'].set(pro_name)
                    break
        
        for young_id, var in self.young_checkboxes.items():
            if young_id in linked_youngs:
                var.set("on")

    def submit(self):
        try:
            date_debut_str = self.widgets['date_debut_entry'].get()
            heure_debut_str = self.widgets['heure_debut_menu'].get()
            minute_debut_str = self.widgets['minute_debut_menu'].get()
            debut_dt = datetime.strptime(f"{date_debut_str} {heure_debut_str}:{minute_debut_str}", '%d-%m-%Y %H:%M')

            date_fin_str = self.widgets['date_fin_entry'].get()
            heure_fin_str = self.widgets['heure_fin_menu'].get()
            minute_fin_str = self.widgets['minute_fin_menu'].get()
            fin_dt = datetime.strptime(f"{date_fin_str} {heure_fin_str}:{minute_fin_str}", '%d-%m-%Y %H:%M')

        except ValueError:
            messagebox.showerror("Erreur de format", "Veuillez entrer les dates au format JJ-MM-AAAA.", parent=self)
            return

        data = {
            "nom_evenement": self.widgets['nom_evenement_entry'].get(),
            "debut_datetime": debut_dt.isoformat(),
            "fin_datetime": fin_dt.isoformat(),
            "type_evenement": self.widgets['type_evenement_menu'].get(),
            "user_id": self.professionals_map.get(self.widgets['user_id_menu'].get())
        }
        
        if not data["nom_evenement"]:
             messagebox.showerror("Erreur", "Le nom de l'événement est obligatoire.", parent=self)
             return

        selected_young_ids = [young_id for young_id, var in self.young_checkboxes.items() if var.get() == "on"]

        success = False
        if self.event_id is None:
            success = add_event(data, selected_young_ids)
        else:
            success = update_event(self.event_id, data, selected_young_ids)
            
        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)
            
    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
