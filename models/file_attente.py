from datetime import date
from database import curseur, connection


def ajouter(patient_id, medecin_id, date_heure_arrivee, motif="", priorite="normale"):
    numero_ticket = _prochain_ticket()
    curseur.execute(
        """INSERT INTO file_attente (patient_id,medecin_id,date_heure_arrivee,motif,priorite,numero_ticket)
           VALUES (?,?,?,?,?,?)""",
        (patient_id, medecin_id, date_heure_arrivee, motif, priorite, numero_ticket))
    connection.commit()
    return curseur.lastrowid, numero_ticket


def _prochain_ticket():
    """Génère T001, T002, etc. Réinitialisé chaque jour."""
    aujourd_hui = date.today().isoformat()
    curseur.execute(
        "SELECT numero_ticket FROM file_attente WHERE date_heure_arrivee LIKE ? ORDER BY numero_ticket DESC LIMIT 1",
        (f"{aujourd_hui}%",))
    r = curseur.fetchone()
    if r is None or r[0] is None:
        return "T001"
    try:
        num = int(r[0][1:])
        return f"T{num + 1:03d}"
    except (ValueError, IndexError):
        return "T001"


def charger_toute(jour_seulement=True):
    """Charge la file. Par défaut, uniquement les entrées du jour."""
    filtre_jour = ""
    params = ()
    if jour_seulement:
        filtre_jour = "AND file_attente.date_heure_arrivee >= ?"
        params = (date.today().isoformat(),)
    curseur.execute(f"""
        SELECT file_attente.id, file_attente.numero_ticket,
               patients.numero_cni, patients.nom, patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               file_attente.date_heure_arrivee, file_attente.priorite,
               file_attente.statut, file_attente.motif, medecins.specialite_id
        FROM file_attente
        JOIN patients ON file_attente.patient_id = patients.id
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.statut NOT IN ('absent') {filtre_jour}
        ORDER BY
            CASE file_attente.priorite
                WHEN 'très urgente' THEN 1
                WHEN 'urgente' THEN 2
                ELSE 3
            END,
            file_attente.date_heure_arrivee""", params)
    return curseur.fetchall()


def charger_par_specialite(spec_id):
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        SELECT file_attente.id, file_attente.numero_ticket,
               patients.numero_cni, patients.nom, patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               file_attente.date_heure_arrivee, file_attente.priorite,
               file_attente.statut, file_attente.motif, medecins.specialite_id
        FROM file_attente
        JOIN patients ON file_attente.patient_id = patients.id
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE medecins.specialite_id=? AND file_attente.statut NOT IN ('absent')
              AND file_attente.date_heure_arrivee >= ?
        ORDER BY
            CASE file_attente.priorite WHEN 'très urgente' THEN 1 WHEN 'urgente' THEN 2 ELSE 3 END,
            file_attente.date_heure_arrivee""", (spec_id, aujourd_hui))
    return curseur.fetchall()


def charger_par_medecin(med_id):
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        SELECT file_attente.id, file_attente.numero_ticket,
               patients.numero_cni, patients.nom, patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               file_attente.date_heure_arrivee, file_attente.priorite,
               file_attente.statut, file_attente.motif, medecins.specialite_id
        FROM file_attente
        JOIN patients ON file_attente.patient_id = patients.id
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.medecin_id=? AND file_attente.statut NOT IN ('absent')
              AND file_attente.date_heure_arrivee >= ?
        ORDER BY
            CASE file_attente.priorite WHEN 'très urgente' THEN 1 WHEN 'urgente' THEN 2 ELSE 3 END,
            file_attente.date_heure_arrivee""", (med_id, aujourd_hui))
    return curseur.fetchall()


def appeler_suivant(medecin_id):
    """Appelle le prochain patient (par priorité puis heure) pour un médecin."""
    curseur.execute("""
        SELECT id FROM file_attente
        WHERE medecin_id=? AND statut='en attente'
        ORDER BY
            CASE priorite WHEN 'très urgente' THEN 1 WHEN 'urgente' THEN 2 ELSE 3 END,
            date_heure_arrivee
        LIMIT 1""", (medecin_id,))
    r = curseur.fetchone()
    if r is None:
        return None
    from datetime import datetime
    curseur.execute("UPDATE file_attente SET statut='appelé', date_heure_appel=? WHERE id=?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M"), r[0]))
    connection.commit()
    return r[0]


