# Fichier : gui/task_form.py
# Description : Fenêtre modale pour ajouter ou modifier une tâche ponctuelle.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from models.tasks.tasks import add_task, update_task, get_task_details
from models.youngs.youngs import get_all_youngs
from models.permissions.permissions import get_users_for_service, get_all_users
from models.services.services import get_all_services_for_form
from utils import date_util
from .calendar_popup import CalendarPopup # Importer le widget calendrier

class TaskForm(ctk.CTkToplevel):
    def __init__(self, parent, task_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.task_id = task_id
        self.result = False

        self.title("Ajouter une Tâche Ponctuelle" if task_id is None else "Modifier la Tâche")
        self.geometry("600x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Le cadre des jeunes prend l'espace

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        self.youngs_frame = ctk.CTkScrollableFrame(self, label_text="Jeunes concernés (facultatif)")
        self.youngs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=2, column=0, padx=20, pady=20)

        self.widgets = {}
        self.young_checkboxes = {}
        self.professionals_map = {}

        self.create_widgets()

        if self.task_id:
            self.load_task_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        row = 0
        
        ctk.CTkLabel(self.form_frame, text="Tâche à réaliser * :").grid(row=row, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        row += 1
        self.widgets['tache_a_realiser'] = ctk.CTkTextbox(self.form_frame, height=100)
        self.widgets['tache_a_realiser'].grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        row += 1

        # --- CORRECTION: Ajout du bouton Calendrier ---
        ctk.CTkLabel(self.form_frame, text="Date limite (facultatif) :").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        
        date_picker_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        date_picker_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        date_picker_frame.grid_columnconfigure(0, weight=1)

        self.widgets['date_limite'] = ctk.CTkEntry(date_picker_frame, placeholder_text="JJ-MM-AAAA")
        self.widgets['date_limite'].grid(row=0, column=0, sticky="ew")
        
        calendar_button = ctk.CTkButton(date_picker_frame, text="🗓️", width=35, height=28, command=self.open_calendar)
        calendar_button.grid(row=0, column=1, padx=(5,0))
        row += 1

        ctk.CTkLabel(self.form_frame, text="Service concerné :").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        services_data = get_all_services_for_form()
        self.services_map = {name: s_id for s_id, name in services_data}
        service_names = ["-- Choisir un service --"] + list(self.services_map.keys())
        self.service_menu = ctk.CTkOptionMenu(self.form_frame, values=service_names, command=self.on_service_change)
        self.service_menu.grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1

        ctk.CTkLabel(self.form_frame, text="Assigner à (facultatif) :").grid(row=row, column=0, padx=10, pady=10, sticky="w")
        self.pro_menu = ctk.CTkOptionMenu(self.form_frame, values=["-- Choisir un service d'abord --"])
        self.pro_menu.grid(row=row, column=1, padx=10, pady=10, sticky="ew"); row += 1
        
        all_youngs_data = get_all_youngs()
        for i, young_data in enumerate(all_youngs_data):
            young_id, nom, prenom, _, _, _, _ = young_data
            var = ctk.StringVar(value="off")
            checkbox = ctk.CTkCheckBox(self.youngs_frame, text=f"{prenom} {nom.upper()}", variable=var, onvalue="on", offvalue="off")
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.young_checkboxes[young_id] = var

    def open_calendar(self):
        """Ouvre la popup du calendrier pour la date limite."""
        CalendarPopup(self, entry_widget=self.widgets['date_limite'])

    def on_service_change(self, selected_service_name):
        """Met à jour la liste des professionnels quand un service est choisi."""
        self.professionals_map = {}
        
        if selected_service_name == "-- Choisir un service --":
            self.pro_menu.configure(values=["-- Choisir un service d'abord --"])
            self.pro_menu.set("-- Choisir un service d'abord --")
            return

        service_id = self.services_map.get(selected_service_name)
        if service_id:
            professionals = get_users_for_service(service_id)
            pro_names = ["Tout le monde"] + [f"{user[1]} {user[2].upper()}" for user in professionals]
            self.professionals_map = {f"{user[1]} {user[2].upper()}": user[0] for user in professionals}
            self.pro_menu.configure(values=pro_names)
            self.pro_menu.set("Tout le monde")

    def load_task_data(self):
        """Charge les données d'une tâche existante dans le formulaire."""
        details, linked_youngs = get_task_details(self.task_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger les données de la tâche.", parent=self)
            self.destroy()
            return
        
        self.widgets['tache_a_realiser'].insert("0.0", details.get('tache_a_realiser', ''))
        
        date_limite_fr = date_util.format_date_to_french(details.get('date_limite'))
        self.widgets['date_limite'].insert(0, date_limite_fr)

        if details.get('user_id'):
            # Il faudrait idéalement trouver le service de l'utilisateur pour pré-selectionner le service aussi.
            # Pour l'instant, cette partie est simplifiée.
            for pro_name, pro_id in self.professionals_map.items():
                if pro_id == details['user_id']:
                    self.pro_menu.set(pro_name)
                    break
        else:
            self.pro_menu.set("Tout le monde")
            
        for young_id, var in self.young_checkboxes.items():
            if young_id in linked_youngs:
                var.set("on")

    def submit(self):
        """Récupère, valide et sauvegarde les données de la tâche."""
        tache_text = self.widgets['tache_a_realiser'].get("1.0", "end-1c")
        if not tache_text:
            messagebox.showerror("Erreur", "La description de la tâche est obligatoire.", parent=self)
            return

        date_limite_str = self.widgets['date_limite'].get()
        
        data = {
            "tache_a_realiser": tache_text,
            "date_limite": date_util.format_date_to_iso(date_limite_str) if date_limite_str else None
        }

        pro_name = self.pro_menu.get()
        data['user_id'] = self.professionals_map.get(pro_name) if pro_name != "Tout le monde" else None

        selected_young_ids = [young_id for young_id, var in self.young_checkboxes.items() if var.get() == "on"]

        success = False
        if self.task_id is None:
            success = add_task(data, selected_young_ids)
        else:
            success = update_task(self.task_id, data, selected_young_ids)
        
        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'opération a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
