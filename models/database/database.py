# Fichier : models/database/database.py
# Description : Définit et initialise la base de données de l'application.

import sqlite3
from sqlite3 import Error
import os

DATABASE_NAME = "mecs_app.db"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Erreur lors de la création de la table : {e}")

def initialize_database():
    """Initialise la base de données en créant toutes les tables nécessaires si elles n'existent pas."""
    
    # --- Définition de toutes les tables ---
    sql_create_services_table = "CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, nom_service TEXT NOT NULL UNIQUE, adresse TEXT, telephone TEXT);"
    sql_create_users_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, nom TEXT NOT NULL, prenom TEXT NOT NULL, identifiant TEXT NOT NULL UNIQUE, mot_de_passe TEXT NOT NULL, niveau_authentification TEXT NOT NULL, adresse TEXT, telephone TEXT, email TEXT UNIQUE, service_id INTEGER, FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE SET NULL);"
    sql_create_youngs_table = "CREATE TABLE IF NOT EXISTS youngs (id INTEGER PRIMARY KEY, nom TEXT NOT NULL, prenom TEXT NOT NULL, date_naissance TEXT, lieu_naissance TEXT, date_entree TEXT, type_placement TEXT, type_accompagnement TEXT, statut_accueil TEXT NOT NULL, referent_id INTEGER, co_referent_id INTEGER, date_echeance_placement TEXT, date_audience TEXT, date_synthese_pec TEXT, date_echeance_cjm TEXT, date_sortie TEXT, service_id INTEGER, FOREIGN KEY (referent_id) REFERENCES users (id) ON DELETE SET NULL, FOREIGN KEY (co_referent_id) REFERENCES users (id) ON DELETE SET NULL, FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE SET NULL);"
    sql_create_young_contacts_table = "CREATE TABLE IF NOT EXISTS young_contacts (id INTEGER PRIMARY KEY, young_id INTEGER NOT NULL, nom TEXT NOT NULL, prenom TEXT NOT NULL, lien_parente TEXT, adresse TEXT, telephone TEXT, email TEXT, FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE);"
    sql_create_events_table = "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, nom_evenement TEXT NOT NULL, debut_datetime TEXT NOT NULL, fin_datetime TEXT NOT NULL, type_evenement TEXT NOT NULL, user_id INTEGER, FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL);"
    sql_create_event_young_link_table = "CREATE TABLE IF NOT EXISTS event_young_link (event_id INTEGER NOT NULL, young_id INTEGER NOT NULL, PRIMARY KEY (event_id, young_id), FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE, FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE);"
    sql_create_tasks_table = "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, tache_a_realiser TEXT NOT NULL, date_limite TEXT, statut TEXT DEFAULT 'à faire', user_id INTEGER, FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL);"
    sql_create_task_young_link_table = "CREATE TABLE IF NOT EXISTS task_young_link (task_id INTEGER NOT NULL, young_id INTEGER NOT NULL, PRIMARY KEY (task_id, young_id), FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE, FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE);"
    sql_create_tasks_hebdo_table = "CREATE TABLE IF NOT EXISTS tasks_hebdo (id INTEGER PRIMARY KEY, jour_semaine TEXT NOT NULL, tache_hebdomadaire TEXT NOT NULL, service_id INTEGER, FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE);"
    sql_create_reports_table = "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, type_rapport TEXT NOT NULL, date_redaction TEXT, young_id INTEGER NOT NULL, redacteur_id INTEGER NOT NULL, validateur_id INTEGER, rappel_situation TEXT, accueil TEXT, scolarite TEXT, soin_sante TEXT, famille TEXT, psychologique TEXT, preconisations TEXT, statut TEXT DEFAULT 'en attente', FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE, FOREIGN KEY (redacteur_id) REFERENCES users (id) ON DELETE CASCADE, FOREIGN KEY (validateur_id) REFERENCES users (id) ON DELETE SET NULL);"
    sql_create_projet_p_table = "CREATE TABLE IF NOT EXISTS projet_p (id INTEGER PRIMARY KEY, date_projet TEXT NOT NULL, young_id INTEGER NOT NULL UNIQUE, rappel_situation TEXT, attentes_jeune TEXT, attentes_famille TEXT);"
    sql_create_projet_p_objectifs_table = "CREATE TABLE IF NOT EXISTS projet_p_objectifs (id INTEGER PRIMARY KEY, projet_p_id INTEGER NOT NULL, objectif TEXT NOT NULL, categorie TEXT, evaluation TEXT, FOREIGN KEY (projet_p_id) REFERENCES projet_p (id) ON DELETE CASCADE);"
    sql_create_projet_p_moyens_table = "CREATE TABLE IF NOT EXISTS projet_p_moyens (id INTEGER PRIMARY KEY, objectif_id INTEGER NOT NULL, moyen TEXT NOT NULL, FOREIGN KEY (objectif_id) REFERENCES projet_p_objectifs (id) ON DELETE CASCADE);"
    # CORRECTION : Ajout de la colonne 'couleur'
    sql_create_transmissions_table = "CREATE TABLE IF NOT EXISTS transmissions (id INTEGER PRIMARY KEY, service_id INTEGER NOT NULL, user_id INTEGER NOT NULL, datetime_transmission TEXT NOT NULL, categorie TEXT NOT NULL, contenu TEXT NOT NULL, couleur TEXT DEFAULT 'gris', FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE);"
    sql_create_transmission_young_link_table = "CREATE TABLE IF NOT EXISTS transmission_young_link (transmission_id INTEGER NOT NULL, young_id INTEGER NOT NULL, PRIMARY KEY (transmission_id, young_id), FOREIGN KEY (transmission_id) REFERENCES transmissions (id) ON DELETE CASCADE, FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE);"
    sql_create_vehicle_table = "CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY, marque TEXT NOT NULL, modele TEXT NOT NULL, plaque_immatriculation TEXT NOT NULL UNIQUE, nombre_places INTEGER NOT NULL, puissance_fiscale INTEGER);"
    sql_create_trips_table = "CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY, date_trajet TEXT NOT NULL, heure_depart TEXT NOT NULL, heure_retour TEXT NOT NULL, motif TEXT, service_id INTEGER NOT NULL, user_id INTEGER NOT NULL, vehicle_id INTEGER NOT NULL, km_depart INTEGER NOT NULL, km_retour INTEGER NOT NULL, FOREIGN KEY (service_id) REFERENCES services (id), FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (vehicle_id) REFERENCES vehicles (id));"
    sql_create_trip_young_link_table = "CREATE TABLE IF NOT EXISTS trip_young_link (trip_id INTEGER NOT NULL, young_id INTEGER NOT NULL, PRIMARY KEY (trip_id, young_id), FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE, FOREIGN KEY (young_id) REFERENCES youngs (id) ON DELETE CASCADE);"
    sql_create_daily_presence_table = """
    CREATE TABLE IF NOT EXISTS daily_presence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        young_id INTEGER NOT NULL,
        presence_status TEXT NOT NULL, -- 'présent', 'absent', 'permis_famille', etc.
        repas_midi TEXT, -- 'normal', 'sans_porc', 'vegetarien', 'aucun'
        repas_soir TEXT,
        UNIQUE(date, young_id)
    );
    """
    
    sql_create_professional_meals_table = """
    CREATE TABLE IF NOT EXISTS professional_meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        repas_midi TEXT,
        repas_soir TEXT,
        UNIQUE(date, user_id)
    );
    """
    

    conn = create_connection()
    if conn is not None:
        create_table(conn, sql_create_services_table); create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_youngs_table); create_table(conn, sql_create_young_contacts_table)
        create_table(conn, sql_create_events_table); create_table(conn, sql_create_event_young_link_table)
        create_table(conn, sql_create_tasks_table); create_table(conn, sql_create_task_young_link_table)
        create_table(conn, sql_create_tasks_hebdo_table); create_table(conn, sql_create_reports_table)
        create_table(conn, sql_create_projet_p_table); create_table(conn, sql_create_projet_p_objectifs_table)
        create_table(conn, sql_create_projet_p_moyens_table); create_table(conn, sql_create_transmissions_table)
        create_table(conn, sql_create_transmission_young_link_table); create_table(conn, sql_create_vehicle_table)
        create_table(conn, sql_create_trips_table); create_table(conn, sql_create_trip_young_link_table)
        create_table(conn, sql_create_daily_presence_table)
        create_table(conn, sql_create_professional_meals_table)
        conn.close()
    else:
        print("Erreur ! Impossible de créer la connexion à la base de données.")