def changer_statut(file_id, nouveau_statut):
    from datetime import datetime
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M")
    if nouveau_statut == "appelé":
        curseur.execute("UPDATE file_attente SET statut=?, date_heure_appel=? WHERE id=?",
                        (nouveau_statut, maintenant, file_id))
    elif nouveau_statut == "en consultation":
        curseur.execute("UPDATE file_attente SET statut=?, date_heure_debut_consultation=? WHERE id=?",
                        (nouveau_statut, maintenant, file_id))
    elif nouveau_statut == "terminé":
        curseur.execute("UPDATE file_attente SET statut=?, date_heure_fin=? WHERE id=?",
                        (nouveau_statut, maintenant, file_id))
    elif nouveau_statut == "en attente":
        # Remise en file : nouvelle heure d'arrivée, reset timestamps
        curseur.execute(
            "UPDATE file_attente SET statut=?, date_heure_arrivee=?, date_heure_appel=NULL WHERE id=?",
            (nouveau_statut, maintenant, file_id))
    else:
        curseur.execute("UPDATE file_attente SET statut=? WHERE id=?", (nouveau_statut, file_id))
    connection.commit()


def retirer(file_id):
    curseur.execute("DELETE FROM file_attente WHERE id=?", (file_id,))
    connection.commit()


def patient_deja_en_attente(patient_id, specialite_id):
    """Vérifie si le patient est déjà en attente dans cette spécialité."""
    curseur.execute("""
        SELECT file_attente.id FROM file_attente
        JOIN medecins ON file_attente.medecin_id = medecins.id
        WHERE file_attente.patient_id=? AND medecins.specialite_id=?
              AND file_attente.statut IN ('en attente', 'appelé')
    """, (patient_id, specialite_id))
    return curseur.fetchone() is not None


def compter_en_attente_par_medecin(medecin_id):
    curseur.execute(
        "SELECT COUNT(*) FROM file_attente WHERE medecin_id=? AND statut='en attente'",
        (medecin_id,))
    return curseur.fetchone()[0]


def compter_en_attente_par_specialite():
    """Retourne le nombre de patients en attente par spécialité (pour le tableau de bord)."""
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        SELECT specialites.nom, COUNT(*)
        FROM file_attente
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.statut = 'en attente'
              AND file_attente.date_heure_arrivee >= ?
        GROUP BY specialites.nom ORDER BY specialites.nom
    """, (aujourd_hui,))
    return curseur.fetchall()


def obtenir_info(file_id):
    """Retourne les infos complètes d'une entrée de file (patient_id, medecin_id, etc.)."""
    curseur.execute("""
        SELECT file_attente.id, file_attente.patient_id, file_attente.medecin_id,
               patients.nom, patients.prenom, medecins.nom, medecins.prenom,
               specialites.nom, file_attente.motif
        FROM file_attente
        JOIN patients ON file_attente.patient_id = patients.id
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.id=?""", (file_id,))
    return curseur.fetchone()


def compter_par_statut_jour():
    """Retourne un dict {statut: nombre} pour la file du jour (tableau de bord)."""
    from datetime import date
    aujourd_hui = date.today().isoformat()
    curseur.execute(
        "SELECT statut, COUNT(*) FROM file_attente WHERE date_heure_arrivee >= ? GROUP BY statut",
        (aujourd_hui,))
    return dict(curseur.fetchall())


def derniers_appeles(limite=8):
    """Derniers tickets appelés aujourd'hui, pour l'écran public d'affichage."""
    from datetime import date
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        SELECT file_attente.numero_ticket, medecins.nom || ' ' || medecins.prenom,
               specialites.nom, file_attente.statut, file_attente.date_heure_appel
        FROM file_attente
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.date_heure_arrivee >= ? AND file_attente.date_heure_appel IS NOT NULL
        ORDER BY file_attente.date_heure_appel DESC LIMIT ?
    """, (aujourd_hui, limite))
    return curseur.fetchall()


def obtenir_statut(file_id):
    """Retourne uniquement le statut d'une entrée de file (utilitaire simple)."""
    curseur.execute("SELECT statut FROM file_attente WHERE id=?", (file_id,))
    r = curseur.fetchone()
    return r[0] if r else None
