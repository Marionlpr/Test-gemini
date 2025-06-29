# Fichier : gui/professionnals_list.py
# Description : Vue pour afficher et gérer la liste des professionnels.

import customtkinter as ctk
from tkinter import messagebox
from .professionnals_form import ProfessionalForm
from models.permissions.permissions import get_all_users, delete_user
from models.services.services import get_all_services_for_form

class ProfessionalsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.selected_user_id = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        """Crée les widgets principaux de la vue."""
        # --- Barre de contrôle compacte ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.control_frame, text="Filtrer par service :").grid(row=0, column=0, padx=(10,5))
        
        self.services_map = {name: s_id for s_id, name in get_all_services_for_form()}
        service_names = ["Tous les services"] + list(self.services_map.keys())
        self.service_filter_menu = ctk.CTkOptionMenu(self.control_frame, values=service_names, command=self.on_filter_change, height=28)
        self.service_filter_menu.grid(row=0, column=1, sticky="ew", padx=10)

        # Les boutons d'action sont à droite
        actions_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, sticky="e", padx=10)

        self.edit_button = ctk.CTkButton(actions_frame, text="Voir / Modifier", command=self.edit_professional, state="disabled", height=28)
        self.edit_button.pack(side="left", padx=5)

        if self.user_level == 'gestion administrative':
            self.add_button = ctk.CTkButton(actions_frame, text="Ajouter", command=self.add_professional, height=28, width=80)
            self.add_button.pack(side="left", padx=5)
            self.delete_button = ctk.CTkButton(actions_frame, text="Supprimer", command=self.delete_professional, state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", height=28)
            self.delete_button.pack(side="left", padx=5)

        # --- Cadre pour la liste ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Liste des professionnels")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_var = ctk.IntVar(value=0)

    def refresh_list(self):
        """Met à jour la liste en fonction du filtre."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        selected_service_name = self.service_filter_menu.get()
        service_id_filter = self.services_map.get(selected_service_name) if selected_service_name != "Tous les services" else None
        
        self.users = get_all_users(service_id=service_id_filter)

        for i, user in enumerate(self.users):
            user_id, nom, prenom, identifiant, level, service = user
            text = f"{prenom.capitalize()} {nom.upper()} ({identifiant}) - Rôle: {level} - Service: {service}"
            radio_button = ctk.CTkRadioButton(self.scrollable_frame, text=text, variable=self.radio_var, value=user_id, command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        self.on_select()

    def on_filter_change(self, choice):
        self.radio_var.set(0) # Désélectionner
        self.refresh_list()

    def on_select(self):
        """Gère la sélection d'un utilisateur."""
        self.selected_user_id = self.radio_var.get()
        is_selected = bool(self.selected_user_id)
        
        self.edit_button.configure(state="normal" if is_selected else "disabled")
        if self.user_level == 'gestion administrative':
            self.delete_button.configure(state="normal" if is_selected else "disabled")

    def add_professional(self):
        form = ProfessionalForm(self)
        if form.show(): self.refresh_list()

    def edit_professional(self):
        if not self.selected_user_id: return
        form = ProfessionalForm(self, user_id=self.selected_user_id)
        if form.show(): self.refresh_list()
    
    def delete_professional(self):
        if not self.selected_user_id: return
        answer = messagebox.askyesno("Confirmation", "Supprimer ce professionnel ?", parent=self)
        if answer:
            if delete_user(self.selected_user_id):
                self.refresh_list()
            else: messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
