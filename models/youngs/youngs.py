# Fichier : models/youngs/youngs.py
# Description : Fonctions pour la gestion des jeunes suivis.

import sqlite3
from models.database.database import create_connection

def get_all_youngs(service_id=None):
    """
    Récupère une liste simplifiée de tous les jeunes pour l'affichage,
    triée par ordre alphabétique (nom, puis prénom).
    Si service_id est fourni, filtre les résultats pour ce service.
    """
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        
        sql = """
            SELECT y.id, y.nom, y.prenom, y.date_naissance, y.statut_accueil, u.nom as referent_nom, s.nom_service
            FROM youngs y
            LEFT JOIN users u ON y.referent_id = u.id
            LEFT JOIN services s ON y.service_id = s.id
        """
        params = []
        
        if service_id is not None:
            sql += " WHERE y.service_id = ?"
            params.append(service_id)
            
        # CORRECTION: S'assurer que le tri est bien par nom puis prénom
        sql += " ORDER BY y.nom, y.prenom"
        
        cursor.execute(sql, params)
        youngs = cursor.fetchall()
        return youngs
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des jeunes : {e}")
        return []
    finally:
        conn.close()

# ... (les autres fonctions du fichier ne changent pas)

def get_young_details(young_id):
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM youngs WHERE id = ?", (young_id,))
        young_details = cursor.fetchone()
        return dict(young_details) if young_details else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du jeune : {e}")
        return None
    finally:
        conn.close()

def add_young(data):
    conn = create_connection()
    if conn is None: return False
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join([':' + key for key in data.keys()])
        sql = f'INSERT INTO youngs ({columns}) VALUES ({placeholders})'
        
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du jeune : {e}")
        return False
    finally:
        conn.close()

def update_young(young_id, data):
    conn = create_connection()
    if conn is None: return False
    
    sql_set_parts = [f"{key} = :{key}" for key in data.keys()]
    sql = f"UPDATE youngs SET {', '.join(sql_set_parts)} WHERE id = :id"
    data['id'] = young_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du jeune : {e}")
        return False
    finally:
        conn.close()

def delete_young(young_id):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM youngs WHERE id = ?", (young_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du jeune : {e}")
        return False
    finally:
        conn.close()

def get_all_referents_for_form():
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, prenom, nom FROM users ORDER BY nom, prenom")
        referents = cursor.fetchall()
        return [(ref[0], f"{ref[1]} {ref[2].upper()}") for ref in referents]
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des référents : {e}")
        return []
    finally:
        conn.close()

def get_youngs_for_professional(user_id):
    conn = create_connection()
    if conn is None:
        return {'referent_of': [], 'co_referent_of': []}
    
    results = {'referent_of': [], 'co_referent_of': []}
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT prenom, nom FROM youngs WHERE referent_id = ? ORDER BY nom, prenom", (user_id,))
        refs = cursor.fetchall()
        results['referent_of'] = [f"{row[0]} {row[1].upper()}" for row in refs]
        
        cursor.execute("SELECT prenom, nom FROM youngs WHERE co_referent_id = ? ORDER BY nom, prenom", (user_id,))
        corefs = cursor.fetchall()
        results['co_referent_of'] = [f"{row[0]} {row[1].upper()}" for row in corefs]
        
        return results
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des références du professionnel : {e}")
        return {'referent_of': [], 'co_referent_of': []}
    finally:
        conn.close()
