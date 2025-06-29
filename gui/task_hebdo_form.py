# Fichier : gui/task_hebdo_form.py
# Description : Fenêtre modale pour ajouter ou modifier une tâche hebdomadaire.

import customtkinter as ctk
from tkinter import messagebox
from models.tasks_hebdo.tasks_hebdo import add_task_hebdo, update_task_hebdo, get_task_hebdo_details
from models.services.services import get_all_services_for_form

class TaskHebdoForm(ctk.CTkToplevel):
    def __init__(self, parent, task_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.task_id = task_id
        self.result = False

        self.title("Ajouter une Tâche Hebdomadaire" if task_id is None else "Modifier la Tâche")
        self.geometry("500x350")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

        if self.task_id:
            self.load_task_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        
        ctk.CTkLabel(self, text="Jour de la tâche * :").pack(anchor="w", padx=20, pady=(20,0))
        jours_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        self.jour_menu = ctk.CTkOptionMenu(self, values=jours_semaine)
        self.jour_menu.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self, text="Tâche hebdomadaire * :").pack(anchor="w", padx=20, pady=(10,0))
        self.tache_entry = ctk.CTkEntry(self, placeholder_text="Description de la tâche")
        self.tache_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self, text="Service concerné * :").pack(anchor="w", padx=20, pady=(10,0))
        services_data = get_all_services_for_form()
        self.services_map = {name: s_id for s_id, name in services_data}
        service_names = list(self.services_map.keys())
        self.service_menu = ctk.CTkOptionMenu(self, values=service_names if service_names else ["Aucun service"])
        self.service_menu.pack(fill="x", padx=20, pady=5)

        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.pack(pady=20)

    def load_task_data(self):
        details = get_task_hebdo_details(self.task_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger la tâche.", parent=self)
            self.destroy()
            return
        
        self.jour_menu.set(details.get('jour_semaine'))
        self.tache_entry.insert(0, details.get('tache_hebdomadaire', ''))
        
        for name, s_id in self.services_map.items():
            if s_id == details.get('service_id'):
                self.service_menu.set(name)
                break

    def submit(self):
        """Récupère, valide et sauvegarde les données de la tâche."""
        service_name = self.service_menu.get()
        if service_name == "Aucun service":
            messagebox.showerror("Erreur", "Veuillez créer un service avant d'ajouter une tâche.", parent=self)
            return
            
        data = {
            "jour_semaine": self.jour_menu.get(),
            "tache_hebdomadaire": self.tache_entry.get(),
            "service_id": self.services_map.get(service_name)
        }

        if not data["tache_hebdomadaire"]:
            messagebox.showerror("Erreur", "La description de la tâche ne peut pas être vide.", parent=self)
            return

        success = False
        if self.task_id is None:
            success = add_task_hebdo(data)
        else:
            success = update_task_hebdo(self.task_id, data)

        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'opération a échoué.", parent=self)

    def show(self):
        """Affiche la fenêtre et attend sa fermeture."""
        self.deiconify()
        self.wait_window()
        return self.result
