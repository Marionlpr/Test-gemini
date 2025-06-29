# Fichier : gui/contacts_form.py
# Description : Fenêtre modale pour ajouter ou modifier un contact.

import customtkinter as ctk
from tkinter import messagebox
from models.contacts import contacts

class ContactForm(ctk.CTkToplevel):
    def __init__(self, parent, young_id, contact_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.young_id = young_id # ID du jeune auquel le contact est lié
        self.contact_id = contact_id
        self.result = False

        self.title("Ajouter un Contact" if contact_id is None else "Modifier un Contact")
        self.geometry("450x450")
        self.resizable(False, False)

        self.create_widgets()

        if self.contact_id:
            self.load_contact_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        # Champs du formulaire
        self.nom_entry = ctk.CTkEntry(self, placeholder_text="Nom *")
        self.nom_entry.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.prenom_entry = ctk.CTkEntry(self, placeholder_text="Prénom *")
        self.prenom_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.lien_entry = ctk.CTkEntry(self, placeholder_text="Lien de parenté (ex: Mère, Père, Tuteur...)")
        self.lien_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.adresse_entry = ctk.CTkEntry(self, placeholder_text="Adresse")
        self.adresse_entry.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.telephone_entry = ctk.CTkEntry(self, placeholder_text="Téléphone")
        self.telephone_entry.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.submit_button = ctk.CTkButton(self, text="Valider", command=self.submit)
        self.submit_button.grid(row=6, column=0, padx=20, pady=20)

    def load_contact_data(self):
        """Charge les données du contact à modifier."""
        data = contacts.get_contact_details(self.contact_id)
        if not data:
            messagebox.showerror("Erreur", "Impossible de charger les données du contact.", parent=self)
            self.destroy()
            return
        
        self.nom_entry.insert(0, data.get('nom', ''))
        self.prenom_entry.insert(0, data.get('prenom', ''))
        self.lien_entry.insert(0, data.get('lien_parente', ''))
        self.adresse_entry.insert(0, data.get('adresse', ''))
        self.telephone_entry.insert(0, data.get('telephone', ''))
        self.email_entry.insert(0, data.get('email', ''))

    def submit(self):
        """Récupère et valide les données avant de les sauvegarder."""
        data = {
            "young_id": self.young_id, # Nécessaire pour l'ajout
            "nom": self.nom_entry.get(),
            "prenom": self.prenom_entry.get(),
            "lien_parente": self.lien_entry.get(),
            "adresse": self.adresse_entry.get(),
            "telephone": self.telephone_entry.get(),
            "email": self.email_entry.get()
        }

        if not data['nom'] or not data['prenom']:
            messagebox.showerror("Erreur de validation", "Le nom et le prénom sont obligatoires.", parent=self)
            return

        success = False
        if self.contact_id is None: # Mode Ajout
            success = contacts.add_contact(data)
        else: # Mode Modification
            success = contacts.update_contact(self.contact_id, data)

        if success:
            messagebox.showinfo("Succès", "Contact enregistré.", parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
