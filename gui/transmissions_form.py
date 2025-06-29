# Fichier : gui/transmissions_form.py
# Description : Fenêtre modale pour ajouter ou modifier une transmission.

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from models.transmissions.transmissions import add_transmission, update_transmission, get_transmission_details
from models.youngs.youngs import get_all_youngs
from models.services.services import get_all_services_for_form
from utils import date_util
from .calendar_popup import CalendarPopup # Importer le nouveau widget

class TransmissionForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, transmission_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.transmission_id = transmission_id
        self.result = False

        self.title("Nouvelle Transmission" if transmission_id is None else "Modifier la Transmission")
        self.geometry("750x850")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) 

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)
        self.options_frame.grid_columnconfigure(3, weight=1)
        
        self.youngs_tools_frame = ctk.CTkFrame(self)
        self.youngs_tools_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")

        self.youngs_frame = ctk.CTkScrollableFrame(self, label_text="Jeunes concernés (facultatif)")
        self.youngs_frame.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="nsew")

        self.content_textbox = ctk.CTkTextbox(self, height=200, font=("Arial", 14))
        self.content_textbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.placeholder = "Rédigez votre transmission ici..."
        
        self.submit_button = ctk.CTkButton(self, text="Enregistrer", command=self.submit)
        self.submit_button.grid(row=4, column=0, padx=20, pady=20)

        self.widgets = {}
        self.young_checkboxes = {}

        self.create_widgets()

        if self.transmission_id:
            self.load_transmission_data()
        else:
             self.content_textbox.insert("0.0", self.placeholder)
             self.content_textbox.configure(text_color="gray")

        self.content_textbox.bind("<FocusIn>", self._on_textbox_focus_in)
        self.content_textbox.bind("<FocusOut>", self._on_textbox_focus_out)

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        # Service
        ctk.CTkLabel(self.options_frame, text="Service *").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        services_data = get_all_services_for_form()
        self.services_map = {name: srv_id for srv_id, name in services_data}
        service_names = list(self.services_map.keys()) or ["Aucun disponible"]
        self.widgets['service_menu'] = ctk.CTkOptionMenu(self.options_frame, values=service_names)
        self.widgets['service_menu'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Catégorie
        ctk.CTkLabel(self.options_frame, text="Catégorie *").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        categories = ['information', 'scolarité', 'famille', 'comportement', 'soin/santé', 'quotidien', 'activités extérieures', 'autres']
        self.widgets['categorie_menu'] = ctk.CTkOptionMenu(self.options_frame, values=categories)
        self.widgets['categorie_menu'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Date et Heure
        ctk.CTkLabel(self.options_frame, text="Date et Heure").grid(row=0, column=2, padx=(20, 10), pady=10, sticky="w")
        now = datetime.now()
        dt_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        dt_frame.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        # Cadre pour la date et le bouton calendrier
        date_picker_frame = ctk.CTkFrame(dt_frame, fg_color="transparent")
        date_picker_frame.pack(side="left", fill="x", expand=True)

        self.widgets['date_entry'] = ctk.CTkEntry(date_picker_frame, placeholder_text="JJ-MM-AAAA")
        self.widgets['date_entry'].pack(side="left", fill="x", expand=True)
        self.widgets['date_entry'].insert(0, now.strftime('%d-%m-%Y'))
        
        # Bouton pour ouvrir le calendrier
        calendar_button = ctk.CTkButton(date_picker_frame, text="🗓️", width=35, height=28, command=self.open_calendar)
        calendar_button.pack(side="left", padx=(5,0))
        
        heures = [f"{h:02}" for h in range(24)]
        minutes = [f"{m:02}" for m in range(0, 60, 5)]
        
        self.widgets['heure_menu'] = ctk.CTkOptionMenu(dt_frame, values=heures, width=80)
        self.widgets['heure_menu'].pack(side="left", padx=(10, 5))
        self.widgets['heure_menu'].set(now.strftime('%H'))
        
        self.widgets['minute_menu'] = ctk.CTkOptionMenu(dt_frame, values=minutes, width=80)
        self.widgets['minute_menu'].pack(side="left")
        self.widgets['minute_menu'].set(f"{now.minute - (now.minute % 5):02}")

        # Sélection de la couleur / importance
        color_frame = ctk.CTkFrame(self.options_frame)
        color_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(color_frame, text="Importance :").pack(side="left", padx=(0, 15))
        
        self.color_var = ctk.StringVar(value="gris")
        colors = {"Normal": "gris", "Positif": "vert", "Attention": "orange", "Urgent": "rouge"}
        for text, value in colors.items():
            option_frame = ctk.CTkFrame(color_frame, fg_color="transparent")
            option_frame.pack(side="left", padx=10, pady=5, expand=True)
            rb = ctk.CTkRadioButton(option_frame, text="", variable=self.color_var, value=value, fg_color=self.get_color_hex(value), width=20, height=20)
            rb.pack(side="left")
            ctk.CTkLabel(option_frame, text=text).pack(side="left", padx=5)

        select_all_btn = ctk.CTkButton(self.youngs_tools_frame, text="Tout sélectionner", height=25, command=self.select_all_youngs)
        select_all_btn.pack(side="left", padx=(0, 10))
        deselect_all_btn = ctk.CTkButton(self.youngs_tools_frame, text="Tout désélectionner", height=25, command=self.deselect_all_youngs)
        deselect_all_btn.pack(side="left")

        all_youngs_data = get_all_youngs()
        for i, young_data in enumerate(all_youngs_data):
            young_id, nom, prenom, _, _, _, _ = young_data
            var = ctk.StringVar(value="off")
            checkbox = ctk.CTkCheckBox(self.youngs_frame, text=f"{prenom} {nom.upper()}", variable=var, onvalue="on", offvalue="off")
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.young_checkboxes[young_id] = var

    def open_calendar(self):
        """Ouvre la popup du calendrier."""
        CalendarPopup(self, self.widgets['date_entry'])

    def get_color_hex(self, color_name):
        color_map = {"vert": "#2E7D32", "orange": "#FF8F00", "rouge": "#C62828", "gris": "#757575"}
        return color_map.get(color_name, "#757575")

    def load_transmission_data(self):
        details, linked_youngs = get_transmission_details(self.transmission_id)
        if not details: return

        for name, s_id in self.services_map.items():
            if s_id == details.get('service_id'): self.widgets['service_menu'].set(name); break
        
        self.widgets['categorie_menu'].set(details.get('categorie'))
        
        dt_obj = datetime.fromisoformat(details.get('datetime_transmission'))
        self.widgets['date_entry'].delete(0, 'end'); self.widgets['date_entry'].insert(0, dt_obj.strftime('%d-%m-%Y'))
        self.widgets['heure_menu'].set(dt_obj.strftime('%H'))
        self.widgets['minute_menu'].set(f"{dt_obj.minute - (dt_obj.minute % 5):02}")
        
        self.color_var.set(details.get('couleur', 'gris'))
        self.content_textbox.insert("0.0", details.get('contenu', ''))
        
        for young_id, var in self.young_checkboxes.items():
            if young_id in linked_youngs: var.set("on")

    def _on_textbox_focus_in(self, event):
        if self.content_textbox.get("1.0", "end-1c") == self.placeholder:
            self.content_textbox.delete("1.0", "end")
            self.content_textbox.configure(text_color=("black", "white"))

    def _on_textbox_focus_out(self, event):
        if not self.content_textbox.get("1.0", "end-1c"):
            self.content_textbox.insert("0.0", self.placeholder)
            self.content_textbox.configure(text_color="gray")
            
    def select_all_youngs(self):
        for var in self.young_checkboxes.values(): var.set("on")

    def deselect_all_youngs(self):
        for var in self.young_checkboxes.values(): var.set("off")

    def submit(self):
        try:
            date_str = self.widgets['date_entry'].get()
            heure_str = self.widgets['heure_menu'].get()
            minute_str = self.widgets['minute_menu'].get()
            dt_transmission = datetime.strptime(f"{date_str} {heure_str}:{minute_str}", '%d-%m-%Y %H:%M')
        except ValueError:
            messagebox.showerror("Erreur de format", "Veuillez entrer la date au format JJ-MM-AAAA.", parent=self)
            return

        service_name = self.widgets['service_menu'].get()
        if service_name == "Aucun disponible":
            messagebox.showerror("Erreur", "Veuillez d'abord créer un service.", parent=self)
            return

        contenu = self.content_textbox.get("1.0", "end-1c")
        if not contenu or contenu == self.placeholder:
             messagebox.showerror("Erreur", "Le contenu de la transmission ne peut pas être vide.", parent=self)
             return

        data = {
            "service_id": self.services_map.get(service_name),
            "categorie": self.widgets['categorie_menu'].get(),
            "contenu": contenu, "user_id": self.user_info[0],
            "datetime_transmission": dt_transmission.isoformat(),
            "couleur": self.color_var.get()
        }

        selected_young_ids = [young_id for young_id, var in self.young_checkboxes.items() if var.get() == "on"]

        success = False
        if self.transmission_id is None:
            success = add_transmission(data, selected_young_ids)
        else:
            success = update_transmission(self.transmission_id, data, selected_young_ids)
            
        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)
            
    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
