# Fichier : gui/professionnals_form.py
# Description : Fenêtre modale pour ajouter ou modifier un professionnel.

import customtkinter as ctk
from tkinter import messagebox
from models.permissions.permissions import get_user_details, add_user, update_user
from models.services.services import get_all_services_for_form
from models.youngs.youngs import get_youngs_for_professional

class ProfessionalForm(ctk.CTkToplevel):
    def __init__(self, parent, user_id=None):
        super().__init__(parent)
        self.transient(parent) 
        self.grab_set() 

        self.parent = parent
        self.user_id = user_id
        self.result = False

        self.title("Fiche Professionnel")
        self.geometry("600x750")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Informations du professionnel")
        self.scrollable_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        self.create_widgets()

        if self.user_id:
            self.load_user_data()

    def create_widgets(self):
        self.nom_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Nom *")
        self.nom_entry.pack(fill="x", padx=20, pady=5)
        self.prenom_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Prénom *")
        self.prenom_entry.pack(fill="x", padx=20, pady=5)
        self.identifiant_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Identifiant de connexion *")
        self.identifiant_entry.pack(fill="x", padx=20, pady=5)
        self.password_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Mot de passe (laisser vide si inchangé)")
        self.password_entry.pack(fill="x", padx=20, pady=5)
        self.adresse_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Adresse")
        self.adresse_entry.pack(fill="x", padx=20, pady=5)
        self.telephone_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Téléphone")
        self.telephone_entry.pack(fill="x", padx=20, pady=5)
        self.email_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Email")
        self.email_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.scrollable_frame, text="Niveau d'authentification :").pack(anchor="w", padx=20, pady=(10,0))
        self.auth_level_menu = ctk.CTkOptionMenu(self.scrollable_frame, values=["standard", "gestion administrative"])
        self.auth_level_menu.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(self.scrollable_frame, text="Service :").pack(anchor="w", padx=20, pady=(10,0))
        self.services_data = get_all_services_for_form()
        self.services_map = {service[1]: service[0] for service in self.services_data}
        service_names = list(self.services_map.keys())
        self.service_menu = ctk.CTkOptionMenu(self.scrollable_frame, values=["Aucun"] + service_names if service_names else ["Aucun"])
        self.service_menu.pack(fill="x", padx=20, pady=5)

        self.ref_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.ref_frame.pack(fill="x", padx=20, pady=20)
        self.ref_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.ref_frame, text="Jeunes en référence principale :", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.ref_textbox = ctk.CTkTextbox(self.ref_frame, height=80, activate_scrollbars=True)
        self.ref_textbox.pack(fill="x", expand=True, padx=10, pady=5)
        self.ref_textbox.configure(state="disabled")

        ctk.CTkLabel(self.ref_frame, text="Jeunes en co-référence :", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.coref_textbox = ctk.CTkTextbox(self.ref_frame, height=80, activate_scrollbars=True)
        self.coref_textbox.pack(fill="x", expand=True, padx=10, pady=10)
        self.coref_textbox.configure(state="disabled")

        self.submit_button = ctk.CTkButton(self.bottom_frame, text="Valider", command=self.submit)
        self.submit_button.pack()

    def load_user_data(self):
        user_data_tuple = get_user_details(self.user_id)
        if not user_data_tuple:
            messagebox.showerror("Erreur", "Impossible de charger les données.", parent=self)
            self.destroy(); return
        
        columns = ["id", "nom", "prenom", "identifiant", "mot_de_passe", "niveau_authentification", "adresse", "telephone", "email", "service_id"]
        user_data = dict(zip(columns, user_data_tuple))

        self.nom_entry.insert(0, user_data.get('nom', ''))
        self.prenom_entry.insert(0, user_data.get('prenom', ''))
        self.identifiant_entry.insert(0, user_data.get('identifiant', ''))
        self.adresse_entry.insert(0, user_data.get('adresse', ''))
        self.telephone_entry.insert(0, user_data.get('telephone', ''))
        # CORRECTION : Affiche une chaîne vide si l'email est None
        self.email_entry.insert(0, user_data.get('email') or '')
        self.auth_level_menu.set(user_data.get('niveau_authentification', 'standard'))

        service_id = user_data.get('service_id')
        if service_id:
            for name, sid in self.services_map.items():
                if sid == service_id: self.service_menu.set(name); break
        else:
            self.service_menu.set("Aucun")
        
        refs = get_youngs_for_professional(self.user_id)
        self.ref_textbox.configure(state="normal"); self.ref_textbox.delete("1.0", "end")
        self.ref_textbox.insert("1.0", "\n".join(refs.get('referent_of', ["Aucun"]))); self.ref_textbox.configure(state="disabled")
        
        self.coref_textbox.configure(state="normal"); self.coref_textbox.delete("1.0", "end")
        self.coref_textbox.insert("1.0", "\n".join(refs.get('co_referent_of', ["Aucun"]))); self.coref_textbox.configure(state="disabled")
    
    def submit(self):
        # CORRECTION : Convertit une chaîne vide en None pour l'email
        email_value = self.email_entry.get()
        
        data = {
            "nom": self.nom_entry.get(), "prenom": self.prenom_entry.get(),
            "identifiant": self.identifiant_entry.get(), "mot_de_passe": self.password_entry.get(),
            "adresse": self.adresse_entry.get(), "telephone": self.telephone_entry.get(),
            "email": email_value if email_value else None,
            "niveau_authentification": self.auth_level_menu.get(),
            "service_id": self.services_map.get(self.service_menu.get()) if self.service_menu.get() != "Aucun" else None
        }

        if not data['nom'] or not data['prenom'] or not data['identifiant']:
            messagebox.showerror("Erreur", "Les champs Nom, Prénom et Identifiant sont obligatoires.", parent=self)
            return
        if self.user_id is None and not data['mot_de_passe']:
            messagebox.showerror("Erreur", "Le mot de passe est obligatoire.", parent=self)
            return

        success = False
        if self.user_id is None:
            result = add_user(data)
            if result == "identifiant_exists":
                 messagebox.showerror("Erreur", "Cet identifiant est déjà utilisé par un autre professionnel.", parent=self)
                 return
            if result == "email_exists":
                 messagebox.showerror("Erreur", "Cette adresse email est déjà utilisée par un autre professionnel.", parent=self)
                 return
            success = result
        else:
            success = update_user(self.user_id, data)
        
        if success:
            messagebox.showinfo("Succès", "Opération réalisée avec succès.", parent=self)
            self.result = True; self.destroy() 
        else:
            messagebox.showerror("Erreur", "Une erreur inattendue est survenue.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
