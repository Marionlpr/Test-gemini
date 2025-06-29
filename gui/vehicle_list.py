# Fichier : gui/vehicle_list.py
# Description : Vue pour afficher et gérer la liste des véhicules.

import customtkinter as ctk
from tkinter import messagebox
from .vehicle_form import VehicleForm
from models.vehicles.vehicles import get_all_vehicles, delete_vehicle

class VehicleListView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        
        # Sécurité : cette vue est réservée à la gestion administrative
        if self.user_info[1] != 'gestion administrative':
            ctk.CTkLabel(self, text="Accès non autorisé.", font=ctk.CTkFont(size=18)).pack(pady=50)
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.selected_vehicle_id = None

        # --- Cadre de contrôle ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.control_frame, text="Ajouter un véhicule", command=self.add_vehicle)
        self.add_button.pack(side="left", padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.control_frame, text="Modifier", state="disabled", command=self.edit_vehicle)
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.control_frame, text="Supprimer", state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_vehicle_action)
        self.delete_button.pack(side="left", padx=10, pady=10)

        # --- Cadre pour la liste ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Flotte de véhicules de l'établissement")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_var = ctk.IntVar(value=0)
        self.refresh_list()

    def refresh_list(self):
        """Met à jour la liste des véhicules."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        all_vehicles = get_all_vehicles()

        if not all_vehicles:
            ctk.CTkLabel(self.scroll_frame, text="Aucun véhicule enregistré.").pack(pady=20)
            return
            
        for i, vehicle in enumerate(all_vehicles):
            vehicle_id, marque, modele, plaque, places = vehicle
            text = f"{marque.upper()} {modele} - {plaque} ({places} places)"
            
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=vehicle_id, command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        self.on_select()

    def on_select(self):
        """Active les boutons d'action lors de la sélection."""
        self.selected_vehicle_id = self.radio_var.get()
        if self.selected_vehicle_id:
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def add_vehicle(self):
        form = VehicleForm(self)
        if form.show():
            self.refresh_list()

    def edit_vehicle(self):
        if not self.selected_vehicle_id: return
        form = VehicleForm(self, vehicle_id=self.selected_vehicle_id)
        if form.show():
            self.refresh_list()

    def delete_vehicle_action(self):
        if not self.selected_vehicle_id: return
        
        answer = messagebox.askyesno("Confirmation", "Supprimer ce véhicule ?", parent=self)
        if answer:
            result = delete_vehicle(self.selected_vehicle_id)
            if result is True:
                self.refresh_list()
            elif result == "in_use":
                messagebox.showerror("Action impossible", "Ce véhicule ne peut pas être supprimé car il est utilisé dans au moins un trajet enregistré.", parent=self)
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)

