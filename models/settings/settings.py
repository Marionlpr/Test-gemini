# Fichier : models/settings/settings.py
# Description : Gère la sauvegarde et le chargement des paramètres de l'application.

import json
import os
import customtkinter as ctk

# Utilisation d'un chemin absolu pour le fichier de paramètres pour plus de robustesse
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SETTINGS_FILE = os.path.join(APP_ROOT, "settings.json")

# Utilisation des thèmes de base intégrés pour une stabilité maximale
AVAILABLE_THEMES = ["blue", "dark-blue", "green"]
DEFAULT_SETTINGS = {
    "appearance_mode": "System",
    "color_theme": "blue"
}

def load_settings():
    """Charge les paramètres depuis le fichier JSON."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_SETTINGS

def save_settings(settings_dict):
    """Sauvegarde le dictionnaire de paramètres dans le fichier JSON."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4)
        return True
    except IOError as e:
        print(f"Erreur lors de la sauvegarde des paramètres : {e}")
        return False

def apply_settings(settings_dict):
    """Applique les paramètres visuels à l'application."""
    appearance_mode = settings_dict.get("appearance_mode", "System")
    color_theme = settings_dict.get("color_theme", "blue")
    
    # Vérifier que les valeurs sont valides
    if appearance_mode not in ["Light", "Dark", "System"]:
        appearance_mode = "System"
    if color_theme not in AVAILABLE_THEMES:
        color_theme = "blue"
        
    ctk.set_appearance_mode(appearance_mode)
    # On passe maintenant directement le nom du thème (une chaîne de caractères)
    ctk.set_default_color_theme(color_theme)

def get_available_themes():
    """Retourne la liste des thèmes de couleurs intégrés disponibles."""
    return AVAILABLE_THEMES
