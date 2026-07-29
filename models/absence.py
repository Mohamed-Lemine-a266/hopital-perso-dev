from datetime import date as _date
from database import curseur, connection


def ajouter(medecin_id, date_debut, date_fin, motif=""):
    curseur.execute(
        "INSERT INTO absences_medecin (medecin_id, date_debut, date_fin, motif) VALUES (?,?,?,?)",
        (medecin_id, date_debut, date_fin, motif))
    connection.commit()
    return curseur.lastrowid


def charger_par_medecin(medecin_id):
    curseur.execute(
        "SELECT id, date_debut, date_fin, motif FROM absences_medecin WHERE medecin_id=? ORDER BY date_debut DESC",
        (medecin_id,))
    return curseur.fetchall()


def supprimer(absence_id):
    curseur.execute("DELETE FROM absences_medecin WHERE id=?", (absence_id,))
    connection.commit()


def est_absent_a_la_date(medecin_id, date_str):
    """date_str au format AAAA-MM-JJ. Vérifie si le médecin a une absence planifiée ce jour-là."""
    curseur.execute(
        "SELECT id FROM absences_medecin WHERE medecin_id=? AND date_debut<=? AND date_fin>=?",
        (medecin_id, date_str, date_str))
    return curseur.fetchone() is not None


def est_absent_aujourd_hui(medecin_id):
    return est_absent_a_la_date(medecin_id, _date.today().isoformat())
