# Fichier : models/events/events.py
# Description : Fonctions pour la gestion des événements de l'agenda.

import sqlite3
from models.database.database import create_connection
from datetime import datetime

def get_events_for_period(start_date, end_date, service_id=None):
    """
    Récupère les événements pour une période donnée.
    Filtre par service en se basant sur les jeunes associés.
    Les événements sans jeunes associés sont considérés comme généraux et toujours affichés.
    """
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # CORRECTION : La requête SQL a été entièrement revue pour un filtrage correct.
        sql = """
            SELECT
                e.id,
                e.nom_evenement,
                e.debut_datetime,
                e.fin_datetime,
                e.type_evenement,
                GROUP_CONCAT(y.prenom, ', ') as young_names
            FROM events e
            LEFT JOIN event_young_link eyl ON e.id = eyl.event_id
            LEFT JOIN youngs y ON eyl.young_id = y.id
            WHERE
                DATE(e.debut_datetime) BETWEEN ? AND ?
            GROUP BY e.id
            HAVING
                -- Condition pour afficher l'événement si:
                -- 1. Aucun filtre de service n'est appliqué
                ? IS NULL
                -- 2. OU si l'événement n'est lié à aucun jeune (événement général)
                OR COUNT(y.id) = 0
                -- 3. OU si au moins un des jeunes liés appartient au service filtré
                OR MAX(CASE WHEN y.service_id = ? THEN 1 ELSE 0 END) = 1
            ORDER BY e.debut_datetime
        """
        params = (start_date, end_date, service_id, service_id)
        
        cursor.execute(sql, params)
        events = [dict(row) for row in cursor.fetchall()]
        return events
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des événements par période : {e}")
        return []
    finally:
        conn.close()

def get_events_for_young(young_id):
    """Récupère tous les événements associés à un jeune spécifique, classés par date."""
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_evenement, debut_datetime, fin_datetime, type_evenement FROM events e JOIN event_young_link eyl ON e.id = eyl.event_id WHERE eyl.young_id = ? ORDER BY e.debut_datetime DESC", (young_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des événements pour le jeune : {e}")
        return []
    finally: conn.close()

def get_event_details(event_id):
    """Récupère les détails d'un événement, y compris les participants."""
    conn = create_connection()
    if conn is None: return None, []
    
    details, linked_youngs = None, []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        details_row = cursor.fetchone()
        if details_row:
            details = dict(details_row)

        cursor.execute("SELECT young_id FROM event_young_link WHERE event_id = ?", (event_id,))
        linked_youngs_rows = cursor.fetchall()
        linked_youngs = [row['young_id'] for row in linked_youngs_rows]
        
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails de l'événement : {e}")
    finally:
        conn.close()
    return details, linked_youngs

def add_event(data, young_ids):
    """Ajoute un nouvel événement et le lie aux jeunes sélectionnés."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO events(nom_evenement, debut_datetime, fin_datetime, type_evenement, user_id)
                 VALUES(:nom_evenement, :debut_datetime, :fin_datetime, :type_evenement, :user_id)'''
        
        cursor.execute(sql, data)
        event_id = cursor.lastrowid

        if event_id and young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO event_young_link (event_id, young_id) VALUES (?, ?)", (event_id, young_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'événement : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_event(event_id, data, young_ids):
    """Met à jour un événement et la liste des jeunes associés."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''UPDATE events SET nom_evenement = :nom_evenement, debut_datetime = :debut_datetime,
                                    fin_datetime = :fin_datetime, type_evenement = :type_evenement, user_id = :user_id
                 WHERE id = :id'''
        data['id'] = event_id
        cursor.execute(sql, data)

        cursor.execute("DELETE FROM event_young_link WHERE event_id = ?", (event_id,))
        if young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO event_young_link (event_id, young_id) VALUES (?, ?)", (event_id, young_id))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'événement : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_event(event_id):
    """Supprime un événement de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'événement : {e}")
        return False
    finally:
        conn.close()
