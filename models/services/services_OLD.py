# Fichier : models/services/services.py
# Description : Fonctions pour la gestion des services de l'établissement.

# ==========================================================
# === TEST DE DIAGNOSTIC : CE MESSAGE DOIT APPARAÎTRE ===
print("DIAGNOSTIC: Le fichier models/services/services.py a été correctement chargé.")
# ==========================================================

import sqlite3
from models.database.database import create_connection

def get_all_services():
    """Récupère tous les services de la base de données."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_service, adresse, telephone FROM services ORDER BY nom_service")
        services = cursor.fetchall()
        return services
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des services : {e}")
        return []
    finally:
        conn.close()

def get_service_details(service_id):
    """Récupère les détails d'un service spécifique."""
    conn = create_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        service_details = cursor.fetchone()
        return service_details
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du service : {e}")
        return None
    finally:
        conn.close()

def add_service(data):
    """Ajoute un nouveau service dans la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        sql = '''INSERT INTO services(nom_service, adresse, telephone)
                 VALUES(:nom_service, :adresse, :telephone)'''
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Erreur d'intégrité : ce nom de service existe déjà.")
        return "exists"
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du service : {e}")
        return False
    finally:
        conn.close()

def update_service(service_id, data):
    """Met à jour les informations d'un service."""
    conn = create_connection()
    if conn is None: return False
    
    sql = '''UPDATE services SET nom_service = :nom_service,
                                 adresse = :adresse,
                                 telephone = :telephone
             WHERE id = :id'''
    data['id'] = service_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du service : {e}")
        return False
    finally:
        conn.close()

def delete_service(service_id):
    """Supprime un service de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET service_id = NULL WHERE service_id = ?", (service_id,))
        cursor.execute("UPDATE youngs SET service_id = NULL WHERE service_id = ?", (service_id,))
        
        cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du service : {e}")
        return False
    finally:
        conn.close()

def get_all_services_for_form():
    """Récupère tous les services pour les utiliser dans un formulaire."""
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_service FROM services ORDER BY nom_service")
        services = cursor.fetchall()
        return services # Retourne une liste de tuples (id, nom_service)
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des services : {e}")
        return []
    finally:
        conn.close()
