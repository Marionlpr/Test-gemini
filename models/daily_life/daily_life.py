# Fichier : models/daily_life/daily_life.py
# Description : Fonctions pour la gestion de la présence et des repas.

import sqlite3
from models.database.database import create_connection
from datetime import timedelta

def get_meal_counts_for_date(date_str, service_id=None):
    """Calcule et retourne le nombre total de repas pour une date donnée."""
    conn = create_connection()
    if conn is None: return {}
    
    counts = {
        'jeunes': {'midi': {}, 'soir': {}},
        'pros': {'midi': {}, 'soir': {}}
    }
    meal_types = ['normal', 'sans_porc', 'vegetarien', 'total']
    for category in counts:
        for moment in counts[category]:
            for m_type in meal_types: counts[category][moment][m_type] = 0

    try:
        cursor = conn.cursor()
        
        # CORRECTION: La logique de comptage est plus robuste.
        # Repas des jeunes
        sql_jeunes = "SELECT dp.repas_midi, dp.repas_soir FROM daily_presence dp JOIN youngs y ON dp.young_id = y.id WHERE dp.date = ?"
        params_jeunes = [date_str]
        if service_id:
            sql_jeunes += " AND y.service_id = ?"
            params_jeunes.append(service_id)
        cursor.execute(sql_jeunes, params_jeunes)
        for repas_midi, repas_soir in cursor.fetchall():
            if repas_midi and repas_midi != 'aucun':
                counts['jeunes']['midi'][repas_midi] = counts['jeunes']['midi'].get(repas_midi, 0) + 1
                counts['jeunes']['midi']['total'] += 1
            if repas_soir and repas_soir != 'aucun':
                counts['jeunes']['soir'][repas_soir] = counts['jeunes']['soir'].get(repas_soir, 0) + 1
                counts['jeunes']['soir']['total'] += 1
                
        # Repas des professionnels
        sql_pros = "SELECT pm.repas_midi, pm.repas_soir FROM professional_meals pm JOIN users u ON pm.user_id = u.id WHERE pm.date = ?"
        params_pros = [date_str]
        if service_id:
            sql_pros += " AND u.service_id = ?"
            params_pros.append(service_id)
        cursor.execute(sql_pros, params_pros)
        for repas_midi, repas_soir in cursor.fetchall():
            if repas_midi and repas_midi != 'aucun':
                counts['pros']['midi'][repas_midi] = counts['pros']['midi'].get(repas_midi, 0) + 1
                counts['pros']['midi']['total'] += 1
            if repas_soir and repas_soir != 'aucun':
                counts['pros']['soir'][repas_soir] = counts['pros']['soir'].get(repas_soir, 0) + 1
                counts['pros']['soir']['total'] += 1
        
        return counts
    except sqlite3.Error as e:
        print(f"Erreur lors du calcul des effectifs repas : {e}")
        return {}
    finally:
        conn.close()

def get_presence_for_date(date_str, service_id=None):
    """
    Récupère les infos de présence pour les jeunes. Filtre par service si un ID est fourni.
    """
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT id, prenom, nom FROM youngs WHERE statut_accueil != 'sorti'"
        params = []
        if service_id:
            sql += " AND service_id = ?"
            params.append(service_id)
        sql += " ORDER BY nom, prenom"
        
        cursor.execute(sql, params)
        all_youngs = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM daily_presence WHERE date = ?", (date_str,))
        presence_data = {row['young_id']: dict(row) for row in cursor.fetchall()}
        
        full_day_data = []
        for young in all_youngs:
            y_id = young['id']
            data = { "young_id": y_id, "prenom": young['prenom'], "nom": young['nom'],
                     "presence_status": presence_data.get(y_id, {}).get('presence_status', 'Présent (journée)'),
                     "repas_midi": presence_data.get(y_id, {}).get('repas_midi', 'normal'),
                     "repas_soir": presence_data.get(y_id, {}).get('repas_soir', 'normal')}
            full_day_data.append(data)
        return full_day_data
    finally:
        conn.close()

