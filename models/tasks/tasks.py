# Fichier : models/tasks/tasks.py
# Description : Fonctions pour la gestion des tâches ponctuelles.

import sqlite3
from models.database.database import create_connection
from datetime import date, timedelta

def get_all_tasks_with_details(service_id=None):
    """
    Récupère toutes les tâches non réalisées.
    Si service_id est fourni, filtre pour n'inclure que les tâches assignées
    à des utilisateurs de ce service ou les tâches assignées à "Tout le monde".
    """
    conn = create_connection()
    if conn is None: return []
    
    today = date.today()
    urgent_limit_date = today + timedelta(days=3)
    
    tasks = []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = """
            SELECT id, tache_a_realiser, date_limite, user_id, statut 
            FROM tasks 
            WHERE statut != 'réalisée'
        """
        params = []
        if service_id is not None:
            sql += " AND (user_id IN (SELECT id FROM users WHERE service_id = ?) OR user_id IS NULL)"
            params.append(service_id)
        
        sql += " ORDER BY CASE WHEN statut = 'réalisée' THEN 1 ELSE 0 END, date_limite ASC"
        
        cursor.execute(sql, tuple(params))
        
        task_list = [dict(row) for row in cursor.fetchall()]

        for task in task_list:
            # ... (la logique d'enrichissement des données reste la même) ...
            if task['statut'] != 'réalisée':
                if task['date_limite']:
                    due_date = date.fromisoformat(task['date_limite'])
                    if due_date <= urgent_limit_date: task['statut'] = 'urgent'
                    else: task['statut'] = 'à faire'
                else: task['statut'] = 'à faire'
            # ... etc ...

        return tasks
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des tâches : {e}")
        return []
    finally:
        conn.close()

def get_task_details(task_id):
    conn = create_connection()
    if conn is None: return None, []
    
    details = None
    linked_youngs = []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        details_row = cursor.fetchone()
        if details_row:
            details = dict(details_row)

        cursor.execute("SELECT young_id FROM task_young_link WHERE task_id = ?", (task_id,))
        linked_youngs_rows = cursor.fetchall()
        linked_youngs = [row['young_id'] for row in linked_youngs_rows]

    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails de la tâche : {e}")
    finally:
        conn.close()
    return details, linked_youngs


def add_task(data, young_ids):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO tasks (tache_a_realiser, date_limite, user_id, statut)
                 VALUES (:tache_a_realiser, :date_limite, :user_id, 'à faire')'''
        
        cursor.execute(sql, data)
        task_id = cursor.lastrowid

        if task_id and young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO task_young_link (task_id, young_id) VALUES (?, ?)", (task_id, young_id))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de la tâche : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_task(task_id, data, young_ids):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = '''UPDATE tasks SET tache_a_realiser = :tache_a_realiser,
                                  date_limite = :date_limite,
                                  user_id = :user_id
                 WHERE id = :id'''
        data['id'] = task_id
        cursor.execute(sql, data)

        cursor.execute("DELETE FROM task_young_link WHERE task_id = ?", (task_id,))
        if young_ids:
            for young_id in young_ids:
                cursor.execute("INSERT INTO task_young_link (task_id, young_id) VALUES (?, ?)", (task_id, young_id))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de la tâche : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def mark_task_as_done(task_id):
    """Met à jour le statut d'une tâche à 'réalisée'."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET statut = 'réalisée' WHERE id = ?", (task_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour de la tâche : {e}")
        return False
    finally:
        conn.close()

def unmark_task_as_done(task_id):
    """Met à jour le statut d'une tâche de 'réalisée' à 'à faire'."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET statut = 'à faire' WHERE id = ?", (task_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'annulation de la tâche : {e}")
        return False
    finally:
        conn.close()

def delete_task(task_id):
    """Supprime une tâche de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de la tâche : {e}")
        return False
    finally:
        conn.close()
