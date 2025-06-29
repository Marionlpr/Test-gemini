# Fichier : models/transmissions/transmissions.py
# Description : Fonctions pour la gestion des transmissions.

import sqlite3
from models.database.database import create_connection
from datetime import datetime

def get_transmissions_for_period(start_date, end_date, service_id=None):
    """
    Récupère toutes les transmissions pour un service et une période donnés.
    """
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                t.id, t.contenu, t.datetime_transmission, t.categorie, t.user_id, t.couleur,
                u.prenom as user_prenom, u.nom as user_nom, s.nom_service
            FROM transmissions t
            JOIN users u ON t.user_id = u.id
            JOIN services s ON t.service_id = s.id
            WHERE DATE(t.datetime_transmission) BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if service_id is not None:
            sql += " AND t.service_id = ?"
            params.append(service_id)
        sql += " ORDER BY t.datetime_transmission DESC"
        cursor.execute(sql, tuple(params))
        
        transmissions = [dict(row) for row in cursor.fetchall()]

        for trans in transmissions:
            cursor.execute("SELECT y.prenom, y.nom FROM youngs y JOIN transmission_young_link tyl ON y.id = tyl.young_id WHERE tyl.transmission_id = ?", (trans['id'],))
            trans['linked_youngs'] = ", ".join([f"{y['prenom']} {y['nom'].upper()}" for y in cursor.fetchall()]) or "Général"
        return transmissions
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des transmissions : {e}")
        return []
    finally:
        conn.close()

def get_transmissions_for_young(young_id):
    """Récupère toutes les transmissions associées à un jeune spécifique."""
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # CORRECTION: Ajout de la colonne 'couleur' à la requête SELECT
        cursor.execute("""
            SELECT
                t.id, t.contenu, t.datetime_transmission, t.categorie, t.couleur,
                u.prenom as user_prenom, u.nom as user_nom,
                s.nom_service
            FROM transmissions t
            JOIN transmission_young_link tyl ON t.id = tyl.transmission_id
            JOIN users u ON t.user_id = u.id
            JOIN services s ON t.service_id = s.id
            WHERE tyl.young_id = ?
            ORDER BY t.datetime_transmission DESC
        """, (young_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des transmissions pour le jeune : {e}")
        return []
    finally:
        conn.close()

def get_latest_transmissions(limit=15, service_id=None):
    """Récupère les dernières transmissions, y compris les jeunes liés."""
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql = """
            SELECT 
                t.id, t.contenu, t.datetime_transmission, t.couleur,
                u.prenom as user_prenom, u.nom as user_nom, s.nom_service
            FROM transmissions t
            JOIN users u ON t.user_id = u.id
            JOIN services s ON t.service_id = s.id
        """
        params = []
        if service_id is not None:
            sql += " WHERE t.service_id = ?"
            params.append(service_id)
        sql += " ORDER BY t.datetime_transmission DESC LIMIT ?"
        params.append(limit)
        transmissions = [dict(row) for row in cursor.execute(sql, tuple(params))]
        for trans in transmissions:
            cursor.execute("SELECT y.prenom, y.nom FROM youngs y JOIN transmission_young_link tyl ON y.id = tyl.young_id WHERE tyl.transmission_id = ?", (trans['id'],))
            trans['linked_youngs'] = ", ".join([f"{y['prenom']} {y['nom'].upper()}" for y in cursor.fetchall()]) or "Général"
        return transmissions
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des dernières transmissions: {e}")
        return []
    finally:
        conn.close()

def get_transmission_details(transmission_id):
    conn = create_connection()
    if conn is None: return None, []
    details, linked_youngs = None, []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transmissions WHERE id = ?", (transmission_id,))
        details_row = cursor.fetchone()
        if details_row:
            details = dict(details_row)
        cursor.execute("SELECT young_id FROM transmission_young_link WHERE transmission_id = ?", (transmission_id,))
        linked_youngs_rows = cursor.fetchall()
        linked_youngs = [row['young_id'] for row in linked_youngs_rows]
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails de la transmission : {e}")
    finally:
        conn.close()
    return details, linked_youngs

def add_transmission(data, young_ids):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO transmissions(service_id, user_id, datetime_transmission, categorie, contenu, couleur)
                 VALUES(:service_id, :user_id, :datetime_transmission, :categorie, :contenu, :couleur)'''
        cursor.execute(sql, data)
        transmission_id = cursor.lastrowid
        if transmission_id and young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO transmission_young_link (transmission_id, young_id) VALUES (?, ?)", (transmission_id, young_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de la transmission : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_transmission(transmission_id, data, young_ids):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''UPDATE transmissions SET service_id = :service_id, categorie = :categorie, 
                                          contenu = :contenu, datetime_transmission = :datetime_transmission,
                                          couleur = :couleur
                 WHERE id = :id'''
        data['id'] = transmission_id
        cursor.execute(sql, data)
        cursor.execute("DELETE FROM transmission_young_link WHERE transmission_id = ?", (transmission_id,))
        if young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO transmission_young_link (transmission_id, young_id) VALUES (?, ?)", (transmission_id, young_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de la transmission : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_transmission(transmission_id):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transmissions WHERE id = ?", (transmission_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de la transmission : {e}")
        return False
    finally:
        conn.close()
