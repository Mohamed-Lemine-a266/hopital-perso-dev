from datetime import date
from database import curseur, connection


def ajouter(patient_id, medecin_id, date_heure, duree_minutes, motif):
    curseur.execute(
        "INSERT INTO rendez_vous (patient_id,medecin_id,date_heure,duree_minutes,motif) VALUES (?,?,?,?,?)",
        (patient_id, medecin_id, date_heure, duree_minutes, motif))
    connection.commit()
    return curseur.lastrowid


def supprimer(rid):
    curseur.execute("DELETE FROM rendez_vous WHERE id=?", (rid,))
    connection.commit()


def charger_tous():
    curseur.execute("""
        SELECT rendez_vous.id, patients.numero_cni,
               patients.nom || ' ' || patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               rendez_vous.date_heure, rendez_vous.duree_minutes,
               rendez_vous.motif, rendez_vous.statut
        FROM rendez_vous
        JOIN patients ON rendez_vous.patient_id = patients.id
        JOIN medecins ON rendez_vous.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        ORDER BY rendez_vous.date_heure DESC""")
    return curseur.fetchall()


def charger_aujourd_hui():
    aujourd_hui = date.today().isoformat()
    curseur.execute("""
        SELECT rendez_vous.id, patients.numero_cni,
               patients.nom || ' ' || patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               rendez_vous.date_heure, rendez_vous.duree_minutes,
               rendez_vous.motif, rendez_vous.statut
        FROM rendez_vous
        JOIN patients ON rendez_vous.patient_id = patients.id
        JOIN medecins ON rendez_vous.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE rendez_vous.date_heure >= ? AND rendez_vous.date_heure < date(?, '+1 day')
        ORDER BY rendez_vous.date_heure""", (aujourd_hui, aujourd_hui))
    return curseur.fetchall()


def charger_par_patient(pid):
    curseur.execute("""
        SELECT rendez_vous.id, patients.numero_cni,
               patients.nom || ' ' || patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               rendez_vous.date_heure, rendez_vous.duree_minutes,
               rendez_vous.motif, rendez_vous.statut
        FROM rendez_vous
        JOIN patients ON rendez_vous.patient_id = patients.id
        JOIN medecins ON rendez_vous.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE rendez_vous.patient_id=?
        ORDER BY rendez_vous.date_heure DESC""", (pid,))
    return curseur.fetchall()


def obtenir_par_id(rid):
    curseur.execute(
        "SELECT id, patient_id, medecin_id, date_heure, duree_minutes, motif, statut FROM rendez_vous WHERE id=?",
        (rid,))
    return curseur.fetchone()


def changer_statut(rid, statut):
    curseur.execute("UPDATE rendez_vous SET statut=? WHERE id=?", (statut, rid))
    connection.commit()


def existe_deja(patient_id, medecin_id, date_heure):
    curseur.execute(
        "SELECT id FROM rendez_vous WHERE patient_id=? AND medecin_id=? AND date_heure=? AND statut NOT IN ('annulé','terminé')",
        (patient_id, medecin_id, date_heure))
    return curseur.fetchone() is not None


def conflit_horaire(medecin_id, date_heure, duree_minutes):
    """Vérifie si un RDV chevauche le créneau proposé."""
    curseur.execute("""
        SELECT id FROM rendez_vous
        WHERE medecin_id=? AND statut NOT IN ('annulé','terminé')
        AND datetime(date_heure, '+' || duree_minutes || ' minutes') > datetime(?)
        AND datetime(date_heure) < datetime(?, '+' || ? || ' minutes')
    """, (medecin_id, date_heure, date_heure, str(duree_minutes)))
    return curseur.fetchone() is not None
