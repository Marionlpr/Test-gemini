# Fichier : models/vehicles/vehicles.py
# Description : Fonctions pour la gestion des véhicules de l'établissement.

import sqlite3
from models.database.database import create_connection

def get_all_vehicles():
    """Récupère tous les véhicules de la base de données."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, marque, modele, plaque_immatriculation, nombre_places FROM vehicles ORDER BY marque, modele")
        vehicles = cursor.fetchall()
        return vehicles
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des véhicules : {e}")
        return []
    finally:
        conn.close()

def get_vehicle_details(vehicle_id):
    """Récupère les détails d'un véhicule spécifique."""
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
        details = cursor.fetchone()
        return dict(details) if details else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du véhicule : {e}")
        return None
    finally:
        conn.close()

def add_vehicle(data):
    """Ajoute un nouveau véhicule."""
    conn = create_connection()
    if conn is None: return False
    try:
        sql = '''INSERT INTO vehicles(marque, modele, plaque_immatriculation, nombre_places, puissance_fiscale)
                 VALUES(:marque, :modele, :plaque_immatriculation, :nombre_places, :puissance_fiscale)'''
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Erreur : Cette plaque d'immatriculation est déjà enregistrée.")
        return "exists"
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du véhicule : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_vehicle(vehicle_id, data):
    """Met à jour les informations d'un véhicule."""
    conn = create_connection()
    if conn is None: return False
    
    sql = '''UPDATE vehicles SET marque = :marque, modele = :modele, plaque_immatriculation = :plaque_immatriculation,
                                 nombre_places = :nombre_places, puissance_fiscale = :puissance_fiscale
             WHERE id = :id'''
    data['id'] = vehicle_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du véhicule : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_vehicle(vehicle_id):
    """Supprime un véhicule de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        # Gérer le cas où le véhicule est utilisé dans un trajet
        if "FOREIGN KEY constraint failed" in str(e):
             print("Impossible de supprimer ce véhicule car il est utilisé dans des trajets existants.")
             return "in_use"
        print(f"Erreur lors de la suppression du véhicule : {e}")
        return False
    finally:
        conn.close()
