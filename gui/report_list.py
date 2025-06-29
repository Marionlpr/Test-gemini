# Fichier : gui/report_list.py
# Description : Vue pour afficher et gérer la liste des rapports.

import customtkinter as ctk
from tkinter import messagebox
from .report_form import ReportForm
# CORRECTION: Imports directs des fonctions pour éviter les ambiguïtés
from models.reports.reports import get_all_reports, get_report_details, validate_report, delete_report
from models.youngs.youngs import get_all_youngs
from utils import date_util, pdf_export # Importer le nouvel utilitaire

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.selected_report_id = None
        self.selected_report_status = None

        # --- Cadre de contrôle en haut ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.control_frame, text="Rédiger un rapport", command=self.open_report_form)
        self.add_button.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(self.control_frame, text="Filtrer par jeune :").pack(side="left", padx=(20, 5), pady=10)
        
        # Menu déroulant pour filtrer par jeune
        self.youngs_map = {f"{y[2]} {y[1].upper()}": y[0] for y in get_all_youngs()}
        filter_options = ["Tous les jeunes"] + list(self.youngs_map.keys())
        self.filter_menu = ctk.CTkOptionMenu(self.control_frame, values=filter_options, command=self.on_filter_change)
        self.filter_menu.pack(side="left", padx=5, pady=10)

        # --- Cadre des actions sur la sélection ---
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.edit_button = ctk.CTkButton(self.actions_frame, text="Lire / Modifier", command=self.edit_report, state="disabled")
        self.edit_button.pack(side="left", padx=10, pady=10)

        # Bouton d'export PDF
        self.export_button = ctk.CTkButton(self.actions_frame, text="Exporter en PDF", command=self.export_report, state="disabled")
        self.export_button.pack(side="left", padx=10, pady=10)
        
        self.validate_button = ctk.CTkButton(self.actions_frame, text="Valider le rapport", command=self.validate_report, state="disabled")
        if self.user_level == 'gestion administrative':
            self.validate_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.actions_frame, text="Supprimer", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_report, state="disabled")
        self.delete_button.pack(side="left", padx=10, pady=10)


        # --- Cadre scrollable pour la liste ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Liste des rapports et écrits")
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.radio_var = ctk.IntVar(value=0)
        self.refresh_list()

    def refresh_list(self):
        """Met à jour la liste des rapports affichée."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        selected_young_filter = self.filter_menu.get()
        young_id_filter = self.youngs_map.get(selected_young_filter) if selected_young_filter != "Tous les jeunes" else None

        all_reports = get_all_reports(young_id=young_id_filter)

        for i, report in enumerate(all_reports):
            date_fr = date_util.format_date_to_french(report['date_redaction']) or "En attente"
            status_text = "Validé" if report['statut'] == 'validé' else "Brouillon"
            
            text = f"[{status_text}] {report['type_rapport']} pour {report['young_prenom']} {report['young_nom'].upper()} | Rédigé par {report['author_prenom']} {report['author_nom'].upper()} | Date: {date_fr}"
            
            radio_button = ctk.CTkRadioButton(self.scrollable_frame, text=text, variable=self.radio_var, value=report['id'],
                                              command=lambda r=report: self.on_select(r))
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        
        self.on_select(None)

    def on_filter_change(self, choice):
        self.refresh_list()

    def on_select(self, report_data):
        """Gère la sélection d'un rapport et l'état des boutons."""
        if report_data:
            self.selected_report_id = report_data['id']
            self.selected_report_status = report_data['statut']
            self.edit_button.configure(state="normal")
            self.delete_button.configure(state="normal")
            
            # Le bouton Exporter n'est actif que pour les rapports validés
            self.export_button.configure(state="normal" if self.selected_report_status == 'validé' else "disabled")

            if self.user_level == 'gestion administrative':
                self.validate_button.configure(state="normal" if self.selected_report_status == 'en attente' else "disabled")
        else:
            self.selected_report_id = None
            self.selected_report_status = None
            self.edit_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            self.export_button.configure(state="disabled")
            if self.user_level == 'gestion administrative':
                self.validate_button.configure(state="disabled")

    def open_report_form(self, report_id=None):
        form = ReportForm(self, user_info=self.user_info, report_id=report_id)
        if form.show():
            self.refresh_list()

    def edit_report(self):
        if self.selected_report_id:
            self.open_report_form(report_id=self.selected_report_id)

    def export_report(self):
        """Exporte le rapport sélectionné en PDF."""
        if self.selected_report_id and self.selected_report_status == 'validé':
            details = get_report_details(self.selected_report_id)
            pdf_export.export_report_to_pdf(details)
        else:
            messagebox.showwarning("Exportation impossible", "Veuillez sélectionner un rapport validé pour l'exporter.", parent=self)

    def validate_report(self):
        if not self.selected_report_id or self.user_level != 'gestion administrative': return
        answer = messagebox.askyesno("Validation", "Valider ce rapport ?\nLa date de rédaction sera fixée à aujourd'hui.", parent=self)
        if answer:
            if validate_report(self.selected_report_id, self.user_info[0]):
                messagebox.showinfo("Succès", "Le rapport a été validé.", parent=self)
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La validation a échoué.", parent=self)

    def delete_report(self):
        if not self.selected_report_id: return
        answer = messagebox.askyesno("Confirmation", "Supprimer définitivement ce rapport ?", parent=self)
        if answer:
            if delete_report(self.selected_report_id):
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)

