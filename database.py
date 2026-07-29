import sqlite3
from datetime import datetime, date
from config import DB_NAME, SPECIALITES_DEFAUT, PARAMS_DEFAUT, JOURS_TRAVAIL_DEFAUT

connection = sqlite3.connect(DB_NAME)
connection.execute("PRAGMA foreign_keys = ON")
curseur = connection.cursor()


def creer_tables():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS parametres (
            cle TEXT PRIMARY KEY,
            valeur TEXT
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS specialites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS medecins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT,
            specialite_id INTEGER NOT NULL,
            jours_travail TEXT NOT NULL DEFAULT '{}',
            heure_debut TEXT NOT NULL DEFAULT '08:00',
            heure_fin TEXT NOT NULL DEFAULT '17:00',
            statut TEXT NOT NULL DEFAULT 'présent',
            FOREIGN KEY (specialite_id) REFERENCES specialites(id)
        )""".format(JOURS_TRAVAIL_DEFAUT))

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cni TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            sexe TEXT,
            date_naissance TEXT,
            telephone TEXT,
            adresse TEXT,
            date_inscription TEXT NOT NULL
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS file_attente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medecin_id INTEGER NOT NULL,
            date_heure_arrivee TEXT NOT NULL,
            motif TEXT,
            priorite TEXT NOT NULL DEFAULT 'normale',
            numero_ticket TEXT,
            statut TEXT NOT NULL DEFAULT 'en attente',
            date_heure_appel TEXT,
            date_heure_debut_consultation TEXT,
            date_heure_fin TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (medecin_id) REFERENCES medecins(id)
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS rendez_vous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medecin_id INTEGER NOT NULL,
            date_heure TEXT NOT NULL,
            duree_minutes INTEGER NOT NULL DEFAULT 30,
            motif TEXT,
            statut TEXT NOT NULL DEFAULT 'planifié',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (medecin_id) REFERENCES medecins(id)
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medecin_id INTEGER NOT NULL,
            date_heure TEXT NOT NULL,
            diagnostic TEXT,
            traitement TEXT,
            observations TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (medecin_id) REFERENCES medecins(id)
        )""")

    connection.commit()
    _init_defaut()
    _migrer_colonnes_patients()
    creer_table_constantes_vitales()
    creer_table_documents()
    creer_table_absences()
    creer_tables_auth()
    creer_table_audit()
    reinitialiser_file_quotidienne()


def _init_defaut():
    for nom in SPECIALITES_DEFAUT:
        try:
            curseur.execute("INSERT INTO specialites (nom) VALUES (?)", (nom,))
        except sqlite3.IntegrityError:
            pass
    for cle, val in PARAMS_DEFAUT.items():
        try:
            curseur.execute("INSERT INTO parametres (cle, valeur) VALUES (?, ?)", (cle, val))
        except sqlite3.IntegrityError:
            pass
    connection.commit()


def _migrer_colonnes_patients():
    """Ajoute les colonnes médicales si elles n'existent pas déjà (idempotent)."""
    colonnes = [
        ("allergies", "TEXT"),
        ("antecedents_medicaux", "TEXT"),
        ("antecedents_chirurgicaux", "TEXT"),
        ("groupe_sanguin", "TEXT"),
    ]
    for nom, type_sql in colonnes:
        try:
            curseur.execute(f"ALTER TABLE patients ADD COLUMN {nom} {type_sql}")
        except sqlite3.OperationalError:
            pass
    connection.commit()


def creer_table_constantes_vitales():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS constantes_vitales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            consultation_id INTEGER,
            date_heure TEXT NOT NULL,
            taille_cm REAL,
            poids_kg REAL,
            temperature_c REAL,
            tension_arterielle TEXT,
            frequence_cardiaque INTEGER,
            saturation_oxygene INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (consultation_id) REFERENCES consultations(id)
        )""")
    connection.commit()


def creer_table_documents():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            type_document TEXT NOT NULL,
            nom_fichier TEXT NOT NULL,
            chemin_fichier TEXT NOT NULL,
            date_ajout TEXT NOT NULL,
            ajoute_par TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )""")
    connection.commit()


def creer_table_absences():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS absences_medecin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medecin_id INTEGER NOT NULL,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            motif TEXT,
            FOREIGN KEY (medecin_id) REFERENCES medecins(id)
        )""")
    connection.commit()


def creer_table_audit():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS journal_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure TEXT NOT NULL,
            utilisateur_id INTEGER,
            utilisateur_nom TEXT,
            action TEXT NOT NULL,
            module TEXT NOT NULL,
            cible_id INTEGER,
            details TEXT,
            ancien_valeur TEXT,
            nouvelle_valeur TEXT
        )""")
    connection.commit()
    for nom in ("ancien_valeur", "nouvelle_valeur"):
        try:
            curseur.execute(f"ALTER TABLE journal_audit ADD COLUMN {nom} TEXT")
        except sqlite3.OperationalError:
            pass
    connection.commit()


