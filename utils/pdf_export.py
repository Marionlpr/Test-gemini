# Fichier : utils/pdf_export.py
# Description : Fonctions pour générer des rapports et projets au format PDF.

from fpdf import FPDF
from tkinter import filedialog, messagebox
from datetime import datetime
from . import date_util
from models.youngs.youngs import get_young_details
from models.permissions.permissions import get_user_details
import os

# --- Chemin d'accès direct au fichier de police ---
# Construit le chemin vers le dossier 'assets' à la racine du projet.
FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
DEJAVU_SANS_PATH = os.path.join(FONT_DIR, "DejaVuSans.ttf")


class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 15)
        self.cell(0, 10, self.title, 0, 1, 'C')
        # CORRECTION: Interligne encore réduit
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, title, 0, 1, 'L', fill=True)
        # CORRECTION: Interligne encore réduit
        self.ln(1)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 11)
        self.multi_cell(0, 5, body) # Hauteur de ligne réduite
        self.ln(1)
    
    def objectif_block(self, categorie, objectif, moyens, evaluation):
        self.set_font('DejaVu', 'BI', 11)
        self.cell(0, 6, f"Catégorie : {categorie.capitalize()}", 0, 1) # Hauteur réduite
        
        self.set_font('DejaVu', 'B', 11)
        self.multi_cell(0, 5, f"Objectif : {objectif}") # Hauteur réduite
        self.ln(1)

        if moyens:
            self.set_font('DejaVu', 'I', 10)
            self.cell(0, 5, "Moyens associés :") # Hauteur réduite
            self.ln()
            self.set_font('DejaVu', '', 10)
            effective_page_width = self.w - self.l_margin - self.r_margin
            for moyen in moyens:
                self.set_x(self.l_margin + 5)
                self.multi_cell(effective_page_width - 5, 4, f"- {moyen}") # Hauteur réduite
            self.ln(1)

        if evaluation:
            self.set_font('DejaVu', 'I', 10)
            self.cell(0, 5, "Évaluation :") # Hauteur réduite
            self.ln()
            self.set_font('DejaVu', '', 10)
            self.multi_cell(0, 5, evaluation)
        
        self.ln(2) # Interligne de bloc réduit

    def add_info_section(self, info_dict):
        """Ajoute une section d'informations clé-valeur de manière robuste."""
        self.set_font('DejaVu', '', 10) # Taille de police réduite
        
        for label, value in info_dict.items():
            # Label en gras
            self.set_font('', 'B')
            # CORRECTION : Hauteur de ligne (h) encore plus réduite
            self.write(h=4, txt=f"{label}: ")
            
            # Valeur en normal
            self.set_font('', '')
            # CORRECTION : Hauteur de ligne (h) encore plus réduite
            self.multi_cell(0, 4, str(value or 'Non renseigné'))
        # CORRECTION : Interligne après la section réduit
        self.ln(1)

def _create_pdf_with_font():
    """Crée un objet PDF et y ajoute les polices DejaVu."""
    if not os.path.exists(DEJAVU_SANS_PATH):
        messagebox.showerror("Erreur de Police", f"Le fichier de police est introuvable:\n{DEJAVU_SANS_PATH}\n\nVeuillez le télécharger et le placer dans le dossier 'assets'.")
        return None

    pdf = PDF()
    pdf.add_font("DejaVu", "", DEJAVU_SANS_PATH)
    pdf.add_font("DejaVu", "B", DEJAVU_SANS_PATH)
    pdf.add_font("DejaVu", "I", DEJAVU_SANS_PATH)
    pdf.add_font("DejaVu", "BI", DEJAVU_SANS_PATH)
    return pdf


