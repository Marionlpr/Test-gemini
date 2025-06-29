# Fichier : models/reports/reports.py
# Description : Fonctions pour la gestion des rapports.

import sqlite3
from models.database.database import create_connection
from datetime import date

def get_all_reports(young_id=None):
    """
    Récupère tous les rapports, avec des informations sur le jeune et l'auteur.
    Si young_id est fourni, filtre les rapports pour ce jeune uniquement.
    """
    conn = create_connection()
    if conn is None: return []
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = """
            SELECT
                r.id, r.type_rapport, r.date_redaction, r.statut,
                y.prenom as young_prenom, y.nom as young_nom,
                u.prenom as author_prenom, u.nom as author_nom
            FROM reports r
            JOIN youngs y ON r.young_id = y.id
            JOIN users u ON r.redacteur_id = u.id
        """
        params = []
        if young_id:
            sql += " WHERE r.young_id = ?"
            params.append(young_id)
            
        sql += " ORDER BY r.date_redaction DESC, y.nom"
        
        cursor.execute(sql, params)
        reports = [dict(row) for row in cursor.fetchall()]
        return reports
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des rapports : {e}")
        return []
    finally:
        conn.close()

def get_report_details(report_id):
    """Récupère tous les détails d'un rapport spécifique."""
    conn = create_connection()
    if conn is None: return None
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        details = cursor.fetchone()
        return dict(details) if details else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des détails du rapport : {e}")
        return None
    finally:
        conn.close()

def add_report(data):
    """Ajoute un nouveau rapport dans la base de données."""
    conn = create_connection()
    if conn is None: return None
    try:
        # On ne met pas la date de rédaction ni le validateur à l'ajout
        # La date sera ajoutée à la validation
        sql = '''INSERT INTO reports(type_rapport, young_id, redacteur_id, rappel_situation, accueil, 
                                     scolarite, soin_sante, famille, psychologique, preconisations, statut)
                 VALUES(:type_rapport, :young_id, :redacteur_id, :rappel_situation, :accueil, 
                        :scolarite, :soin_sante, :famille, :psychologique, :preconisations, 'en attente')'''
        
        cursor = conn.cursor()
        cursor.execute(sql, data)
        report_id = cursor.lastrowid
        conn.commit()
        return report_id
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du rapport : {e}")
        return None
    finally:
        conn.close()

def update_report(report_id, data):
    """Met à jour le contenu d'un rapport."""
    conn = create_connection()
    if conn is None: return False
    
    # On ne met à jour que les champs modifiables par l'éducateur
    sql = '''UPDATE reports SET type_rapport = :type_rapport, rappel_situation = :rappel_situation, accueil = :accueil,
                                scolarite = :scolarite, soin_sante = :soin_sante, famille = :famille, 
                                psychologique = :psychologique, preconisations = :preconisations
             WHERE id = :id'''
    data['id'] = report_id
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la mise à jour du rapport : {e}")
        return False
    finally:
        conn.close()

def validate_report(report_id, validator_id):
    """Valide un rapport, ajoutant la date de rédaction et l'ID du validateur."""
    conn = create_connection()
    if conn is None: return False
    
    sql = '''UPDATE reports SET statut = 'validé', 
                                validateur_id = ?,
                                date_redaction = ?
             WHERE id = ?'''
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (validator_id, date.today().isoformat(), report_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la validation du rapport : {e}")
        return False
    finally:
        conn.close()


def delete_report(report_id):
    """Supprime un rapport de la base de données."""
    conn = create_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du rapport : {e}")
        return False
    finally:
        conn.close()
