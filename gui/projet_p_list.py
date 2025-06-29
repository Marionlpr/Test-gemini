# Fichier : gui/projet_p_list.py
# Description : Vue pour afficher et gérer les projets personnalisés.

import customtkinter as ctk
from tkinter import messagebox
from .projet_p_form import ProjetPersonnaliseForm
# CORRECTION: Imports plus spécifiques pour éviter les conflits
from models.projet_p.projet_p import get_all_projets, get_projet_details, delete_projet, calculate_next_project_date
from models.youngs.youngs import get_all_youngs
from utils import date_util, pdf_export # Importer le module d'export

class ProjetPView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.selected_projet_id = None

        # --- Cadre de contrôle en haut ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.control_frame, text="Rédiger un projet", command=self.open_projet_form)
        self.add_button.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(self.control_frame, text="Filtrer par jeune :").pack(side="left", padx=(20, 5), pady=10)
        
        self.youngs_map = {f"{y[2]} {y[1].upper()}": y[0] for y in get_all_youngs()}
        filter_options = ["Tous les jeunes"] + list(self.youngs_map.keys())
        self.filter_menu = ctk.CTkOptionMenu(self.control_frame, values=filter_options, command=self.refresh_list)
        self.filter_menu.pack(side="left", padx=5, pady=10)

        # --- Cadre des actions sur la sélection ---
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.actions_frame.grid_columnconfigure(1, weight=1)

        self.edit_button = ctk.CTkButton(self.actions_frame, text="Voir / Modifier", command=self.edit_projet, state="disabled")
        self.edit_button.pack(side="left", padx=10, pady=10)
        
        # CORRECTION : Ajout du bouton d'exportation
        self.export_button = ctk.CTkButton(self.actions_frame, text="Exporter en PDF", command=self.export_projet, state="disabled")
        self.export_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.actions_frame, text="Supprimer", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_projet, state="disabled")
        self.delete_button.pack(side="left", padx=10, pady=10)
        
        self.next_date_label = ctk.CTkLabel(self.actions_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.next_date_label.pack(side="right", padx=10, pady=10)

        # --- Cadre scrollable pour la liste ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Projets personnalisés enregistrés")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.radio_var = ctk.IntVar(value=0)
        self.refresh_list()

    def refresh_list(self, filter_choice=None):
        """Met à jour la liste des projets affichée."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        all_projets = get_all_projets()
        
        selected_young_filter = self.filter_menu.get()
        young_id_filter = self.youngs_map.get(selected_young_filter) if selected_young_filter != "Tous les jeunes" else None

        for i, projet in enumerate(all_projets):
            if young_id_filter and projet['young_id'] != young_id_filter:
                continue
            
            date_fr = date_util.format_date_to_french(projet['date_projet'])
            text = f"Projet pour {projet['prenom']} {projet['nom'].upper()} - Date d'enregistrement : {date_fr}"
            
            radio_button = ctk.CTkRadioButton(self.scrollable_frame, text=text, variable=self.radio_var, value=projet['id'],
                                              command=lambda p=projet: self.on_select(p))
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        self.on_select(None)

    def on_select(self, projet_data):
        """Gère la sélection d'un projet dans la liste."""
        if projet_data:
            self.selected_projet_id = projet_data['id']
            self.edit_button.configure(state="normal")
            self.export_button.configure(state="normal") # Activer le bouton
            self.delete_button.configure(state="normal")
            
            next_date = calculate_next_project_date(projet_data['date_projet'])
            self.next_date_label.configure(text=f"Prochain projet à prévoir pour le : {next_date}")
        else:
            self.selected_projet_id = None
            self.edit_button.configure(state="disabled")
            self.export_button.configure(state="disabled") # Désactiver le bouton
            self.delete_button.configure(state="disabled")
            self.next_date_label.configure(text="")

    def open_projet_form(self, projet_id=None):
        """Ouvre le formulaire pour ajouter ou modifier un projet."""
        form = ProjetPersonnaliseForm(self, user_info=self.user_info, projet_id=projet_id)
        if form.show():
            self.refresh_list()

    def edit_projet(self):
        if self.selected_projet_id:
            self.open_projet_form(projet_id=self.selected_projet_id)

    def export_projet(self):
        """Exporte le projet sélectionné en PDF."""
        if not self.selected_projet_id:
            messagebox.showwarning("Exportation impossible", "Veuillez d'abord sélectionner un projet.", parent=self)
            return
        
        details = get_projet_details(self.selected_projet_id)
        pdf_export.export_projet_p_to_pdf(details)


    def delete_projet(self):
        if not self.selected_projet_id: return
        answer = messagebox.askyesno("Confirmation", "Supprimer définitivement ce projet personnalisé ?", parent=self)
        if answer:
            if delete_projet(self.selected_projet_id):
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
