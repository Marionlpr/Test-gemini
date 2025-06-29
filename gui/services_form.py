# Fichier : gui/services_form.py
# Description : Fenêtre modale pour ajouter ou modifier un service.

import customtkinter as ctk
from tkinter import messagebox
from models.services import services

class ServiceForm(ctk.CTkToplevel):
    def __init__(self, parent, service_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.service_id = service_id
        self.result = False

        self.title("Ajouter un Service" if service_id is None else "Modifier un Service")
        self.geometry("400x300")
        self.resizable(False, False)

        self.create_widgets()

        if self.service_id:
            self.load_service_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        self.nom_entry = ctk.CTkEntry(self, placeholder_text="Nom du service")
        self.nom_entry.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.adresse_entry = ctk.CTkEntry(self, placeholder_text="Adresse")
        self.adresse_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.telephone_entry = ctk.CTkEntry(self, placeholder_text="Numéro de téléphone")
        self.telephone_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=3, column=0, padx=20, pady=20)

    def load_service_data(self):
        service_data_tuple = services.get_service_details(self.service_id)
        if not service_data_tuple:
            messagebox.showerror("Erreur", "Impossible de charger les données du service.", parent=self)
            self.destroy()
            return

        columns = ["id", "nom_service", "adresse", "telephone"]
        service_data = dict(zip(columns, service_data_tuple))

        self.nom_entry.insert(0, service_data.get('nom_service', ''))
        self.adresse_entry.insert(0, service_data.get('adresse', ''))
        self.telephone_entry.insert(0, service_data.get('telephone', ''))

    def submit(self):
        data = {
            "nom_service": self.nom_entry.get(),
            "adresse": self.adresse_entry.get(),
            "telephone": self.telephone_entry.get()
        }

        if not data['nom_service']:
            messagebox.showerror("Erreur de validation", "Le nom du service est obligatoire.", parent=self)
            return

        success = False
        if self.service_id is None:
            result = services.add_service(data)
            if result == "exists":
                messagebox.showerror("Erreur", "Ce nom de service est déjà utilisé.", parent=self)
                return
            success = result
        else:
            success = services.update_service(self.service_id, data)

        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "Une erreur est survenue lors de l'opération.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
