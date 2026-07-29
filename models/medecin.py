from database import curseur, connection


def ajouter(nom, prenom, telephone, specialite_id, jours_travail, heure_debut, heure_fin):
    curseur.execute(
        """INSERT INTO medecins (nom,prenom,telephone,specialite_id,jours_travail,heure_debut,heure_fin)
           VALUES (?,?,?,?,?,?,?)""",
        (nom, prenom, telephone, specialite_id, jours_travail, heure_debut, heure_fin))
    connection.commit()
    return curseur.lastrowid


def modifier(mid, nom, prenom, telephone, specialite_id, jours_travail, heure_debut, heure_fin, statut):
    curseur.execute(
        """UPDATE medecins SET nom=?,prenom=?,telephone=?,specialite_id=?,
           jours_travail=?,heure_debut=?,heure_fin=?,statut=? WHERE id=?""",
        (nom, prenom, telephone, specialite_id, jours_travail, heure_debut, heure_fin, statut, mid))
    connection.commit()


def supprimer(mid):
    curseur.execute("DELETE FROM medecins WHERE id=?", (mid,))
    connection.commit()


def charger_tous():
    curseur.execute("""
        SELECT medecins.id, medecins.nom, medecins.prenom, medecins.telephone,
               specialites.nom, medecins.jours_travail, medecins.heure_debut,
               medecins.heure_fin, medecins.statut, medecins.specialite_id
        FROM medecins JOIN specialites ON medecins.specialite_id = specialites.id
        ORDER BY specialites.nom, medecins.nom""")
    return curseur.fetchall()


def charger_par_specialite(spec_id):
    curseur.execute("""
        SELECT medecins.id, medecins.nom, medecins.prenom, medecins.telephone,
               specialites.nom, medecins.jours_travail, medecins.heure_debut,
               medecins.heure_fin, medecins.statut, medecins.specialite_id
        FROM medecins JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE medecins.specialite_id=? ORDER BY medecins.nom""", (spec_id,))
    return curseur.fetchall()


def charger_disponibles_par_specialite(spec_id):
    """Médecins présents dans une spécialité."""
    curseur.execute("""
        SELECT medecins.id, medecins.nom, medecins.prenom, medecins.telephone,
               specialites.nom, medecins.jours_travail, medecins.heure_debut,
               medecins.heure_fin, medecins.statut, medecins.specialite_id
        FROM medecins JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE medecins.specialite_id=? AND medecins.statut='présent'
        ORDER BY medecins.nom""", (spec_id,))
    return curseur.fetchall()


def obtenir_par_id(mid):
    curseur.execute("""
        SELECT medecins.id, medecins.nom, medecins.prenom, medecins.telephone,
               medecins.specialite_id, specialites.nom, medecins.jours_travail,
               medecins.heure_debut, medecins.heure_fin, medecins.statut
        FROM medecins JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE medecins.id=?""", (mid,))
    return curseur.fetchone()


def existe_deja(nom, prenom, spec_id, exclure_id=None):
    if exclure_id:
        curseur.execute("SELECT id FROM medecins WHERE nom=? AND prenom=? AND specialite_id=? AND id!=?",
                        (nom, prenom, spec_id, exclure_id))
    else:
        curseur.execute("SELECT id FROM medecins WHERE nom=? AND prenom=? AND specialite_id=?",
                        (nom, prenom, spec_id))
    return curseur.fetchone() is not None


def a_des_enregistrements(mid):
    for t in ["file_attente", "rendez_vous", "consultations"]:
        curseur.execute(f"SELECT COUNT(*) FROM {t} WHERE medecin_id=?", (mid,))
        if curseur.fetchone()[0] > 0:
            return True
    return False


def reorienter_patients(ancien_mid, nouveau_mid):
    """Réoriente les patients en attente d'un médecin vers un autre."""
    curseur.execute(
        "UPDATE file_attente SET medecin_id=? WHERE medecin_id=? AND statut='en attente'",
        (nouveau_mid, ancien_mid))
    connection.commit()
    return curseur.rowcount


def compter_par_statut():
    """Retourne un dict {statut: nombre} pour le tableau de bord."""
    curseur.execute("SELECT statut, COUNT(*) FROM medecins GROUP BY statut")
    return dict(curseur.fetchall())
