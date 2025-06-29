# Fichier : gui/calendar_popup.py
# Description : Un widget de calendrier pop-up pour la sélection de date.

import customtkinter as ctk
import calendar
from datetime import date, datetime
import locale

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except locale.Error:
        print("Locale 'fr_FR' non disponible.")


class CalendarPopup(ctk.CTkToplevel):
    def __init__(self, parent, entry_widget=None, callback=None, initial_date=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Sélectionner une date")
        self.geometry("280x280")
        self.resizable(False, False)

        x = parent.winfo_x() + 50
        y = parent.winfo_y() + 50
        self.geometry(f"+{x}+{y}")

        self.entry_widget = entry_widget
        self.callback = callback # Pour rafraîchir une vue
        
        # Déterminer la date initiale à afficher
        if initial_date:
            self.current_date = initial_date
        elif self.entry_widget:
            try:
                self.current_date = datetime.strptime(self.entry_widget.get(), "%d-%m-%Y").date()
            except (ValueError, TypeError):
                self.current_date = date.today()
        else:
            self.current_date = date.today()
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(expand=True, fill="both")
        
        self.create_widgets()
        self.populate_calendar(self.current_date.year, self.current_date.month)

    def create_widgets(self):
        nav_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=5, padx=5)
        nav_frame.grid_columnconfigure(1, weight=1)

        prev_btn = ctk.CTkButton(nav_frame, text="<", width=30, command=self.prev_month)
        prev_btn.grid(row=0, column=0)
        self.month_year_label = ctk.CTkLabel(nav_frame, font=ctk.CTkFont(weight="bold"))
        self.month_year_label.grid(row=0, column=1)
        next_btn = ctk.CTkButton(nav_frame, text=">", width=30, command=self.next_month)
        next_btn.grid(row=0, column=2)

        days_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        days_frame.pack(fill="x", padx=5)
        days = ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
        for i, day in enumerate(days):
            days_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(days_frame, text=day, font=ctk.CTkFont(size=10)).grid(row=0, column=i, padx=1, pady=1)

        self.calendar_grid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.calendar_grid.pack(expand=True, fill="both", padx=5, pady=5)
        for i in range(7): self.calendar_grid.grid_columnconfigure(i, weight=1)
        for i in range(6): self.calendar_grid.grid_rowconfigure(i, weight=1)

    def populate_calendar(self, year, month):
        for widget in self.calendar_grid.winfo_children(): widget.destroy()
        cal = calendar.monthcalendar(year, month)
        self.month_year_label.configure(text=f"{calendar.month_name[month].capitalize()} {year}")

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day != 0:
                    day_btn = ctk.CTkButton(self.calendar_grid, text=str(day), height=30,
                                            command=lambda d=day: self.select_date(d))
                    if date(year, month, day) == date.today():
                        day_btn.configure(border_width=2)
                    day_btn.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

    def select_date(self, day):
        selected = date(self.current_date.year, self.current_date.month, day)
        if self.entry_widget:
            self.entry_widget.delete(0, "end")
            self.entry_widget.insert(0, selected.strftime("%d-%m-%Y"))
        if self.callback:
            self.callback(selected)
        self.destroy()

    def prev_month(self):
        year, month = self.current_date.year, self.current_date.month
        month -= 1
        if month == 0: month = 12; year -= 1
        self.current_date = date(year, month, 1)
        self.populate_calendar(year, month)

    def next_month(self):
        year, month = self.current_date.year, self.current_date.month
        month += 1
        if month == 13: month = 1; year += 1
        self.current_date = date(year, month, 1)
        self.populate_calendar(year, month)
