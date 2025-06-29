# Fichier : utils/date_util.py
# Description : Fonctions utilitaires pour la manipulation des dates.

from datetime import datetime

def format_date_to_french(date_str):
    """
    Convertit une date du format AAAA-MM-JJ au format français JJ-MM-AAAA.
    
    Args:
        date_str (str): La date sous forme de chaîne au format 'AAAA-MM-JJ'.
                        Peut aussi être un objet datetime.
                        Si l'entrée est None, vide ou invalide, retourne une chaîne vide.

    Returns:
        str: La date formatée en 'JJ-MM-AAAA' ou une chaîne vide.
    """
    if not date_str:
        return ""
    try:
        # Tente de convertir la chaîne en objet date
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        else: # Si c'est déjà un objet date/datetime
            date_obj = date_str
            
        return date_obj.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        # En cas d'erreur de format ou de type, on retourne une chaîne vide
        # pour ne pas faire planter l'application.
        return ""

def format_date_to_iso(date_str):
    """
    Convertit une date du format français JJ-MM-AAAA au format ISO AAAA-MM-JJ.
    C'est utile pour sauvegarder les dates dans la base de données de manière standard.
    
    Args:
        date_str (str): La date sous forme de chaîne au format 'JJ-MM-AAAA'.
                        Si l'entrée est None, vide ou invalide, retourne None.

    Returns:
        str: La date formatée en 'AAAA-MM-JJ' ou None.
    """
    if not date_str:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
        return date_obj.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None

# --- Exemples d'utilisation ---
if __name__ == '__main__':
    iso_date = "2023-10-27"
    french_date = format_date_to_french(iso_date)
    print(f"Date ISO '{iso_date}' devient '{french_date}' en format français.") # Devrait afficher 27-10-2023

    french_date_input = "25-12-2024"
    iso_date_output = format_date_to_iso(french_date_input)
    print(f"Date française '{french_date_input}' devient '{iso_date_output}' en format ISO.") # Devrait afficher 2024-12-25
    
    invalid_date = "ceci-n-est-pas-une-date"
    print(f"Test date invalide (fr): '{format_date_to_french(invalid_date)}'") # Devrait être vide
    print(f"Test date invalide (iso): '{format_date_to_iso(invalid_date)}'") # Devrait être None
    
    empty_date = ""
    print(f"Test date vide (fr): '{format_date_to_french(empty_date)}'") # Devrait être vide
    print(f"Test date vide (iso): '{format_date_to_iso(empty_date)}'") # Devrait être None
