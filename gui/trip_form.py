# Fichier : gui/trip_form.py
# Description : Fenêtre modale pour ajouter ou modifier un trajet.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from utils import date_util
# Imports directs des fonctions pour éviter les conflits
from models.trips.trips import add_trip, update_trip, get_trip_details
from models.youngs.youngs import get_all_youngs
from models.permissions.permissions import get_all_users
from models.services.services import get_all_services_for_form
from models.vehicles.vehicles import get_all_vehicles

class TripForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, trip_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.trip_id = trip_id
        self.result = False

        self.title("Enregistrer un Trajet" if trip_id is None else "Modifier le Trajet")
        self.geometry("700x850")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        self.widgets = {}
        self.young_checkboxes = {}

        self.create_widgets()

        if self.trip_id:
            self.load_trip_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        row = 0
        
        # --- Section Informations du trajet ---
        ctk.CTkLabel(self.scroll_frame, text="Date du trajet *:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['date_trajet'] = ctk.CTkEntry(self.scroll_frame, placeholder_text="JJ-MM-AAAA")
        self.widgets['date_trajet'].insert(0, date.today().strftime('%d-%m-%Y'))
        self.widgets['date_trajet'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1

        ctk.CTkLabel(self.scroll_frame, text="Heure de départ *:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['heure_depart'] = ctk.CTkEntry(self.scroll_frame, placeholder_text="HH:MM")
        self.widgets['heure_depart'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1
        
        ctk.CTkLabel(self.scroll_frame, text="Heure de retour *:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['heure_retour'] = ctk.CTkEntry(self.scroll_frame, placeholder_text="HH:MM")
        self.widgets['heure_retour'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1
        
        ctk.CTkLabel(self.scroll_frame, text="Motif du trajet:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['motif'] = ctk.CTkEntry(self.scroll_frame)
        self.widgets['motif'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1
        
        # --- Section Association ---
        self.add_option_menu(row, 'service_id', "Service *:", get_all_services_for_form()); row += 1
        self.add_option_menu(row, 'user_id', "Professionnel *:", get_all_users(), name_key=2, surname_key=1); row += 1
        self.add_option_menu(row, 'vehicle_id', "Véhicule *:", get_all_vehicles(), name_key=1, model_key=2, plate_key=3); row += 1

        # --- Section Kilométrage ---
        ctk.CTkLabel(self.scroll_frame, text="Kilométrage au départ *:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['km_depart'] = ctk.CTkEntry(self.scroll_frame)
        self.widgets['km_depart'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1

        ctk.CTkLabel(self.scroll_frame, text="Kilométrage au retour *:").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.widgets['km_retour'] = ctk.CTkEntry(self.scroll_frame)
        self.widgets['km_retour'].grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1

        # --- Section Jeunes transportés ---
        youngs_frame = ctk.CTkScrollableFrame(self.scroll_frame, label_text="Jeunes transportés")
        youngs_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"); row += 1
        
        all_youngs_data = get_all_youngs()
        for i, young_data in enumerate(all_youngs_data):
            young_id, nom, prenom, _, _, _, _ = young_data
            var = ctk.StringVar(value="off")
            checkbox = ctk.CTkCheckBox(youngs_frame, text=f"{prenom} {nom.upper()}", variable=var, onvalue="on", offvalue="off")
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.young_checkboxes[young_id] = var

        # --- Bouton de validation ---
        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=1, column=0, padx=15, pady=15)

    def add_option_menu(self, row, name, label_text, data_list, name_key=1, surname_key=None, plate_key=None, model_key=None):
        """Helper pour créer les menus déroulants."""
        # CORRECTION : Utilisation du bon nom de variable self.scroll_frame
        ctk.CTkLabel(self.scroll_frame, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        self.widgets[name + '_map'] = {}
        options = []
        if data_list:
            for item in data_list:
                item_id = item[0]
                if surname_key:
                    display_text = f"{item[name_key]} {item[surname_key].upper()}"
                elif plate_key:
                    display_text = f"{item[name_key]} {item[model_key]} ({item[plate_key]})"
                else:
                    display_text = item[name_key]
                
                self.widgets[name + '_map'][display_text] = item_id
                options.append(display_text)
        
        menu = ctk.CTkOptionMenu(self.scroll_frame, values=options if options else ["Aucun"])
        menu.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        self.widgets[name] = menu

    def load_trip_data(self):
        """Charge les données d'un trajet existant pour le modifier."""
        details, linked_youngs = get_trip_details(self.trip_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger les données du trajet.", parent=self)
            self.destroy(); return
        
        self.widgets['date_trajet'].insert(0, date_util.format_date_to_french(details.get('date_trajet')))
        self.widgets['heure_depart'].insert(0, details.get('heure_depart'))
        self.widgets['heure_retour'].insert(0, details.get('heure_retour'))
        self.widgets['motif'].insert(0, details.get('motif'))
        self.widgets['km_depart'].insert(0, str(details.get('km_depart')))
        self.widgets['km_retour'].insert(0, str(details.get('km_retour')))
        
        for name, item_id in self.widgets['service_id_map'].items():
            if item_id == details.get('service_id'): self.widgets['service_id'].set(name); break
        for name, item_id in self.widgets['user_id_map'].items():
            if item_id == details.get('user_id'): self.widgets['user_id'].set(name); break
        for name, item_id in self.widgets['vehicle_id_map'].items():
            if item_id == details.get('vehicle_id'): self.widgets['vehicle_id'].set(name); break
            
        for young_id, var in self.young_checkboxes.items():
            if young_id in linked_youngs: var.set("on")

    def submit(self):
        """Récupère et sauvegarde les données du trajet."""
        data = {
            "date_trajet": date_util.format_date_to_iso(self.widgets['date_trajet'].get()),
            "heure_depart": self.widgets['heure_depart'].get(),
            "heure_retour": self.widgets['heure_retour'].get(),
            "motif": self.widgets['motif'].get(),
            "km_depart": self.widgets['km_depart'].get(),
            "km_retour": self.widgets['km_retour'].get(),
            "service_id": self.widgets['service_id_map'].get(self.widgets['service_id'].get()),
            "user_id": self.widgets['user_id_map'].get(self.widgets['user_id'].get()),
            "vehicle_id": self.widgets['vehicle_id_map'].get(self.widgets['vehicle_id'].get())
        }

        required = ["date_trajet", "heure_depart", "heure_retour", "km_depart", "km_retour", "service_id", "user_id", "vehicle_id"]
        if any(not data.get(key) for key in required):
            messagebox.showerror("Validation", "Tous les champs marqués d'une * sont obligatoires.", parent=self)
            return

        selected_young_ids = [y_id for y_id, var in self.young_checkboxes.items() if var.get() == "on"]

        success = False
        if self.trip_id is None:
            success = add_trip(data, selected_young_ids)
        else:
            success = update_trip(self.trip_id, data, selected_young_ids)
        
        if success:
            self.result = True; self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
