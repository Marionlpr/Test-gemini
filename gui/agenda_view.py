# Fichier : gui/agenda_view.py
# Description : Interface graphique de l'agenda hebdomadaire (Version Stable).

import customtkinter as ctk
from tkinter import Menu, messagebox
from datetime import date, timedelta, datetime
import locale
from .event_form import EventForm
from .calendar_popup import CalendarPopup
from models.events.events import get_events_for_period, delete_event
from models.tasks_hebdo.tasks_hebdo import get_tasks_for_day
from models.permissions.permissions import get_user_details
from models.services.services import get_all_services_for_form

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")

class AgendaView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.user_info = user_info
        user_id, self.user_level = self.user_info
        
        user_details = get_user_details(self.user_info[0])
        self.user_service_id = user_details[9] if user_details and len(user_details) > 9 else None
        
        self.current_date = date.today()
        self.view_mode = "week" 
        self.selected_service_id = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_widgets()
        self.update_agenda_display()

    def create_widgets(self):
        """Crée les widgets principaux de l'agenda."""
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.nav_frame.grid_columnconfigure(1, weight=1)

        left_nav_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        left_nav_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left_nav_frame, text="Service:").pack(side="left", padx=(10,5))
        self.services_map = {name: s_id for s_id, name in get_all_services_for_form()}
        service_names = ["Tous les services"] + list(self.services_map.keys())
        self.service_filter_menu = ctk.CTkOptionMenu(left_nav_frame, values=service_names, command=self.on_filter_change, height=28)
        self.service_filter_menu.pack(side="left", padx=(0,10))

        date_nav_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        date_nav_frame.grid(row=0, column=1, sticky="ew")
        date_nav_frame.grid_columnconfigure(1, weight=1)
        self.prev_button = ctk.CTkButton(date_nav_frame, text="<", width=30, height=28, command=self.go_to_previous)
        self.prev_button.pack(side="left", padx=(10,5))
        self.calendar_button = ctk.CTkButton(date_nav_frame, text="🗓️", width=35, height=28, command=self.open_calendar_picker)
        self.calendar_button.pack(side="left")
        self.date_label = ctk.CTkLabel(date_nav_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.date_label.pack(side="left", padx=10, expand=True)
        self.next_button = ctk.CTkButton(date_nav_frame, text=">", width=30, height=28, command=self.go_to_next)
        self.next_button.pack(side="left", padx=(5,10))

        right_nav_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        right_nav_frame.grid(row=0, column=2, sticky="e")
        self.today_button = ctk.CTkButton(right_nav_frame, text="Aujourd'hui", command=self.go_to_today, height=28)
        self.today_button.pack(side="left", padx=10)
        self.toggle_view_button = ctk.CTkButton(right_nav_frame, text="Vue Journée", command=self.toggle_view, height=28)
        self.toggle_view_button.pack(side="left", padx=10)
        
        self.calendar_container = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_container.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.calendar_container.grid_rowconfigure(0, weight=1)
        self.calendar_container.grid_columnconfigure(0, weight=1)

        self.week_view_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        self.week_view_frame.grid_rowconfigure(0, weight=1)
        
        self.day_view_frame = ctk.CTkFrame(self.calendar_container, fg_color="transparent")
        self.day_view_frame.grid_rowconfigure(0, weight=1)
        self.day_view_frame.grid_columnconfigure(0, weight=1)
        
        self.day_widgets = []
        for i in range(7):
            container = ctk.CTkFrame(self.week_view_frame, border_width=1)
            self.day_widgets.append({"container": container})

    def on_filter_change(self, choice=None):
        self.selected_service_id = self.services_map.get(choice) if choice != "Tous les services" else None
        self.update_agenda_display()

    def update_agenda_display(self):
        """Met à jour le contenu et la disposition de l'agenda."""
        # CORRECTION: On retire la logique qui désactivait le filtre pour les standards.
        # Le filtrage des données se fait dans la requête SQL, c'est plus sûr.
        self.update_view_layout()

    def update_view_layout(self):
        """Ajuste la visibilité des cadres et les textes des boutons."""
        if self.view_mode == "week":
            self.day_view_frame.grid_forget()
            self.week_view_frame.grid(row=0, column=0, sticky="nsew")
            self.toggle_view_button.configure(text="Vue Journée")
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            self.date_label.configure(text=f"Semaine du {start_of_week.strftime('%d/%m/%Y')} au {(start_of_week + timedelta(days=6)).strftime('%d/%m/%Y')}")
            self.update_week_content()
        elif self.view_mode == "day":
            self.week_view_frame.grid_forget()
            self.day_view_frame.grid(row=0, column=0, sticky="nsew")
            self.toggle_view_button.configure(text="Vue Semaine")
            self.date_label.configure(text=self.current_date.strftime('%A %d %B %Y').capitalize())
            self.update_day_view_content()

    def update_week_content(self):
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        week_events = get_events_for_period(start_of_week.isoformat(), (start_of_week + timedelta(days=6)).isoformat(), service_id=self.selected_service_id)
        
        for i in range(7):
            self.week_view_frame.grid_columnconfigure(i, weight=1, uniform="day_column")
            day_date = start_of_week + timedelta(days=i)
            self.day_widgets[i]["container"].grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.create_day_column_content(self.day_widgets[i]["container"], day_date, week_events)
    
    def update_day_view_content(self):
        for widget in self.day_view_frame.winfo_children(): widget.destroy()
        
        day_container = ctk.CTkFrame(self.day_view_frame, border_width=1)
        day_container.grid(row=0, column=0, sticky="nsew")
        
        self.create_day_column_content(day_container, self.current_date)

    def create_day_column_content(self, container, day_date, events_list=None):
        for widget in container.winfo_children(): widget.destroy()
        
        container.grid_rowconfigure(2, weight=1); container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(container, text=f"{day_date.strftime('%A').capitalize()}\n{day_date.strftime('%d/%m')}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="ew")
        hebdo_frame = ctk.CTkFrame(container, fg_color=("gray85", "gray20"), corner_radius=5)
        hebdo_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        events_scroll = ctk.CTkScrollableFrame(container, label_text="")
        events_scroll.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        if events_list is None:
            events_list = get_events_for_period(day_date.isoformat(), day_date.isoformat(), service_id=self.selected_service_id)
        
        day_name_fr = day_date.strftime("%A").lower()
        hebdo_tasks = get_tasks_for_day(day_name_fr, self.user_service_id) if self.user_service_id else []
        if hebdo_tasks:
            for task in hebdo_tasks: ctk.CTkLabel(hebdo_frame, text=f"- {task[1]}", anchor="w", font=ctk.CTkFont(size=11)).pack(fill="x", padx=5, pady=1)
        else:
            ctk.CTkLabel(hebdo_frame, text="Aucune tâche récurrente", anchor="center", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").pack(fill="x", padx=5, pady=1)

        add_button = ctk.CTkButton(events_scroll, text="+ Ajouter", height=20, command=lambda d=day_date: self.open_event_form(initial_date=d))
        add_button.pack(fill="x", padx=5, pady=5)
        
        events_for_this_day = [e for e in events_list if datetime.fromisoformat(e['debut_datetime']).date() == day_date]
        for event in sorted(events_for_this_day, key=lambda e: e['debut_datetime']):
            event_id = event.get('id')
            nom = event.get('nom_evenement')
            debut_dt = datetime.fromisoformat(event['debut_datetime'])
            young_names = event.get('young_names')
            
            display_text = f"{debut_dt.strftime('%H:%M')} - {nom}"
            if young_names: display_text += f"\n({young_names})"
            event_widget = ctk.CTkButton(events_scroll, text=display_text, anchor="w", command=lambda eid=event_id: self.open_event_form(event_id=eid))
            event_widget.pack(fill="x", padx=5, pady=(0, 3))
            
            context_menu = Menu(event_widget, tearoff=0)
            context_menu.add_command(label="Modifier", command=lambda eid=event_id: self.open_event_form(event_id=eid))
            context_menu.add_command(label="Supprimer", command=lambda eid=event_id: self.delete_event_action(eid))
            event_widget.bind("<Button-3>", lambda e, menu=context_menu: menu.tk_popup(e.x_root, e.y_root))

        if day_date == date.today(): container.configure(border_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], border_width=2)
        else: container.configure(border_color="gray20", border_width=1)
            
    def toggle_view(self):
        self.view_mode = "day" if self.view_mode == "week" else "week"
        self.update_agenda_display()

    def go_to_previous(self):
        self.current_date -= timedelta(days=1 if self.view_mode == "day" else 7)
        self.update_agenda_display()

    def go_to_next(self):
        self.current_date += timedelta(days=1 if self.view_mode == "day" else 7)
        self.update_agenda_display()
        
    def go_to_today(self): self.current_date = date.today(); self.update_agenda_display()
    
    def open_calendar_picker(self):
        CalendarPopup(self, callback=self.set_date_and_refresh, initial_date=self.current_date)
    
    def set_date_and_refresh(self, selected_date):
        self.current_date = selected_date
        self.update_agenda_display()

    def open_event_form(self, event_id=None, initial_date=None):
        form = EventForm(self, self.user_info, event_id=event_id, initial_date=initial_date)
        if form.show(): self.update_agenda_display()
    def delete_event_action(self, event_id):
        if messagebox.askyesno("Confirmation", "Supprimer cet événement ?", parent=self):
            if delete_event(event_id): self.update_agenda_display()
            else: messagebox.showerror("Erreur", "La suppression a échoué.", parent=self)
    def refresh_list(self): self.update_agenda_display()
