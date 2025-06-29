# Fichier : gui/vehicle_form.py
# Description : Fenêtre modale pour ajouter ou modifier un véhicule.

import customtkinter as ctk
from tkinter import messagebox
# Importation directe des fonctions pour éviter les conflits
from models.vehicles.vehicles import add_vehicle, update_vehicle, get_vehicle_details

class VehicleForm(ctk.CTkToplevel):
    def __init__(self, parent, vehicle_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.vehicle_id = vehicle_id
        self.result = False

        self.title("Ajouter un Véhicule" if vehicle_id is None else "Modifier le Véhicule")
        self.geometry("450x400")
        self.resizable(False, False)

        self.create_widgets()

        if self.vehicle_id:
            self.load_vehicle_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        self.grid_columnconfigure(0, weight=1)

        # Champs du formulaire
        self.marque_entry = ctk.CTkEntry(self, placeholder_text="Marque *")
        self.marque_entry.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.modele_entry = ctk.CTkEntry(self, placeholder_text="Modèle *")
        self.modele_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.plaque_entry = ctk.CTkEntry(self, placeholder_text="Plaque d'immatriculation *")
        self.plaque_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.places_entry = ctk.CTkEntry(self, placeholder_text="Nombre de places *")
        self.places_entry.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.puissance_entry = ctk.CTkEntry(self, placeholder_text="Puissance fiscale")
        self.puissance_entry.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Bouton de validation
        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=5, column=0, padx=20, pady=20)

    def load_vehicle_data(self):
        """Charge les données du véhicule à modifier."""
        details = get_vehicle_details(self.vehicle_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger les données du véhicule.", parent=self)
            self.destroy()
            return
        
        self.marque_entry.insert(0, details.get('marque', ''))
        self.modele_entry.insert(0, details.get('modele', ''))
        self.plaque_entry.insert(0, details.get('plaque_immatriculation', ''))
        self.places_entry.insert(0, str(details.get('nombre_places', '')))
        self.puissance_entry.insert(0, str(details.get('puissance_fiscale', '')))

    def submit(self):
        """Récupère, valide et sauvegarde les données du véhicule."""
        data = {
            "marque": self.marque_entry.get(),
            "modele": self.modele_entry.get(),
            "plaque_immatriculation": self.plaque_entry.get(),
            "nombre_places": self.places_entry.get(),
            "puissance_fiscale": self.puissance_entry.get() or None # Accepte un champ vide
        }

        # Validation simple
        if not data['marque'] or not data['modele'] or not data['plaque_immatriculation'] or not data['nombre_places']:
            messagebox.showerror("Validation", "Les champs marqués d'une * sont obligatoires.", parent=self)
            return
        
        try:
            int(data['nombre_places'])
            if data['puissance_fiscale'] is not None:
                int(data['puissance_fiscale'])
        except ValueError:
            messagebox.showerror("Erreur de format", "Le nombre de places et la puissance fiscale doivent être des nombres.", parent=self)
            return

        success = False
        if self.vehicle_id is None: # Mode Ajout
            result = add_vehicle(data)
            if result == "exists":
                messagebox.showerror("Erreur", "Cette plaque d'immatriculation est déjà enregistrée.", parent=self)
                return
            success = result
        else: # Mode Modification
            success = update_vehicle(self.vehicle_id, data)

        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        """Affiche la fenêtre et attend sa fermeture."""
        self.deiconify()
        self.wait_window()
        return self.result
