# Fichier : gui/young_detail_view.py
# Description : Vue détaillée de la fiche d'un jeune, avec des onglets.

import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
# Imports directs des fonctions pour éviter les conflits
from models.youngs.youngs import get_young_details
from models.permissions.permissions import get_user_details
from models.services.services import get_service_details
from models.reports.reports import get_all_reports
from models.projet_p.projet_p import get_all_projets
from models.transmissions.transmissions import get_transmissions_for_young
from models.events.events import get_events_for_young
from utils import date_util
from .contacts_list import ContactsListView
from .report_form import ReportForm
from .projet_p_form import ProjetPersonnaliseForm

class YoungDetailView(ctk.CTkFrame):
    def __init__(self, parent, young_id, user_info):
        """
        Initialise la vue détaillée.
        """
        super().__init__(parent, corner_radius=10, fg_color=("gray90", "gray13"))
        self.young_id = young_id
        self.user_info = user_info
        
        self.color_map = {"vert": "#2E7D32", "orange": "#FF8F00", "rouge": "#C62828", "gris": "gray50"}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cadre du haut avec titre ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.top_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(side="left", padx=10, pady=10)

        # --- Système d'onglets ---
        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tab_view.add("Informations")
        self.tab_view.add("Contacts")
        self.tab_view.add("Agenda")
        self.tab_view.add("Transmissions")
        self.tab_view.add("Projet Personnalisé")
        self.tab_view.add("Rapports")

        # --- Remplissage des onglets ---
        self.populate_all_tabs()


    def populate_all_tabs(self):
        """Remplit ou met à jour tous les onglets avec les dernières informations."""
        tab_names = ["Informations", "Contacts", "Agenda", "Transmissions", "Projet Personnalisé", "Rapports"]
        for tab_name in tab_names:
             for widget in self.tab_view.tab(tab_name).winfo_children():
                widget.destroy()

        self.populate_info_tab(self.tab_view.tab("Informations"))
        self.populate_contacts_tab(self.tab_view.tab("Contacts"))
        self.populate_agenda_tab(self.tab_view.tab("Agenda"))
        self.populate_transmissions_tab(self.tab_view.tab("Transmissions"))
        self.populate_projets_tab(self.tab_view.tab("Projet Personnalisé"))
        self.populate_reports_tab(self.tab_view.tab("Rapports"))

    def populate_info_tab(self, tab):
        """Remplit l'onglet 'Informations' avec les détails du jeune."""
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        info_scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        info_scroll_frame.grid(row=0, column=0, sticky="nsew")
        info_scroll_frame.grid_columnconfigure(1, weight=1)
        
        details = get_young_details(self.young_id)
        if not details:
            ctk.CTkLabel(info_scroll_frame, text="Impossible de charger les informations.").pack(padx=20, pady=20)
            return

        self.title_label.configure(text=f"Fiche de {details.get('prenom')} {details.get('nom').upper()}")

        labels_map = {
            "Nom complet": f"{details.get('prenom')} {details.get('nom').upper()}",
            "Date de naissance": date_util.format_date_to_french(details.get('date_naissance')),
            "Lieu de naissance": details.get('lieu_naissance'),
            "Date d'entrée": date_util.format_date_to_french(details.get('date_entree')),
            "Statut": details.get('statut_accueil'),
            "Placement": details.get('type_placement'),
            "Accompagnement": details.get('type_accompagnement'),
            "--- Suivi ---": "",
            "Référent": "Chargement...", "Co-référent": "Chargement...", "Service": "Chargement...",
            "--- Échéances ---": "",
            "Échéance placement": date_util.format_date_to_french(details.get('date_echeance_placement')),
            "Date d'audience": date_util.format_date_to_french(details.get('date_audience')),
            "Date de synthèse (PEC)": date_util.format_date_to_french(details.get('date_synthese_pec')),
            "Échéance CJM": date_util.format_date_to_french(details.get('date_echeance_cjm')),
            "Date de sortie": date_util.format_date_to_french(details.get('date_sortie'))
        }

        if details.get('referent_id'):
            ref_details = get_user_details(details.get('referent_id'))
            labels_map["Référent"] = f"{ref_details[2]} {ref_details[1].upper()}" if ref_details else "Inconnu"
        else: labels_map["Référent"] = "Aucun"
        
        if details.get('co_referent_id'):
            coref_details = get_user_details(details.get('co_referent_id'))
            labels_map["Co-référent"] = f"{coref_details[2]} {coref_details[1].upper()}" if coref_details else "Inconnu"
        else: labels_map["Co-référent"] = "Aucun"

        if details.get('service_id'):
            srv_details = get_service_details(details.get('service_id'))
            labels_map["Service"] = srv_details[1] if srv_details else "Inconnu"
        else: labels_map["Service"] = "Aucun"

        row = 0
        for label_text, value_text in labels_map.items():
            if "---" in label_text: 
                ctk.CTkLabel(info_scroll_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold")).grid(row=row, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")
            else:
                ctk.CTkLabel(info_scroll_frame, text=f"{label_text} :", anchor="e").grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(info_scroll_frame, text=value_text or "Non renseigné", anchor="w", wraplength=400).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            row += 1

    def populate_contacts_tab(self, tab):
        contacts_view = ContactsListView(tab, self.young_id, self.user_info[1])
        contacts_view.pack(expand=True, fill="both")
        
    def populate_agenda_tab(self, tab):
        """Remplit l'onglet 'Agenda' avec l'historique des événements du jeune."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Historique des événements")
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        events_data = get_events_for_young(self.young_id)

        if not events_data:
            ctk.CTkLabel(scroll_frame, text="Aucun événement enregistré pour ce jeune.").pack(pady=20)
            return

        for event in events_data:
            event_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            event_frame.pack(fill="x", pady=5)
            
            debut_dt = datetime.fromisoformat(event['debut_datetime'])
            date_fr = date_util.format_date_to_french(debut_dt)
            heure_fr = debut_dt.strftime('%H:%M')
            
            label_text = f"{date_fr} à {heure_fr} - {event['nom_evenement']} ({event['type_evenement']})"
            ctk.CTkLabel(event_frame, text=label_text).pack(anchor="w")


    def populate_transmissions_tab(self, tab):
        """Remplit l'onglet 'Transmissions' avec l'historique du jeune."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Historique des transmissions")
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        transmissions_data = get_transmissions_for_young(self.young_id)

        if not transmissions_data:
            ctk.CTkLabel(scroll_frame, text="Aucune transmission enregistrée pour ce jeune.").pack(pady=20)
            return

        for trans in transmissions_data:
            trans_frame = ctk.CTkFrame(scroll_frame, border_width=1)
            trans_frame.pack(fill="x", padx=5, pady=5, anchor="n")
            trans_frame.grid_columnconfigure(1, weight=1)

            color_dot = ctk.CTkFrame(trans_frame, fg_color=self.color_map.get(trans.get('couleur'), "gray50"), width=15, height=15, corner_radius=10)
            color_dot.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")

            dt_obj = datetime.fromisoformat(trans['datetime_transmission'])
            header_text = f"{dt_obj.strftime('%d/%m/%Y à %H:%M')} | {trans['nom_service']} | par {trans['user_prenom']}"
            ctk.CTkLabel(trans_frame, text=header_text, font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").grid(row=0, column=1, sticky="w", padx=10, pady=(5,0))
            
            ctk.CTkLabel(trans_frame, text=trans['contenu'], wraplength=500, justify="left", anchor="w").grid(row=1, column=1, sticky="w", padx=10, pady=5)
            
    def populate_projets_tab(self, tab):
        """Remplit l'onglet 'Projet Personnalisé'."""
        tab.grid_columnconfigure(0, weight=1)
        projets = get_all_projets()
        young_projet = next((p for p in projets if p['young_id'] == self.young_id), None)

        if not young_projet:
            ctk.CTkLabel(tab, text="Aucun projet personnalisé enregistré pour ce jeune.").pack(pady=20)
            ctk.CTkButton(tab, text="Créer le Projet Personnalisé", command=lambda: self.open_projet_form(None)).pack(pady=10)
            return

        date_fr = date_util.format_date_to_french(young_projet['date_projet'])
        text = f"Projet du {date_fr}"
        ctk.CTkButton(tab, text=text, command=lambda: self.open_projet_form(young_projet['id'])).pack(fill="x", padx=20, pady=10)

    def populate_reports_tab(self, tab):
        """Remplit l'onglet 'Rapports' avec la liste des rapports du jeune."""
        tab.grid_columnconfigure(0, weight=1)
        reports = get_all_reports(young_id=self.young_id)

        if not reports:
            ctk.CTkLabel(tab, text="Aucun rapport enregistré pour ce jeune.").pack(pady=20)
            return
            
        for report in reports:
            date_fr = date_util.format_date_to_french(report['date_redaction']) or "Brouillon"
            text = f"{report['type_rapport'].capitalize()} - {date_fr}"
            ctk.CTkButton(tab, text=text, command=lambda r_id=report['id']: self.open_report_form(r_id)).pack(fill="x", padx=20, pady=5)
    
    def open_report_form(self, report_id):
        form = ReportForm(self, user_info=self.user_info, report_id=report_id)
        if form.show(): self.populate_all_tabs()

    def open_projet_form(self, projet_id):
        form = ProjetPersonnaliseForm(self, user_info=self.user_info, projet_id=projet_id)
        if form.show(): self.populate_all_tabs()