def save_day_presence(date_str, presence_list):
    """Sauvegarde toutes les informations de présence et de repas pour une journée."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = "INSERT OR REPLACE INTO daily_presence (date, young_id, presence_status, repas_midi, repas_soir) VALUES (?, ?, ?, ?, ?)"
        data_to_save = [(date_str, item['young_id'], item['presence_status'], item['repas_midi'], item['repas_soir']) for item in presence_list]
        cursor.executemany(sql, data_to_save)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la sauvegarde de la présence : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_meal_counts_for_date(date_str, service_id=None):
    """Calcule et retourne le nombre total de repas pour une date donnée."""
    conn = create_connection()
    if conn is None: return {}
    
    counts = {'jeunes': {'midi': {}, 'soir': {}}, 'pros': {'midi': {}, 'soir': {}}}
    meal_types = ['normal', 'sans_porc', 'vegetarien', 'total']
    for category in counts:
        for moment in counts[category]:
            for m_type in meal_types: counts[category][moment][m_type] = 0

    try:
        cursor = conn.cursor()
        
        # CORRECTION : La logique est plus directe et ne se base plus sur le statut de présence.
        # Repas des jeunes
        sql_jeunes = "SELECT dp.repas_midi, dp.repas_soir FROM daily_presence dp JOIN youngs y ON dp.young_id = y.id WHERE dp.date = ?"
        params_jeunes = [date_str]
        if service_id:
            sql_jeunes += " AND y.service_id = ?"
            params_jeunes.append(service_id)
        cursor.execute(sql_jeunes, params_jeunes)
        
        for repas_midi, repas_soir in cursor.fetchall():
            if repas_midi and repas_midi != 'aucun':
                counts['jeunes']['midi'][repas_midi] = counts['jeunes']['midi'].get(repas_midi, 0) + 1
                counts['jeunes']['midi']['total'] += 1
            if repas_soir and repas_soir != 'aucun':
                counts['jeunes']['soir'][repas_soir] = counts['jeunes']['soir'].get(repas_soir, 0) + 1
                counts['jeunes']['soir']['total'] += 1
                
        # Repas des professionnels
        sql_pros = "SELECT pm.repas_midi, pm.repas_soir FROM professional_meals pm JOIN users u ON pm.user_id = u.id WHERE pm.date = ?"
        params_pros = [date_str]
        if service_id:
            sql_pros += " AND u.service_id = ?"
            params_pros.append(service_id)
        cursor.execute(sql_pros, params_pros)
        
        for repas_midi, repas_soir in cursor.fetchall():
            if repas_midi and repas_midi != 'aucun':
                counts['pros']['midi'][repas_midi] = counts['pros']['midi'].get(repas_midi, 0) + 1
                counts['pros']['midi']['total'] += 1
            if repas_soir and repas_soir != 'aucun':
                counts['pros']['soir'][repas_soir] = counts['pros']['soir'].get(repas_soir, 0) + 1
                counts['pros']['soir']['total'] += 1
        
        return counts
    finally:
        conn.close()
        
def get_presence_summary(start_date, end_date, service_id=None):
    """Calcule la synthèse des présences. Filtre par service si un ID est fourni."""
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql_youngs = "SELECT id, prenom, nom FROM youngs WHERE statut_accueil != 'sorti'"
        params_youngs = []
        if service_id:
            sql_youngs += " AND service_id = ?"
            params_youngs.append(service_id)
        cursor.execute(sql_youngs, params_youngs)
        all_youngs = {row['id']: f"{row['prenom']} {row['nom'].upper()}" for row in cursor.fetchall()}
        
        sql_summary = """
            SELECT dp.young_id, CASE WHEN dp.presence_status LIKE 'Présent%' THEN 'Présent' ELSE dp.presence_status END as simplified_status, COUNT(*) as count 
            FROM daily_presence dp JOIN youngs y ON dp.young_id = y.id
            WHERE dp.date BETWEEN ? AND ?
        """
        params_summary = [start_date, end_date]
        if service_id:
            sql_summary += " AND y.service_id = ?"
            params_summary.append(service_id)
        sql_summary += " GROUP BY dp.young_id, simplified_status"
        
        cursor.execute(sql_summary, params_summary)
        
        summary_data = {y_id: {'name': name} for y_id, name in all_youngs.items()}
        for row in cursor.fetchall():
            y_id = row['young_id']
            if y_id in summary_data:
                summary_data[y_id][row['simplified_status']] = row['count']
        return list(summary_data.values())
    finally:
        conn.close()

# ... (les autres fonctions restent les mêmes) ...

def save_professional_meals(date_str, meals_list):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = "INSERT OR REPLACE INTO professional_meals (date, user_id, repas_midi, repas_soir) VALUES (?, ?, ?, ?)"
        data_to_save = [(date_str, item['user_id'], item['repas_midi'], item['repas_soir']) for item in meals_list]
        cursor.executemany(sql, data_to_save)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la sauvegarde des repas pro : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_presence_summary(start_date, end_date, service_id=None):
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql_youngs = "SELECT id, prenom, nom FROM youngs WHERE statut_accueil != 'sorti'"
        params_youngs = []
        if service_id:
            sql_youngs += " AND service_id = ?"
            params_youngs.append(service_id)
        cursor.execute(sql_youngs, params_youngs)
        all_youngs = {row['id']: f"{row['prenom']} {row['nom'].upper()}" for row in cursor.fetchall()}
        
        sql_summary = "SELECT young_id, CASE WHEN presence_status LIKE 'Présent%' THEN 'Présent' ELSE presence_status END as simplified_status, COUNT(*) as count FROM daily_presence WHERE date BETWEEN ? AND ? GROUP BY young_id, simplified_status"
        params_summary = [start_date, end_date]
        if service_id:
            sql_summary = "SELECT dp.young_id, CASE WHEN dp.presence_status LIKE 'Présent%' THEN 'Présent' ELSE dp.presence_status END as simplified_status, COUNT(*) as count FROM daily_presence dp JOIN youngs y ON dp.young_id = y.id WHERE dp.date BETWEEN ? AND ? AND y.service_id = ? GROUP BY dp.young_id, simplified_status"
            params_summary.append(service_id)
        
        cursor.execute(sql_summary, params_summary)
        summary_data = {y_id: {'name': name} for y_id, name in all_youngs.items()}
        for row in cursor.fetchall():
            y_id = row['young_id']
            if y_id in summary_data:
                summary_data[y_id][row['simplified_status']] = row['count']
        return list(summary_data.values())
    finally:
        conn.close()


def save_day_presence(date_str, presence_list):
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        sql = "INSERT OR REPLACE INTO daily_presence (date, young_id, presence_status, repas_midi, repas_soir) VALUES (?, ?, ?, ?, ?)"
        data_to_save = []
        for item in presence_list:
            data_to_save.append((date_str, item['young_id'], item['presence_status'], item['repas_midi'], item['repas_soir']))
        cursor.executemany(sql, data_to_save)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la sauvegarde de la présence : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_weekly_meal_summary(start_date, end_date):
    summary = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        daily_counts = get_meal_counts_for_date(date_str)
        summary[date_str] = daily_counts
        current_date += timedelta(days=1)
    return summary

