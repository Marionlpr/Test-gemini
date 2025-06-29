# Fichier : gui/task_list.py
# Description : Vue pour afficher et gérer la liste des tâches ponctuelles.

import customtkinter as ctk
from tkinter import messagebox
from .task_form import TaskForm
from models.tasks.tasks import get_all_tasks_with_details, mark_task_as_done, unmark_task_as_done, delete_task
from utils import date_util

class TaskListView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        
        self.selected_task_id = None
        self.all_tasks = [] 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Cadre de contrôle compact ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1) # Pour pousser les boutons

        self.add_button = ctk.CTkButton(self.control_frame, text="Ajouter une tâche", command=self.add_task, height=28)
        self.add_button.grid(row=0, column=0, padx=10, pady=5)
        
        # --- Cadre des actions sur la sélection ---
        self.actions_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.actions_frame.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        self.done_button = ctk.CTkButton(self.actions_frame, text="Réalisée", state="disabled", command=self.mark_done, height=28)
        self.done_button.pack(side="left", padx=5)
        self.undo_button = ctk.CTkButton(self.actions_frame, text="Annuler", state="disabled", command=self.unmark_done, fg_color="#FFA000", hover_color="#FF8F00", height=28)
        self.undo_button.pack(side="left", padx=5)
        self.edit_button = ctk.CTkButton(self.actions_frame, text="Modifier", state="disabled", command=self.edit_task, height=28)
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(self.actions_frame, text="Supprimer", state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_task_action, height=28)
        self.delete_button.pack(side="left", padx=5)

        # --- Cadre principal pour la liste des tâches ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Tâches à effectuer")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.status_colors = {"urgent": "#D32F2F", "à faire": "#388E3C", "réalisée": "gray50"}
        self.radio_var = ctk.IntVar(value=0)

        self.refresh_list()

    def refresh_list(self):
        """Met à jour l'affichage des tâches."""
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.all_tasks = get_all_tasks_with_details()
        if not self.all_tasks:
            ctk.CTkLabel(self.scroll_frame, text="Aucune tâche enregistrée.").pack(pady=20)
            return
        for i, task in enumerate(self.all_tasks):
            task_id = task['id']
            date_limite_fr = date_util.format_date_to_french(task['date_limite']) or "Aucune"
            text = f"{task['tache_a_realiser']}\n"
            text += f"Limite: {date_limite_fr} | Assigné à: {task['user_name']} | Jeunes: {task['youngs_names']}"
            text_color = self.status_colors.get(task['statut'], "gray")
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=task_id,
                                              command=self.on_select, text_color=text_color)
            radio_button.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        self.on_select()

    def on_select(self):
        """Active les boutons d'action en fonction du statut de la tâche sélectionnée."""
        self.selected_task_id = self.radio_var.get()
        selected_task = next((task for task in self.all_tasks if task['id'] == self.selected_task_id), None)
        
        if selected_task:
            is_done = selected_task['statut'] == 'réalisée'
            self.done_button.configure(state="disabled" if is_done else "normal")
            self.edit_button.configure(state="disabled" if is_done else "normal")
            self.undo_button.configure(state="normal" if is_done else "disabled")
            self.delete_button.configure(state="normal")
        else:
            self.done_button.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.undo_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")

    def add_task(self):
        form = TaskForm(self)
        if form.show(): self.refresh_list()
    
    def edit_task(self):
        if self.selected_task_id:
            form = TaskForm(self, task_id=self.selected_task_id)
            if form.show(): self.refresh_list()

    def mark_done(self):
        if self.selected_task_id and mark_task_as_done(self.selected_task_id): self.refresh_list()
        elif self.selected_task_id: messagebox.showerror("Erreur", "La mise à jour a échoué.", parent=self)

    def unmark_done(self):
        if self.selected_task_id and unmark_task_as_done(self.selected_task_id): self.refresh_list()
        elif self.selected_task_id: messagebox.showerror("Erreur", "L'annulation a échoué.", parent=self)

    def delete_task_action(self):
        if self.selected_task_id and messagebox.askyesno("Confirmation", "Supprimer cette tâche ?", parent=self):
            if delete_task(self.selected_task_id): self.refresh_list()
            else: messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
