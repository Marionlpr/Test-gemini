# Fichier : models/tasks_hebdo/tasks_hebdo.py
# Description : Fonctions pour la gestion des tâches hebdomadaires.

import sqlite3
from models.database.database import create_connection

def get_tasks_for_day(day_name, service_id):
    """Récupère les tâches hebdomadaires pour un jour ET un service donnés."""
    conn = create_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tache_hebdomadaire, jour_semaine FROM tasks_hebdo
            WHERE jour_semaine = ? AND service_id = ?
        """, (day_name.lower(), service_id))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des tâches hebdomadaires : {e}")
        return []
    finally:
        conn.close()

def get_all_hebdo_tasks():
    """Récupère toutes les tâches hebdomadaires pour les lister."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, jour_semaine, tache_hebdomadaire FROM tasks_hebdo ORDER BY jour_semaine")
        tasks = cursor.fetchall()
        return tasks
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération de toutes les tâches hebdomadaires : {e}")
        return []
    finally:
        conn.close()

def get_task_hebdo_details(task_id):
    """Récupère les détails d'une tâche hebdomadaire spécifique."""
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks_hebdo WHERE id = ?", (task_id,))
        details = cursor.fetchone()
        return dict(details) if details else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails de la tâche hebdo : {e}")
        return None
    finally:
        conn.close()

def add_task_hebdo(data):
    """Ajoute une nouvelle tâche hebdomadaire avec un service associé."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO tasks_hebdo (jour_semaine, tache_hebdomadaire, service_id)
                 VALUES (:jour_semaine, :tache_hebdomadaire, :service_id)'''
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de la tâche hebdomadaire : {e}")
        return False
    finally:
        conn.close()

def update_task_hebdo(task_id, data):
    """Met à jour une tâche hebdomadaire."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''UPDATE tasks_hebdo SET jour_semaine = :jour_semaine, tache_hebdomadaire = :tache_hebdomadaire
                 WHERE id = :id'''
        data['id'] = task_id
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de la tâche hebdomadaire : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_task_hebdo(task_id):
    """Supprime une tâche hebdomadaire."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks_hebdo WHERE id = ?", (task_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de la tâche hebdomadaire : {e}")
        return False
    finally:
        conn.close()
