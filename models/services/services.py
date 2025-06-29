# Fichier : models/services/services.py
# Description : Fonctions pour la gestion des services de l'établissement.

print("\n[DIAGNOSTIC] >>> Le fichier 'models/services/services.py' est en cours de chargement.\n")

import sqlite3
from models.database.database import create_connection

def get_all_services():
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_service, adresse, telephone FROM services ORDER BY nom_service")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des services : {e}")
        return []
    finally:
        conn.close()

def get_service_details(service_id):
    conn = create_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du service : {e}")
        return None
    finally:
        conn.close()

def add_service(data):
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
        return "exists"
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du service : {e}")
        return False
    finally:
        conn.close()

def update_service(service_id, data):
    conn = create_connection()
    if conn is None: return False
    sql = '''UPDATE services SET nom_service = :nom_service, adresse = :adresse, telephone = :telephone
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
    print("[DIAGNOSTIC] >>> Appel de la fonction 'get_all_services_for_form' dans services.py")
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_service FROM services ORDER BY nom_service")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des services : {e}")
        return []
    finally:
        conn.close()
