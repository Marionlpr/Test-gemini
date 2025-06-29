# Fichier : models/trips/trips.py
# Description : Fonctions pour la gestion des trajets.

import sqlite3
from models.database.database import create_connection

def get_all_trips():
    """Récupère tous les trajets avec les détails importants pour l'affichage."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Requête complexe pour joindre toutes les informations nécessaires
        cursor.execute("""
            SELECT
                t.id, t.date_trajet, t.motif,
                u.prenom || ' ' || u.nom AS professional_name,
                v.marque || ' ' || v.modele AS vehicle_name,
                s.nom_service
            FROM trips t
            JOIN users u ON t.user_id = u.id
            JOIN vehicles v ON t.vehicle_id = v.id
            JOIN services s ON t.service_id = s.id
            ORDER BY t.date_trajet DESC, t.heure_depart DESC
        """)
        trips = [dict(row) for row in cursor.fetchall()]

        # Pour chaque trajet, récupérer les jeunes associés
        for trip in trips:
            cursor.execute("""
                SELECT y.prenom, y.nom FROM youngs y
                JOIN trip_young_link tyl ON y.id = tyl.young_id
                WHERE tyl.trip_id = ?
            """, (trip['id'],))
            youngs_raw = cursor.fetchall()
            trip['youngs_names'] = ", ".join([f"{y['prenom']} {y['nom'].upper()}" for y in youngs_raw]) or "Aucun"

        return trips
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des trajets : {e}")
        return []
    finally:
        conn.close()

def get_trip_details(trip_id):
    """Récupère les détails d'un trajet et les participants."""
    conn = create_connection()
    if conn is None: return None, []
    
    details = None
    linked_youngs = []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        details_row = cursor.fetchone()
        if details_row:
            details = dict(details_row)

        cursor.execute("SELECT young_id FROM trip_young_link WHERE trip_id = ?", (trip_id,))
        linked_youngs_rows = cursor.fetchall()
        linked_youngs = [row['young_id'] for row in linked_youngs_rows]
        
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du trajet : {e}")
    finally:
        conn.close()
    return details, linked_youngs


def add_trip(data, young_ids):
    """Ajoute un nouveau trajet et lie les jeunes transportés."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO trips (date_trajet, heure_depart, heure_retour, motif, service_id, user_id, vehicle_id, km_depart, km_retour)
                 VALUES (:date_trajet, :heure_depart, :heure_retour, :motif, :service_id, :user_id, :vehicle_id, :km_depart, :km_retour)'''
        
        cursor.execute(sql, data)
        trip_id = cursor.lastrowid

        if trip_id and young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO trip_young_link (trip_id, young_id) VALUES (?, ?)", (trip_id, young_id))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du trajet : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_trip(trip_id, data, young_ids):
    """Met à jour un trajet et la liste des jeunes associés."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''UPDATE trips SET date_trajet=:date_trajet, heure_depart=:heure_depart, heure_retour=:heure_retour, 
                                  motif=:motif, service_id=:service_id, user_id=:user_id, vehicle_id=:vehicle_id, 
                                  km_depart=:km_depart, km_retour=:km_retour
                 WHERE id = :id'''
        data['id'] = trip_id
        cursor.execute(sql, data)

        cursor.execute("DELETE FROM trip_young_link WHERE trip_id = ?", (trip_id,))
        if young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO trip_young_link (trip_id, young_id) VALUES (?, ?)", (trip_id, young_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du trajet : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_trip(trip_id):
    """Supprime un trajet de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du trajet : {e}")
        return False
    finally:
        conn.close()
