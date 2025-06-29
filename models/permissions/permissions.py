# Fichier : models/permissions/permissions.py
# Description : Fonctions pour la gestion des utilisateurs (professionnels).

import sqlite3
from models.database.database import create_connection
from models.auth.auth import hash_password

def get_all_users(service_id=None):
    """
    Récupère tous les utilisateurs de la base de données, triés par ordre alphabétique.
    Si service_id est fourni, filtre les utilisateurs pour ce service.
    """
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        sql = """
            SELECT u.id, u.nom, u.prenom, u.identifiant, u.niveau_authentification, COALESCE(s.nom_service, 'N/A') as service_name
            FROM users u
            LEFT JOIN services s ON u.service_id = s.id
        """
        params = []
        if service_id is not None:
            sql += " WHERE u.service_id = ?"
            params.append(service_id)
        
        # CORRECTION: Ajout du tri par nom puis prénom.
        sql += " ORDER BY u.nom, u.prenom"

        cursor.execute(sql, params)
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return []
    finally:
        conn.close()

def get_users_for_service(service_id):
    """Récupère les utilisateurs associés à un service spécifique."""
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, prenom, nom FROM users WHERE service_id = ? ORDER BY nom, prenom", (service_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des utilisateurs par service : {e}")
        return []
    finally:
        conn.close()

# ... (les autres fonctions du fichier ne changent pas) ...

def get_user_details(user_id):
    conn = create_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_details = cursor.fetchone()
        return user_details
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails de l'utilisateur : {e}")
        return None
    finally:
        conn.close()

def add_user(data):
    conn = create_connection()
    if conn is None: return False
    try:
        data['mot_de_passe'] = hash_password(data['mot_de_passe'])
        
        sql = '''INSERT INTO users(nom, prenom, identifiant, mot_de_passe, niveau_authentification, adresse, telephone, email, service_id)
                 VALUES(:nom, :prenom, :identifiant, :mot_de_passe, :niveau_authentification, :adresse, :telephone, :email, :service_id)'''
        
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        error_msg = str(e).lower()
        if "unique constraint failed: users.identifiant" in error_msg:
            return "identifiant_exists"
        if "unique constraint failed: users.email" in error_msg:
            return "email_exists"
        print(f"Erreur d'intégrité inattendue : {e}")
        return False
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'utilisateur : {e}")
        return False
    finally:
        conn.close()

def update_user(user_id, data):
    conn = create_connection()
    if conn is None: return False
    
    if data.get('mot_de_passe'):
        data['mot_de_passe'] = hash_password(data['mot_de_passe'])
        sql_set_parts = [f"{key} = :{key}" for key in data.keys()]
    else:
        data.pop('mot_de_passe', None) 
        sql_set_parts = [f"{key} = :{key}" for key in data.keys()]

    sql = f"UPDATE users SET {', '.join(sql_set_parts)} WHERE id = :id"
    data['id'] = user_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de l'utilisateur : {e}")
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'utilisateur : {e}")
        return False
    finally:
        conn.close()