def export_report_to_pdf(report_details):
    if not report_details:
        messagebox.showerror("Erreur", "Aucun détail de rapport à exporter.")
        return

    pdf = _create_pdf_with_font()
    if not pdf: return
    
    pdf.set_title("Rapport Éducatif")
    pdf.add_page()
    
    young_details = get_young_details(report_details['young_id'])
    author_details = get_user_details(report_details['redacteur_id'])
    validator_details = get_user_details(report_details['validateur_id']) if report_details.get('validateur_id') else None

    young_name = f"{young_details.get('prenom', '')} {young_details.get('nom', '').upper()}" if young_details else "Inconnu"
    author_name = f"{author_details[2]} {author_details[1].upper()}" if author_details else "Inconnu"
    validator_name = f"{validator_details[2]} {validator_details[1].upper()}" if validator_details else "Non validé"

    pdf.chapter_title("Informations Générales")
    info = {
        "Jeune concerné": young_name,
        "Date de naissance": date_util.format_date_to_french(young_details.get('date_naissance')),
        "Date d'entrée": date_util.format_date_to_french(young_details.get('date_entree')),
        "Type de placement": young_details.get('type_placement'),
        "Type de rapport": report_details['type_rapport'],
        "Date de validation": date_util.format_date_to_french(report_details['date_redaction']),
        "Rédigé par": author_name,
        "Validé par": validator_name
    }
    pdf.add_info_section(info)

    report_sections = [
        ("rappel_situation", "Rappel de la situation"), ("accueil", "Accueil"), ("scolarite", "Scolarité"),
        ("soin_sante", "Soin / Santé"), ("famille", "Famille"), ("psychologique", "Psychologique"),
        ("preconisations", "Préconisations")
    ]
    for key, title in report_sections:
        pdf.chapter_title(title)
        pdf.chapter_body(report_details.get(key, "Non renseigné."))

    save_pdf_file(pdf, f"Rapport_{young_name.replace(' ', '_')}")

def export_projet_p_to_pdf(projet_data):
    if not projet_data:
        messagebox.showerror("Erreur", "Aucun détail de projet à exporter.")
        return

    pdf = _create_pdf_with_font()
    if not pdf: return
    
    pdf.set_title("Projet Personnalisé")
    pdf.add_page()
    
    details = projet_data.get('details', {})
    objectifs = projet_data.get('objectifs', [])
    young_details = get_young_details(details['young_id'])
    young_name = f"{young_details.get('prenom', '')} {young_details.get('nom', '').upper()}" if young_details else "Inconnu"

    pdf.chapter_title("Informations Générales")
    info = {
        "Jeune concerné": young_name,
        "Date de naissance": date_util.format_date_to_french(young_details.get('date_naissance')),
        "Date d'entrée": date_util.format_date_to_french(young_details.get('date_entree')),
        "Type de placement": young_details.get('type_placement'),
        "Date du projet": date_util.format_date_to_french(details.get('date_projet'))
    }
    pdf.add_info_section(info)

    text_sections = [
        ("rappel_situation", "Rappel de la situation"),
        ("attentes_jeune", "Attentes du jeune"),
        ("attentes_famille", "Attentes de la famille")
    ]
    for key, title in text_sections:
        pdf.chapter_title(title)
        pdf.chapter_body(details.get(key, "Non renseigné."))

    if objectifs:
        pdf.chapter_title("Objectifs")
        for obj in objectifs:
            pdf.objectif_block(
                categorie=obj.get('categorie', 'N/A'),
                objectif=obj.get('objectif', 'N/A'),
                moyens=obj.get('moyens', []),
                evaluation=obj.get('evaluation')
            )

    save_pdf_file(pdf, f"Projet_{young_name.replace(' ', '_')}")


def save_pdf_file(pdf_object, initial_filename):
    """Demande à l'utilisateur où sauvegarder le PDF et l'enregistre."""
    try:
        default_filename = f"{initial_filename}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            initialfile=default_filename,
            title="Enregistrer le document en PDF"
        )

        if filepath:
            pdf_object.output(filepath)
            messagebox.showinfo("Succès", f"Le document a été exporté avec succès.\n{filepath}")

    except Exception as e:
        messagebox.showerror("Erreur d'exportation", f"Une erreur est survenue lors de la création du PDF :\n{e}")
