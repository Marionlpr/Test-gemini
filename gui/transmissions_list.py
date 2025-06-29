# Fichier : gui/transmissions_list.py
# Description : Vue pour afficher et gérer les transmissions.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta, datetime
from .transmissions_form import TransmissionForm
from .calendar_popup import CalendarPopup # Importer le nouveau widget
from models.transmissions.transmissions import get_transmissions_for_period, delete_transmission
from models.services.services import get_all_services_for_form
from utils import date_util
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")


class TransmissionsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        
        self.current_date = date.today()
        self.selected_service_id = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.color_map = {"vert": "#2E7D32", "orange": "#FF8F00", "rouge": "#C62828", "gris": "gray50"}

        self.create_widgets()
        self.load_services()
        self.refresh_transmissions()

    def create_widgets(self):
        """Crée les widgets principaux de la vue."""
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.control_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self.control_frame, text="Service :").grid(row=0, column=0, padx=(10,5), pady=5)
        self.service_menu = ctk.CTkOptionMenu(self.control_frame, values=["Chargement..."], command=self.on_service_change, height=28)
        self.service_menu.grid(row=0, column=1, padx=(0,10), pady=5)
        
        date_nav_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        date_nav_frame.grid(row=0, column=2, padx=10, pady=5)
        self.prev_day_button = ctk.CTkButton(date_nav_frame, text="<", width=30, height=28, command=self.go_to_previous_day)
        self.prev_day_button.pack(side="left")
        
        # --- NOUVEAU: Bouton pour ouvrir le calendrier ---
        calendar_btn = ctk.CTkButton(date_nav_frame, text="🗓️", width=35, height=28, command=self.open_calendar_picker)
        calendar_btn.pack(side="left", padx=5)

        self.date_label = ctk.CTkLabel(date_nav_frame, text="", font=ctk.CTkFont(size=14, weight="bold"), width=200)
        self.date_label.pack(side="left", padx=5)
        self.next_day_button = ctk.CTkButton(date_nav_frame, text=">", width=30, height=28, command=self.go_to_next_day)
        self.next_day_button.pack(side="left")
        
        self.add_button = ctk.CTkButton(self.control_frame, text="Rédiger", command=self.add_transmission, height=28)
        self.add_button.grid(row=0, column=4, padx=10, pady=5, sticky="e")

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Transmissions")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def load_services(self):
        """Charge la liste des services et ajoute l'option 'Tous les services'."""
        services_data = get_all_services_for_form()
        self.services_map = {name: srv_id for srv_id, name in services_data}
        service_names = ["Tous les services"] + list(self.services_map.keys())
        
        if len(service_names) > 1:
            self.service_menu.configure(values=service_names)
            self.service_menu.set("Tous les services") 
        else:
            self.service_menu.configure(values=["Aucun service"], state="disabled")
            self.add_button.configure(state="disabled")

    def on_service_change(self, selected_service_name):
        self.selected_service_id = self.services_map.get(selected_service_name) if selected_service_name != "Tous les services" else None
        self.refresh_transmissions()

    def refresh_transmissions(self):
        """Met à jour l'affichage des transmissions en fonction du filtre."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        self.date_label.configure(text=self.current_date.strftime("%A %d %B %Y").capitalize())
        
        iso_date = self.current_date.isoformat()
        transmissions_data = get_transmissions_for_period(iso_date, iso_date, self.selected_service_id)
        
        if not transmissions_data:
            ctk.CTkLabel(self.scroll_frame, text="Aucune transmission enregistrée pour ce jour.").pack(pady=20)
            return
            
        for trans in transmissions_data:
            self.create_transmission_widget(trans)

    def create_transmission_widget(self, trans_data):
        """Crée un widget pour une seule transmission."""
        border_color = self.color_map.get(trans_data.get('couleur'), "gray50")
        
        trans_frame = ctk.CTkFrame(self.scroll_frame, border_width=2, border_color=border_color)
        trans_frame.pack(fill="x", padx=5, pady=5, anchor="n")
        trans_frame.grid_columnconfigure(1, weight=1)

        color_dot = ctk.CTkFrame(trans_frame, fg_color=border_color, width=15, height=15, corner_radius=10)
        color_dot.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="n")
        
        header_frame = ctk.CTkFrame(trans_frame, fg_color="transparent")
        header_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=(5,0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        dt_obj = datetime.fromisoformat(trans_data['datetime_transmission'])
        author_text = f"Par {trans_data['user_prenom']} {trans_data['user_nom'].upper()} le {dt_obj.strftime('%d/%m/%Y à %H:%M')}"
        ctk.CTkLabel(header_frame, text=author_text, font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(header_frame, text=f"Service : {trans_data['nom_service']}", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w", padx=20)

        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e")
        
        edit_btn = ctk.CTkButton(button_frame, text="Modifier", width=70, height=24, 
                                 command=lambda t_id=trans_data['id']: self.edit_transmission(t_id))
        edit_btn.pack(side="left", padx=(0,5))

        delete_btn = ctk.CTkButton(button_frame, text="Supprimer", width=80, height=24, fg_color="#D32F2F", hover_color="#B71C1C",
                                   command=lambda t_id=trans_data['id']: self.delete_transmission(t_id))
        delete_btn.pack(side="left")
        
        ctk.CTkLabel(trans_frame, text=f"Catégorie : {trans_data['categorie'].capitalize()}", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=1, sticky="w", padx=10, pady=(5,0))
        ctk.CTkLabel(trans_frame, text=trans_data['contenu'], wraplength=700, justify="left", anchor="w").grid(row=2, column=1, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(trans_frame, text=f"Concernés : {trans_data['linked_youngs']}", font=ctk.CTkFont(size=11, weight="bold")).grid(row=3, column=1, sticky="w", padx=10, pady=(0,5))
        
    def add_transmission(self):
        form = TransmissionForm(self, user_info=self.user_info)
        if form.show(): self.refresh_transmissions()

    def edit_transmission(self, transmission_id):
        form = TransmissionForm(self, user_info=self.user_info, transmission_id=transmission_id)
        if form.show(): self.refresh_transmissions()

    def delete_transmission(self, transmission_id):
        if messagebox.askyesno("Confirmation", "Supprimer cette transmission ?", parent=self):
            if delete_transmission(transmission_id):
                self.refresh_transmissions()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)

    def open_calendar_picker(self):
        """Ouvre le calendrier pour sélectionner une date."""
        CalendarPopup(self, callback=self.set_date_and_refresh, initial_date=self.current_date)
    
    def set_date_and_refresh(self, selected_date):
        """Met à jour la date et rafraîchit la vue."""
        self.current_date = selected_date
        self.refresh_transmissions()

    def go_to_previous_day(self): self.current_date -= timedelta(days=1); self.refresh_transmissions()
    def go_to_next_day(self): self.current_date += timedelta(days=1); self.refresh_transmissions()
    def refresh_list(self): self.refresh_transmissions()
