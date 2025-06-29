# Fichier : gui/projet_p_form.py
# Description : Fenêtre pour rédiger ou modifier un projet personnalisé.

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from models.projet_p.projet_p import add_or_update_projet, get_projet_details
from models.youngs.youngs import get_all_youngs
from utils import date_util

class ProjetPersonnaliseForm(ctk.CTkToplevel):
    def __init__(self, parent, user_info, projet_id=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()

        self.parent = parent
        self.user_info = user_info
        self.projet_id = projet_id
        self.result = False

        self.title("Nouveau Projet Personnalisé" if projet_id is None else "Modifier le Projet Personnalisé")
        self.geometry("900x900")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.text_widgets = {}
        self.option_widgets = {}
        self.objectifs_widgets_list = []

        self.create_widgets()

        if self.projet_id:
            self.load_projet_data()

    def create_widgets(self):
        """Crée tous les widgets du formulaire."""
        # Options du haut (Jeune, Date)
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(options_frame, text="Jeune concerné *").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        youngs_data = get_all_youngs()
        self.youngs_map = {f"{y[2]} {y[1].upper()}": y[0] for y in youngs_data}
        young_names = list(self.youngs_map.keys())
        self.option_widgets['young_id'] = ctk.CTkOptionMenu(options_frame, values=young_names or ["Aucun jeune"])
        self.option_widgets['young_id'].grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(options_frame, text="Date du projet *").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.option_widgets['date_projet'] = ctk.CTkEntry(options_frame, placeholder_text="JJ-MM-AAAA")
        self.option_widgets['date_projet'].insert(0, date.today().strftime('%d-%m-%Y'))
        self.option_widgets['date_projet'].grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Sections de texte
        text_sections = [
            ("rappel_situation", "Rappel de la situation"),
            ("attentes_jeune", "Attentes du jeune"),
            ("attentes_famille", "Attentes de la famille")
        ]
        for name, label_text in text_sections:
            self.add_text_section(label_text, name)

        # Section Objectifs
        self.add_objectifs_section("Objectifs, Moyens et Évaluations")
        
        # Bouton de validation
        self.submit_button = ctk.CTkButton(self, text="Enregistrer le Projet", command=self.submit)
        self.submit_button.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

    def add_text_section(self, label_text, name):
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(fill="x", padx=10, pady=(15, 5))
        textbox = ctk.CTkTextbox(self.scrollable_frame, height=120, wrap="word")
        textbox.pack(fill="x", expand=True, padx=10)
        self.text_widgets[name] = textbox

    def add_objectifs_section(self, label_text):
        label = ctk.CTkLabel(self.scrollable_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(fill="x", padx=10, pady=(15, 5))
        
        self.objectifs_container = ctk.CTkFrame(self.scrollable_frame)
        self.objectifs_container.pack(fill="x", padx=10)
        
        btn_frame = ctk.CTkFrame(self.objectifs_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(btn_frame, text="+ Ajouter un Objectif", command=self.add_objectif_item).pack(side="left")
        ctk.CTkButton(btn_frame, text="- Supprimer Objectif", command=self.remove_objectif_item).pack(side="left", padx=10)

        self.add_objectif_item()

    def add_objectif_item(self, objectif_text="", categorie_text=None, evaluation_text="", moyens_list=None):
        if moyens_list is None or not moyens_list: moyens_list = [""]

        obj_frame = ctk.CTkFrame(self.objectifs_container, border_width=2, border_color="gray60")
        obj_frame.pack(fill="x", pady=10, padx=5, ipady=10)
        
        # --- CORRECTION : Menu déroulant pour la catégorie ---
        ctk.CTkLabel(obj_frame, text="Catégorie de l'objectif :").pack(anchor="w", padx=10, pady=(5,0))
        categories = ['éducatif', 'scolarité', 'soin/santé', 'famille', 'activités extérieures', 'autres']
        categorie_menu = ctk.CTkOptionMenu(obj_frame, values=categories)
        if categorie_text and categorie_text in categories:
            categorie_menu.set(categorie_text)
        categorie_menu.pack(fill="x", padx=10, pady=(0,10))
        # ---------------------------------------------------
        
        ctk.CTkLabel(obj_frame, text="Objectif :").pack(anchor="w", padx=10, pady=(5,0))
        objectif_entry = ctk.CTkEntry(obj_frame)
        objectif_entry.pack(fill="x", padx=10, pady=(0,10))
        objectif_entry.insert(0, objectif_text)
        
        moyens_container = ctk.CTkFrame(obj_frame)
        moyens_container.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(moyens_container, text="Moyens pour cet objectif :").pack(anchor="w", padx=5)
        
        moyens_btn_frame = ctk.CTkFrame(moyens_container, fg_color="transparent")
        moyens_btn_frame.pack(fill="x", padx=5)
        
        moyen_entries = []
        def add_moyen_entry(text=""):
            entry = ctk.CTkEntry(moyens_container)
            entry.pack(fill="x", pady=2, padx=5)
            entry.insert(0, text)
            moyen_entries.append(entry)

        ctk.CTkButton(moyens_btn_frame, text="+", width=30, command=lambda: add_moyen_entry()).pack(side="left")
        
        def remove_moyen_entry():
            if len(moyen_entries) > 1:
                moyen_entries.pop().destroy()
        ctk.CTkButton(moyens_btn_frame, text="-", width=30, command=remove_moyen_entry).pack(side="left", padx=5)

        for moyen in moyens_list:
            add_moyen_entry(moyen)

        ctk.CTkLabel(obj_frame, text="Évaluation de l'objectif :").pack(anchor="w", padx=10, pady=(10,0))
        evaluation_box = ctk.CTkTextbox(obj_frame, height=60, wrap="word")
        evaluation_box.pack(fill="x", expand=True, padx=10, pady=(0,10))
        evaluation_box.insert("0.0", evaluation_text)
        
        self.objectifs_widgets_list.append({
            'frame': obj_frame, 'objectif': objectif_entry, 'categorie': categorie_menu,
            'evaluation': evaluation_box, 'moyens': moyen_entries
        })

    def remove_objectif_item(self):
        if len(self.objectifs_widgets_list) > 1:
            item_to_remove = self.objectifs_widgets_list.pop()
            item_to_remove['frame'].destroy()

    def load_projet_data(self):
        data = get_projet_details(self.projet_id)
        if not data: return
        details = data.get('details', {})

        for name, y_id in self.youngs_map.items():
            if y_id == details.get('young_id'):
                self.option_widgets['young_id'].set(name)
                self.option_widgets['young_id'].configure(state="disabled")
                break
        
        date_fr = date_util.format_date_to_french(details.get('date_projet'))
        self.option_widgets['date_projet'].delete(0, "end")
        self.option_widgets['date_projet'].insert(0, date_fr)

        for name, widget in self.text_widgets.items():
            widget.insert("0.0", details.get(name, ""))

        for widget_dict in self.objectifs_widgets_list: widget_dict['frame'].destroy()
        self.objectifs_widgets_list.clear()
        
        objectifs_data = data.get('objectifs', [])
        if not objectifs_data:
            self.add_objectif_item()
        else:
            for obj_dict in objectifs_data:
                self.add_objectif_item(
                    objectif_text=obj_dict.get('objectif', ''),
                    categorie_text=obj_dict.get('categorie'),
                    evaluation_text=obj_dict.get('evaluation', ''),
                    moyens_list=obj_dict.get('moyens')
                )

    def submit(self):
        young_name = self.option_widgets['young_id'].get()
        date_str = self.option_widgets['date_projet'].get()
        if young_name == "Aucun jeune" or not date_str:
            messagebox.showerror("Validation", "Le jeune et la date du projet sont obligatoires.", parent=self)
            return

        data = {
            "young_id": self.youngs_map.get(young_name),
            "date_projet": date_util.format_date_to_iso(date_str)
        }
        for name, widget in self.text_widgets.items():
            data[name] = widget.get("1.0", "end-1c")

        data['objectifs'] = []
        for item_widgets in self.objectifs_widgets_list:
            objectif_text = item_widgets['objectif'].get()
            if objectif_text:
                data['objectifs'].append({
                    'objectif': objectif_text,
                    'categorie': item_widgets['categorie'].get(),
                    'evaluation': item_widgets['evaluation'].get("1.0", "end-1c"),
                    'moyens': [entry.get() for entry in item_widgets['moyens'] if entry.get()]
                })

        result = add_or_update_projet(data, self.projet_id)
            
        if result is True:
            messagebox.showinfo("Succès", "Projet personnalisé enregistré.", parent=self)
            self.result = True
            self.destroy()
        elif result == "exists":
            messagebox.showerror("Erreur", "Un projet personnalisé existe déjà pour ce jeune.\nVeuillez le modifier depuis la liste.", parent=self)
        else:
            messagebox.showerror("Erreur", "L'enregistrement a échoué.", parent=self)

    def show(self):
        self.deiconify()
        self.wait_window()
        return self.result
