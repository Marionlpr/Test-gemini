# Fichier : models/auth/auth.py
# Description : Gère l'authentification des utilisateurs.

import hashlib
import sqlite3
from ..database.database import create_connection

def hash_password(password):
    """
    Hache un mot de passe en utilisant l'algorithme SHA-256.
    
    Args:
        password (str): Le mot de passe en clair.
        
    Returns:
        str: Le mot de passe haché sous forme de chaîne hexadécimale.
    """
    # un "salt" est une chaîne aléatoire ajoutée au mot de passe avant le hachage
    # pour le rendre plus sécurisé. Idéalement, il devrait être unique par utilisateur
    # et stocké dans la BDD. Pour simplifier ici, nous utilisons un salt statique.
    salt = "un_salt_secret_pour_la_securite"
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode('utf-8')).hexdigest()

def check_user(identifiant, password):
    """
    Vérifie les informations d'identification d'un utilisateur.

    Args:
        identifiant (str): L'identifiant de l'utilisateur.
        password (str): Le mot de passe en clair.

    Returns:
        tuple: Un tuple contenant (user_id, niveau_authentification) si la connexion réussit,
               sinon None.
    """
    conn = create_connection()
    if conn is None:
        print("Erreur de connexion à la base de données pour l'authentification.")
        return None

    try:
        cursor = conn.cursor()
        
        # Hachage du mot de passe fourni pour le comparer à celui dans la BDD
        hashed_password = hash_password(password)

        # Récupération de l'utilisateur par son identifiant et son mot de passe haché
        cursor.execute(
            "SELECT id, niveau_authentification FROM users WHERE identifiant = ? AND mot_de_passe = ?",
            (identifiant, hashed_password)
        )
        
        user_data = cursor.fetchone() # fetchone() récupère la première ligne correspondante

        if user_data:
            print(f"Authentification réussie pour l'utilisateur ID: {user_data[0]}")
            return user_data  # Retourne (id, niveau_authentification)
        else:
            print("Échec de l'authentification : identifiant ou mot de passe incorrect.")
            return None
    except sqlite3.Error as e:
        print(f"Erreur de base de données lors de la vérification de l'utilisateur : {e}")
        return None
    finally:
        conn.close()

# --- Section pour tester et ajouter un premier utilisateur ---
def add_first_admin_user():
    """
    Ajoute un utilisateur administrateur par défaut si aucun utilisateur n'existe.
    À n'utiliser que pour l'initialisation.
    """
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            print("Aucun utilisateur trouvé. Création de l'administrateur par défaut...")
            admin_id = "admin"
            admin_pass = "admin123" # Mot de passe à changer à la première connexion
            
            hashed_pass = hash_password(admin_pass)

            cursor.execute("""
                INSERT INTO users (nom, prenom, identifiant, mot_de_passe, niveau_authentification)
                VALUES (?, ?, ?, ?, ?)
            """, ("Admin", "System", admin_id, hashed_pass, "gestion administrative"))
            
            conn.commit()
            print(f"Utilisateur admin créé avec l'identifiant '{admin_id}' et le mot de passe '{admin_pass}'.")
        else:
            print("La base de données contient déjà des utilisateurs.")

    except sqlite3.Error as e:
        print(f"Erreur lors de la création de l'utilisateur admin : {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # Cette fonction sera appelée si vous exécutez ce script directement.
    # Utile pour peupler la base de données avec un premier utilisateur pour pouvoir se connecter.
    add_first_admin_user()
