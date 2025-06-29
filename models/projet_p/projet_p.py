# Fichier : models/projet_p/projet_p.py
# Description : Fonctions pour la gestion des projets personnalisés.

import sqlite3
from models.database.database import create_connection
from datetime import datetime, date

def get_all_projets():
    """Récupère tous les projets personnalisés avec les noms des jeunes."""
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                pp.id, pp.date_projet, pp.young_id,
                y.prenom, y.nom
            FROM projet_p pp
            JOIN youngs y ON pp.young_id = y.id
            ORDER BY pp.date_projet DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des projets personnalisés : {e}")
        return []
    finally:
        conn.close()

def get_projet_details(projet_id):
    """Récupère les détails d'un projet, y compris les objectifs, catégories, évaluations et moyens associés."""
    conn = create_connection()
    if conn is None: return None
    
    results = {}
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projet_p WHERE id = ?", (projet_id,))
        projet_details = cursor.fetchone()
        if not projet_details: return None
        results['details'] = dict(projet_details)

        # Récupère la catégorie avec l'objectif et son évaluation
        cursor.execute("SELECT id, objectif, categorie, evaluation FROM projet_p_objectifs WHERE projet_p_id = ?", (projet_id,))
        objectifs_data = [dict(row) for row in cursor.fetchall()]

        # Pour chaque objectif, récupérer les moyens liés
        for obj in objectifs_data:
            cursor.execute("SELECT moyen FROM projet_p_moyens WHERE objectif_id = ?", (obj['id'],))
            obj['moyens'] = [row['moyen'] for row in cursor.fetchall()]
        
        results['objectifs'] = objectifs_data
        
        return results
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du projet : {e}")
        return None
    finally:
        conn.close()

def add_or_update_projet(data, projet_id=None):
    """Ajoute ou met à jour un projet personnalisé et toutes ses données imbriquées."""
    conn = create_connection()
    if conn is None: return False
    
    try:
        cursor = conn.cursor()
        
        objectifs_data = data.pop('objectifs', [])
        
        if projet_id is None: # Mode Ajout
            sql_projet = '''INSERT INTO projet_p(date_projet, young_id, rappel_situation, attentes_jeune, attentes_famille)
                            VALUES(:date_projet, :young_id, :rappel_situation, :attentes_jeune, :attentes_famille)'''
            cursor.execute(sql_projet, data)
            projet_id = cursor.lastrowid
        else: # Mode Modification
            cursor.execute("DELETE FROM projet_p_objectifs WHERE projet_p_id = ?", (projet_id,))
            
            sql_projet = '''UPDATE projet_p SET date_projet = :date_projet, young_id = :young_id, rappel_situation = :rappel_situation,
                                            attentes_jeune = :attentes_jeune, attentes_famille = :attentes_famille
                            WHERE id = :id'''
            data['id'] = projet_id
            cursor.execute(sql_projet, data)

        # Insérer les nouveaux objectifs et moyens
        for obj_dict in objectifs_data:
            objectif_text = obj_dict.get('objectif')
            if objectif_text:
                sql_objectif = "INSERT INTO projet_p_objectifs (projet_p_id, objectif, categorie, evaluation) VALUES (?, ?, ?, ?)"
                cursor.execute(sql_objectif, (projet_id, objectif_text, obj_dict.get('categorie'), obj_dict.get('evaluation')))
                objectif_id = cursor.lastrowid
                
                for moyen_text in obj_dict.get('moyens', []):
                    if moyen_text:
                        sql_moyen = "INSERT INTO projet_p_moyens (objectif_id, moyen) VALUES (?, ?)"
                        cursor.execute(sql_moyen, (objectif_id, moyen_text))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Erreur: Un projet personnalisé existe déjà pour ce jeune.")
        conn.rollback()
        return "exists"
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout/mise à jour du projet : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_projet(projet_id):
    """Supprime un projet personnalisé et toutes ses données associées."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        # La suppression en cascade s'occupe des objectifs et moyens
        cursor.execute("DELETE FROM projet_p WHERE id = ?", (projet_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du projet : {e}")
        return False
    finally:
        conn.close()


def calculate_next_project_date(start_date_str):
    """Calcule la date un an après la date fournie."""
    if not start_date_str: return "Date de départ non valide"
    try:
        start_date = date.fromisoformat(start_date_str)
        # Ajoute un an. Gère les années bissextiles.
        next_date = start_date.replace(year=start_date.year + 1)
        return next_date.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        return "Format de date invalide"
