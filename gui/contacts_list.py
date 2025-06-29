# Fichier : gui/contacts_list.py
# Description : Interface pour afficher et gérer la liste de contacts d'un jeune.

import customtkinter as ctk
from tkinter import messagebox
from .contacts_form import ContactForm
from models.contacts import contacts

class ContactsListView(ctk.CTkFrame):
    def __init__(self, parent, young_id, user_level):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.young_id = young_id
        self.user_level = user_level

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cadre du haut avec les boutons d'action ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Les boutons ne sont actifs que pour les admins
        self.add_button = ctk.CTkButton(self.top_frame, text="Ajouter un contact", command=self.add_contact)
        self.add_button.pack(side="left", padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.top_frame, text="Modifier le contact", command=self.edit_contact, state="disabled")
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.top_frame, text="Supprimer le contact", command=self.delete_contact, state="disabled")
        self.delete_button.pack(side="left", padx=10, pady=10)
        
        if self.user_level != 'gestion administrative':
            self.add_button.configure(state="disabled")

        # --- Cadre scrollable pour la liste des contacts ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Contacts associés")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_buttons = []
        self.selected_contact_id = None
        self.radio_var = ctk.IntVar(value=0)

        self.refresh_list()

    def refresh_list(self):
        """Met à jour la liste des contacts affichée."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.radio_buttons.clear()

        self.all_contacts = contacts.get_contacts_for_young(self.young_id)

        for i, contact_data in enumerate(self.all_contacts):
            contact_id, nom, prenom, lien, tel, email = contact_data
            text = f"{prenom.capitalize()} {nom.upper()} ({lien or 'N/A'}) - Tél: {tel or 'N/A'}"
            
            radio_button = ctk.CTkRadioButton(self.scrollable_frame, text=text, variable=self.radio_var, value=contact_id,
                                              command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.radio_buttons.append(radio_button)
        
        self.on_select()

    def on_select(self):
        """Gère la sélection d'un contact dans la liste."""
        self.selected_contact_id = self.radio_var.get()
        if self.selected_contact_id and self.user_level == 'gestion administrative':
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        elif self.user_level == 'gestion administrative':
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def add_contact(self):
        form = ContactForm(self, young_id=self.young_id)
        if form.show():
            self.refresh_list()

    def edit_contact(self):
        if not self.selected_contact_id:
            return
        form = ContactForm(self, young_id=self.young_id, contact_id=self.selected_contact_id)
        if form.show():
            self.refresh_list()
    
    def delete_contact(self):
        if not self.selected_contact_id:
            return
        
        answer = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce contact ?", parent=self)
        if answer:
            if contacts.delete_contact(self.selected_contact_id):
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
