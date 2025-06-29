# Fichier : gui/report_form.py
# Description : Fenêtre pour rédiger ou modifier un rapport.

import customtkinter as ctk
from tkinter import messagebox
# CORRECTION: Imports plus spécifiques pour éviter les conflits
from models.reports.reports import get_report_details, add_report, update_report
from models.youngs.youngs import get_all_youngs
from utils import date_util

class ReportForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, report_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.report_id = report_id
        self.result = False

        self.title("Nouveau Rapport" if report_id is None else "Modifier le Rapport")
        self.geometry("900x850")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.text_widgets = {}
        self.option_widgets = {}

        self.create_widgets()

        if self.report_id:
            self.load_report_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(options_frame, text="Jeune concerné *").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        youngs_data = get_all_youngs()
        self.youngs_map = {f"{y[2]} {y[1].upper()}": y[0] for y in youngs_data}
        young_names = list(self.youngs_map.keys())
        self.option_widgets['young_id'] = ctk.CTkOptionMenu(options_frame, values=young_names or ["Aucun jeune"])
        self.option_widgets['young_id'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(options_frame, text="Type de rapport *").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        report_types = ['rapport d’évaluation accueil d’urgence', 'rapport d’évaluation accueil 72h', 'rapport d’évaluation placement provisoire', 'rapport de synthèse']
        self.option_widgets['type_rapport'] = ctk.CTkOptionMenu(options_frame, values=report_types)
        self.option_widgets['type_rapport'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(options_frame, text="Rédacteur :").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        author_name = f"Utilisateur ID {self.user_info[0]}"
        ctk.CTkLabel(options_frame, text=author_name).grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        report_sections = [
            ("rappel_situation", "Rappel de la situation"), ("accueil", "Accueil"), ("scolarite", "Scolarité"),
            ("soin_sante", "Soin / Santé"), ("famille", "Famille"), ("psychologique", "Psychologique"),
            ("preconisations", "Préconisations")
        ]

        for name, label_text in report_sections:
            label = ctk.CTkLabel(self.scrollable_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(fill="x", padx=10, pady=(15, 5))
            textbox = ctk.CTkTextbox(self.scrollable_frame, height=150, wrap="word", font=("Arial", 13))
            textbox.pack(fill="x", expand=True, padx=10)
            self.text_widgets[name] = textbox
            
        self.submit_button = ctk.CTkButton(self, text="Enregistrer le Brouillon", command=self.submit)
        self.submit_button.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

    def load_report_data(self):
        """Charge les données d'un rapport existant pour modification."""
        details = get_report_details(self.report_id)
        if not details:
            messagebox.showerror("Erreur", "Impossible de charger les données du rapport.", parent=self)
            self.destroy()
            return

        for name, y_id in self.youngs_map.items():
            if y_id == details.get('young_id'):
                self.option_widgets['young_id'].set(name)
                break
        self.option_widgets['type_rapport'].set(details.get('type_rapport'))

        for name, widget in self.text_widgets.items():
            widget.insert("0.0", details.get(name, ""))

    def submit(self):
        """Récupère et sauvegarde les données du formulaire."""
        young_name = self.option_widgets['young_id'].get()
        if young_name == "Aucun jeune":
            messagebox.showerror("Validation", "Veuillez sélectionner un jeune.", parent=self)
            return

        data = {
            "young_id": self.youngs_map.get(young_name),
            "type_rapport": self.option_widgets['type_rapport'].get(),
            "redacteur_id": self.user_info[0]
        }
        
        for name, widget in self.text_widgets.items():
            data[name] = widget.get("1.0", "end-1c")

        if self.report_id:
            success = update_report(self.report_id, data)
        else:
            report_id = add_report(data)
            success = report_id is not None
            
        if success:
            messagebox.showinfo("Succès", "Le brouillon du rapport a été enregistré.", parent=self)
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