def reinitialiser_file_quotidienne():
    """Marque comme 'absent' les entrées non terminées des jours précédents."""
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        UPDATE file_attente SET statut = 'absent'
        WHERE date_heure_arrivee < ? AND statut NOT IN ('terminé', 'absent')
    """, (aujourd_hui,))
    connection.commit()


# ──────────────────────────────────────────────
# Tables utilisateurs / rôles / permissions
# ──────────────────────────────────────────────

def creer_tables_auth():
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            description TEXT
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            actif INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )""")

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateur_permissions (
            utilisateur_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            accorde INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (utilisateur_id, permission_id),
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )""")

    connection.commit()
    _migrer_lien_medecin()
    _init_permissions_defaut()


def _migrer_lien_medecin():
    """Relie un compte utilisateur à sa fiche médecin (permissions par propriétaire)."""
    try:
        curseur.execute("ALTER TABLE utilisateurs ADD COLUMN medecin_id INTEGER")
    except sqlite3.OperationalError:
        pass
    connection.commit()


PERMISSIONS_DEFAUT = [
    ("accueil", "Voir le tableau de bord"),
    ("accueil_patient", "Accueil et orientation des patients"),
    ("patients_voir", "Consulter la liste des patients"),
    ("patients_gerer", "Ajouter, modifier, supprimer des patients"),
    ("medecins_voir", "Consulter la liste des médecins"),
    ("medecins_gerer", "Ajouter, modifier, supprimer des médecins"),
    ("file_attente_voir", "Consulter la file d'attente"),
    ("file_attente_gerer", "Gérer la file d'attente (appeler, retirer)"),
    ("rdv_voir", "Consulter les rendez-vous"),
    ("rdv_gerer", "Planifier, modifier, annuler des rendez-vous"),
    ("consultations_voir", "Consulter l'historique médical"),
    ("consultations_gerer", "Enregistrer des consultations"),
    ("recherche", "Rechercher des patients"),
    ("statistiques", "Consulter les statistiques"),
    ("parametres", "Modifier les paramètres de l'application"),
    ("utilisateurs_gerer", "Gérer les utilisateurs, rôles et permissions"),
    ("audit_voir", "Consulter le journal des actions"),
    ("documents_voir", "Consulter les documents des patients"),
    ("documents_gerer", "Ajouter ou supprimer des documents patients"),
    ("specialites_gerer", "Gérer les spécialités de l'établissement"),
]

ROLES_DEFAUT = {
    "Administrateur": [p[0] for p in PERMISSIONS_DEFAUT],
    "Secrétaire": ["accueil", "accueil_patient", "patients_voir", "patients_gerer",
                   "file_attente_voir", "file_attente_gerer", "rdv_voir", "rdv_gerer", "recherche",
                   "documents_voir", "documents_gerer"],
    "Médecin": ["accueil", "file_attente_voir", "rdv_voir", "consultations_voir",
                "consultations_gerer", "recherche", "documents_voir", "documents_gerer"],
    "Directeur": ["accueil", "patients_voir", "medecins_voir", "file_attente_voir",
                  "rdv_voir", "consultations_voir", "recherche", "statistiques", "documents_voir"],
}


def _init_permissions_defaut():
    import bcrypt
    for code, desc in PERMISSIONS_DEFAUT:
        try:
            curseur.execute("INSERT INTO permissions (code, description) VALUES (?,?)", (code, desc))
        except sqlite3.IntegrityError:
            pass

    for nom_role, perms in ROLES_DEFAUT.items():
        try:
            curseur.execute("INSERT INTO roles (nom, description) VALUES (?,?)",
                            (nom_role, f"Rôle {nom_role}"))
        except sqlite3.IntegrityError:
            pass
        curseur.execute("SELECT id FROM roles WHERE nom=?", (nom_role,))
        role_id = curseur.fetchone()[0]
        for code_perm in perms:
            curseur.execute("SELECT id FROM permissions WHERE code=?", (code_perm,))
            perm = curseur.fetchone()
            if perm:
                try:
                    curseur.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (?,?)",
                                    (role_id, perm[0]))
                except sqlite3.IntegrityError:
                    pass

    curseur.execute("SELECT id FROM utilisateurs WHERE nom_utilisateur='admin'")
    if curseur.fetchone() is None:
        curseur.execute("SELECT id FROM roles WHERE nom='Administrateur'")
        admin_role = curseur.fetchone()
        if admin_role:
            mdp_hash = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            curseur.execute(
                "INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, nom, prenom, role_id) VALUES (?,?,?,?,?)",
                ("admin", mdp_hash, "Administrateur", "Système", admin_role[0]))

    connection.commit()