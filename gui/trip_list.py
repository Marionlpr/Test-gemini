# Fichier : gui/trip_list.py
# Description : Vue pour afficher et gérer la liste des trajets.

import customtkinter as ctk
from tkinter import messagebox
from .trip_form import TripForm
# Imports directs des fonctions pour éviter les conflits
from models.trips.trips import get_all_trips, delete_trip
from utils import date_util

class TripListView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.selected_trip_id = None

        # --- Cadre de contrôle ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.control_frame, text="Enregistrer un trajet", command=self.add_trip)
        self.add_button.pack(side="left", padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.control_frame, text="Modifier", state="disabled", command=self.edit_trip)
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.control_frame, text="Supprimer", state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_trip_action)
        self.delete_button.pack(side="left", padx=10, pady=10)

        # --- Cadre pour la liste ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Historique des trajets")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_var = ctk.IntVar(value=0)
        self.refresh_list()

    def refresh_list(self):
        """Met à jour la liste des trajets affichée."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        all_trips = get_all_trips()

        if not all_trips:
            ctk.CTkLabel(self.scroll_frame, text="Aucun trajet enregistré.").pack(pady=20)
            return
            
        for i, trip in enumerate(all_trips):
            date_fr = date_util.format_date_to_french(trip['date_trajet'])
            text = f"Date: {date_fr} | Motif: {trip['motif'] or 'N/A'} | Conducteur: {trip['professional_name']} | Véhicule: {trip['vehicle_name']}"
            
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=trip['id'],
                                              command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        self.on_select()

    def on_select(self):
        """Active les boutons d'action lors de la sélection."""
        self.selected_trip_id = self.radio_var.get()
        if self.selected_trip_id:
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def add_trip(self):
        form = TripForm(self, user_info=self.user_info)
        if form.show():
            self.refresh_list()

    def edit_trip(self):
        if not self.selected_trip_id: return
        form = TripForm(self, user_info=self.user_info, trip_id=self.selected_trip_id)
        if form.show():
            self.refresh_list()

    def delete_trip_action(self):
        if not self.selected_trip_id: return
        
        answer = messagebox.askyesno("Confirmation", "Supprimer cet enregistrement de trajet ?", parent=self)
        if answer:
            if delete_trip(self.selected_trip_id):
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
