# Fichier : gui/youngs_form.py
# Description : Fenêtre modale pour ajouter ou modifier un jeune.

import customtkinter as ctk
from tkinter import messagebox
# CORRECTION: Imports plus spécifiques pour éviter les conflits
from models.youngs.youngs import get_all_youngs, get_young_details, add_young, update_young, get_all_referents_for_form
from models.services.services import get_all_services_for_form
from utils import date_util

class YoungForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, young_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.young_id = young_id
        self.result = False

        # --- Sécurité ---
        # On vérifie les permissions AVANT de construire la fenêtre
        user_id_logged_in, user_level = self.user_info
        if self.young_id is None and user_level != 'gestion administrative':
            messagebox.showerror("Accès refusé", "Vous n'avez pas les permissions requises pour ajouter un jeune.")
            # On utilise 'after' pour s'assurer que la fenêtre est détruite proprement
            self.after(10, self.destroy)
            return

        self.title("Ajouter un Jeune" if young_id is None else "Modifier la Fiche d'un Jeune")
        self.geometry("600x800")
        
        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Informations du jeune")
        self.scrollable_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        self.widgets = {}
        self.create_widgets()

        if self.young_id:
            self.load_young_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire en utilisant .pack pour la robustesse."""
        # --- Champs de saisie ---
        fields = {
            "nom": "Nom *", "prenom": "Prénom *", "date_naissance": "Date de naissance (JJ-MM-AAAA) *",
            "lieu_naissance": "Lieu de naissance", "date_entree": "Date d'entrée (JJ-MM-AAAA) *",
            "date_echeance_placement": "Date échéance placement (JJ-MM-AAAA)", "date_audience": "Date d'audience (JJ-MM-AAAA)",
            "date_synthese_pec": "Date de synthèse (PEC) (JJ-MM-AAAA)", "date_echeance_cjm": "Date échéance CJM (JJ-MM-AAAA)",
            "date_sortie": "Date de sortie (JJ-MM-AAAA)"
        }

        for name, label_text in fields.items():
            ctk.CTkLabel(self.scrollable_frame, text=label_text).pack(anchor="w", padx=20, pady=(10,0))
            entry = ctk.CTkEntry(self.scrollable_frame)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.widgets[name] = entry
            
        # --- Menus déroulants ---
        self.add_option_menu("type_placement", "Type de placement *", 
                             ['accueil d’urgence', 'accueil 72h', 'placement provisoire', 'mesure judiciaire', 'mesure administrative'])
        self.add_option_menu("type_accompagnement", "Type d'accompagnement *",
                             ['AEMO-RH', 'séjour de répit (AEMO-RH)', 'internat', 'studio'])
        self.add_option_menu("statut_accueil", "Statut de l'accueil *",
                             ['en attente', 'admission validée', 'sorti'])

        referents_data = get_all_referents_for_form()
        self.referents_map = {name: ref_id for ref_id, name in referents_data}
        referent_names = ["Aucun"] + list(self.referents_map.keys())
        
        self.add_option_menu("referent_id", "Référent *", referent_names)
        self.add_option_menu("co_referent_id", "Co-référent", referent_names)

        services_data = get_all_services_for_form()
        self.services_map = {name: srv_id for srv_id, name in services_data}
        service_names = ["Aucun"] + list(self.services_map.keys())
        self.add_option_menu("service_id", "Service", service_names)
        
        # --- Bouton de validation ---
        self.submit_button = ctk.CTkButton(self.bottom_frame, text="Valider", command=self.submit)
        self.submit_button.pack()

        # Seul un admin peut modifier les références
        user_id_logged_in, user_level = self.user_info
        if user_level != 'gestion administrative':
            self.widgets['referent_id'].configure(state='disabled')
            self.widgets['co_referent_id'].configure(state='disabled')

    def add_option_menu(self, name, label_text, values):
        ctk.CTkLabel(self.scrollable_frame, text=label_text).pack(anchor="w", padx=20, pady=(10,0))
        menu = ctk.CTkOptionMenu(self.scrollable_frame, values=values)
        menu.pack(fill="x", padx=20, pady=(0,5))
        self.widgets[name] = menu
        
    def load_young_data(self):
        data = get_young_details(self.young_id)
        if not data: return
        
        for name, widget in self.widgets.items():
            value = data.get(name)
            if "date" in name and value:
                widget.insert(0, date_util.format_date_to_french(value))
            elif isinstance(widget, ctk.CTkOptionMenu):
                if (name == "referent_id" or name == "co_referent_id") and value:
                    for ref_name, ref_id in self.referents_map.items():
                        if ref_id == value: widget.set(ref_name); break
                elif name == "service_id" and value:
                     for srv_name, srv_id in self.services_map.items():
                        if srv_id == value: widget.set(srv_name); break
                elif value:
                    widget.set(str(value))
            elif value:
                widget.insert(0, str(value))

    def submit(self):
        form_data = {}
        for name, widget in self.widgets.items():
            value = widget.get()
            if isinstance(widget, ctk.CTkEntry):
                if "date" in name and value: form_data[name] = date_util.format_date_to_iso(value)
                elif value: form_data[name] = value
            elif isinstance(widget, ctk.CTkOptionMenu):
                # Pour les références et services, on gère le cas "Aucun"
                if (name == "referent_id" or name == "co_referent_id"):
                    form_data[name] = self.referents_map.get(value) if value != "Aucun" else None
                elif name == "service_id":
                    form_data[name] = self.services_map.get(value) if value != "Aucun" else None
                else: 
                    form_data[name] = value
        
        required_fields = ["nom", "prenom", "date_naissance", "date_entree", "type_placement", "type_accompagnement", "statut_accueil", "referent_id"]
        for field in required_fields:
            if not form_data.get(field):
                messagebox.showerror("Erreur", f"Le champ '{field}' est obligatoire.", parent=self)
                return

        success = False
        if self.young_id is None: # Mode ajout
            success = add_young(form_data)
        else: # Mode modification
            success = update_young(self.young_id, form_data)
        
        if success:
            messagebox.showinfo("Succès", "Opération réalisée avec succès.", parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
