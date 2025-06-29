# Fichier : models/contacts/contacts.py
# Description : Fonctions pour la gestion des contacts des jeunes.

import sqlite3
from models.database.database import create_connection

def get_contacts_for_young(young_id):
    """Récupère tous les contacts associés à un jeune spécifique."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nom, prenom, lien_parente, telephone, email
            FROM young_contacts
            WHERE young_id = ?
            ORDER BY nom, prenom
        """, (young_id,))
        contacts = cursor.fetchall()
        return contacts
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des contacts : {e}")
        return []
    finally:
        conn.close()

def get_contact_details(contact_id):
    """Récupère les détails d'un contact spécifique."""
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM young_contacts WHERE id = ?", (contact_id,))
        details = cursor.fetchone()
        return dict(details) if details else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du contact : {e}")
        return None
    finally:
        conn.close()

def add_contact(data):
    """Ajoute un nouveau contact à la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        sql = '''INSERT INTO young_contacts(young_id, nom, prenom, lien_parente, adresse, telephone, email)
                 VALUES(:young_id, :nom, :prenom, :lien_parente, :adresse, :telephone, :email)'''
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du contact : {e}")
        return False
    finally:
        conn.close()

def update_contact(contact_id, data):
    """Met à jour les informations d'un contact."""
    conn = create_connection()
    if conn is None: return False
    
    sql = '''UPDATE young_contacts SET nom = :nom, prenom = :prenom, lien_parente = :lien_parente,
                                      adresse = :adresse, telephone = :telephone, email = :email
             WHERE id = :id'''
    data['id'] = contact_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du contact : {e}")
        return False
    finally:
        conn.close()

def delete_contact(contact_id):
    """Supprime un contact de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM young_contacts WHERE id = ?", (contact_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du contact : {e}")
        return False
    finally:
        conn.close()
