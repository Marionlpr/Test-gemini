# Fichier : gui/task_hebdo_list.py
# Description : Vue pour afficher et gérer les tâches hebdomadaires récurrentes.

import customtkinter as ctk
from tkinter import messagebox
from .task_hebdo_form import TaskHebdoForm
from models.tasks_hebdo import tasks_hebdo

class TaskHebdoListView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.control_frame, text="Ajouter une tâche hebdo", command=self.add_task)
        self.add_button.pack(side="left", padx=10, pady=10)
        
        self.edit_button = ctk.CTkButton(self.control_frame, text="Modifier la tâche", state="disabled", command=self.edit_task)
        self.edit_button.pack(side="left", padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.control_frame, text="Supprimer la tâche", state="disabled", fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_task)
        self.delete_button.pack(side="left", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Toutes les tâches hebdomadaires définies")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.radio_var = ctk.IntVar(value=0)
        self.selected_task_id = None
        
        self.refresh_list()

    def refresh_list(self):
        """Met à jour la liste des tâches affichée."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        all_tasks = tasks_hebdo.get_all_hebdo_tasks()
        
        day_order = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        try:
            sorted_tasks = sorted(all_tasks, key=lambda x: day_order.index(x[1].lower()))
        except ValueError:
            sorted_tasks = all_tasks

        if not sorted_tasks:
            ctk.CTkLabel(self.scroll_frame, text="Aucune tâche hebdomadaire définie.").pack(pady=20)
            return

        current_day = ""
        current_row = 0
        for task in sorted_tasks:
            task_id, jour, tache = task
            
            if jour.capitalize() != current_day:
                current_day = jour.capitalize()
                day_label = ctk.CTkLabel(self.scroll_frame, text=current_day, font=ctk.CTkFont(size=14, weight="bold"))
                day_label.grid(row=current_row, column=0, padx=5, pady=(10, 5), sticky="w")
                current_row += 1

            text = f"- {tache}"
            radio_button = ctk.CTkRadioButton(self.scroll_frame, text=text, variable=self.radio_var, value=task_id, command=self.on_select)
            radio_button.grid(row=current_row, column=0, padx=20, pady=2, sticky="w")
            current_row += 1
        
        self.on_select()

    def on_select(self):
        """Active les boutons d'action si une tâche est sélectionnée."""
        self.selected_task_id = self.radio_var.get()
        if self.selected_task_id:
            self.delete_button.configure(state="normal")
            self.edit_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")
            self.edit_button.configure(state="disabled")

    def add_task(self):
        form = TaskHebdoForm(self)
        if form.show():
            self.refresh_list()

    def edit_task(self):
        if not self.selected_task_id: return
        form = TaskHebdoForm(self, task_id=self.selected_task_id)
        if form.show():
            self.refresh_list()

    def delete_task(self):
        if not self.selected_task_id: return
        
        answer = messagebox.askyesno("Confirmation", "Supprimer cette tâche hebdomadaire récurrente ?", parent=self)
        if answer:
            if tasks_hebdo.delete_task_hebdo(self.selected_task_id):
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
