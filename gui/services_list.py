# Fichier : gui/services_list.py
# Description : Vue pour afficher et gérer la liste des services.

import customtkinter as ctk
from tkinter import messagebox
from .services_form import ServiceForm
from models.services.services import get_all_services, delete_service

class ServicesView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info

        # Sécurité : cette vue est réservée à la gestion administrative
        if self.user_level != 'gestion administrative':
            ctk.CTkLabel(self, text="Accès non autorisé.", font=ctk.CTkFont(size=18)).pack(pady=50)
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.top_frame, text="Ajouter un service", command=self.add_service)
        self.add_button.pack(side="left", padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.top_frame, text="Modifier le service", command=self.edit_service, state="disabled")
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.top_frame, text="Supprimer le service", command=self.delete_service, state="disabled")
        self.delete_button.pack(side="left", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Liste des services")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.radio_buttons = []
        self.selected_service_id = None
        self.radio_var = ctk.IntVar(value=0)

        self.refresh_list()

    def refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.radio_buttons.clear()

        self.all_services = get_all_services()

        for i, service in enumerate(self.all_services):
            service_id, nom, adresse, tel = service
            text = f"{nom} - {adresse or 'N/A'} - {tel or 'N/A'}"
            
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=service_id,
                                              command=self.on_select)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.radio_buttons.append(radio_button)
        
        self.on_select()

    def on_select(self):
        self.selected_service_id = self.radio_var.get()
        if self.selected_service_id:
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
        else:
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def add_service(self):
        form = ServiceForm(self)
        if form.show():
            self.refresh_list()

    def edit_service(self):
        if not self.selected_service_id:
            return
        form = ServiceForm(self, service_id=self.selected_service_id)
        if form.show():
            self.refresh_list()
    
    def delete_service(self):
        if not self.selected_service_id:
            return
        
        answer = messagebox.askyesno("Confirmation", "Supprimer ce service ?\nLes professionnels et jeunes associés seront désaffiliés.",
                                     parent=self)
        if answer:
            result = delete_service(self.selected_service_id)
            if result is True:
                messagebox.showinfo("Succès", "Le service a été supprimé.", parent=self)
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
