# Fichier : gui/youngs_list.py
# Description : Vue pour afficher la liste des jeunes et leur fiche détaillée côte à côte.

import customtkinter as ctk
from tkinter import messagebox
from .youngs_form import YoungForm
from .young_detail_view import YoungDetailView 
from models.youngs.youngs import get_all_youngs, delete_young
from models.services.services import get_all_services_for_form
from utils import date_util

class YoungsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info

        # --- Configuration de la grille principale (2 colonnes) ---
        self.grid_columnconfigure(0, weight=1, minsize=300) # Colonne de la liste
        self.grid_columnconfigure(1, weight=3) # Colonne de la fiche (plus grande)
        self.grid_rowconfigure(0, weight=1)
        
        self.selected_young_id = None
        self.detail_view_frame = None

        # --- Cadre de gauche pour la liste ---
        self.list_container = ctk.CTkFrame(self)
        self.list_container.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.list_container.grid_columnconfigure(0, weight=1)
        
        self.create_list_widgets()

        # --- Cadre de droite pour la fiche détaillée ---
        self.detail_container = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_container.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.show_placeholder()

        self.refresh_list()

    def create_list_widgets(self):
        """Crée les widgets de la colonne de gauche (liste)."""
        # --- CORRECTION: Barre d'actions compacte sur une seule ligne ---
        self.list_container.grid_rowconfigure(1, weight=1) 

        self.top_frame = ctk.CTkFrame(self.list_container)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1) # La colonne du filtre s'étire

        ctk.CTkLabel(self.top_frame, text="Service:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(10,5))
        
        self.services_map = {name: s_id for s_id, name in get_all_services_for_form()}
        service_names = ["Tous les services"] + list(self.services_map.keys())
        self.service_filter_menu = ctk.CTkOptionMenu(self.top_frame, values=service_names, command=self.on_filter_change, height=28)
        self.service_filter_menu.grid(row=0, column=1, sticky="ew", padx=5)
        
        if self.user_level == 'gestion administrative':
            # Cadre pour les boutons admin, à droite du filtre
            admin_actions_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
            admin_actions_frame.grid(row=0, column=2, padx=(10, 5), sticky="e")

            self.add_button = ctk.CTkButton(admin_actions_frame, text="Ajouter", command=self.add_young, height=28, width=70)
            self.add_button.pack(side="left", padx=5)

            self.edit_button = ctk.CTkButton(admin_actions_frame, text="Modifier", command=self.edit_young, height=28, width=70, state="disabled")
            self.edit_button.pack(side="left", padx=5)
            
            self.delete_button = ctk.CTkButton(admin_actions_frame, text="Supprimer", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_young, state="disabled", height=28, width=80)
            self.delete_button.pack(side="left")
        
        # Le cadre de la liste est maintenant sur la ligne 1
        self.scroll_frame = ctk.CTkScrollableFrame(self.list_container, label_text="Liste des jeunes suivis")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_buttons = []
        self.radio_var = ctk.IntVar(value=0)

    def refresh_list(self):
        """Met à jour la liste des jeunes affichée en fonction du filtre."""
        current_selection = self.radio_var.get()
        
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.radio_buttons.clear()
        
        selected_service_name = self.service_filter_menu.get()
        service_id_filter = self.services_map.get(selected_service_name) if selected_service_name != "Tous les services" else None
        
        self.all_youngs = get_all_youngs(service_id=service_id_filter)
        for i, young_data in enumerate(self.all_youngs):
            young_id, nom, prenom, _, _, _, _ = young_data
            text = f"{prenom.capitalize()} {nom.upper()}"
            
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=young_id, command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.radio_buttons.append(radio_button)
        
        if current_selection in [y[0] for y in self.all_youngs]:
            self.radio_var.set(current_selection)
            self.on_select()
        else:
            self.on_select(clear=True)
            
    def on_filter_change(self, choice):
        """Appelé lors du changement de filtre pour rafraîchir la liste."""
        self.on_select(clear=True) 
        self.refresh_list()

    def on_select(self, clear=False):
        """Gère la sélection d'un jeune dans la liste."""
        if clear:
            self.selected_young_id = 0
            self.radio_var.set(0)
        else:
             self.selected_young_id = self.radio_var.get()

        is_selected = bool(self.selected_young_id)
        
        if self.user_level == 'gestion administrative':
            self.edit_button.configure(state="normal" if is_selected else "disabled")
            self.delete_button.configure(state="normal" if is_selected else "disabled")
        
        if is_selected:
            self.show_detail_view(self.selected_young_id)
        else:
            self.show_placeholder()

    def show_placeholder(self):
        if self.detail_view_frame: self.detail_view_frame.destroy()
        self.detail_view_frame = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        self.detail_view_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(self.detail_view_frame, text="Sélectionnez un jeune dans la liste pour voir sa fiche.",
                     font=ctk.CTkFont(size=16, slant="italic"), text_color="gray").pack(expand=True)

    def show_detail_view(self, young_id):
        if self.detail_view_frame: self.detail_view_frame.destroy()
        self.detail_view_frame = YoungDetailView(self.detail_container, young_id=young_id, user_info=self.user_info)
        self.detail_view_frame.pack(expand=True, fill="both")

    def add_young(self):
        form = YoungForm(self, user_info=self.user_info)
        if form.show():
            self.refresh_list()
    
    def edit_young(self):
        if not self.selected_young_id: return
        form = YoungForm(self, user_info=self.user_info, young_id=self.selected_young_id)
        if form.show():
            self.refresh_list()
            self.show_detail_view(self.selected_young_id)

    def delete_young(self):
        if not self.selected_young_id: return
        answer = messagebox.askyesno("Confirmation", "Supprimer ce jeune et toutes ses données associées ?", parent=self)
        if answer:
            if delete_young(self.selected_young_id):
                self.selected_young_id = 0; self.radio_var.set(0)
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.")
