from datetime import date, timedelta
from database import curseur


def _filtre_date(jours):
    """Retourne la date de début selon le nombre de jours. None = pas de filtre."""
    if jours is None:
        return None
    if jours == 0:
        return date.today().isoformat()
    return (date.today() - timedelta(days=jours)).isoformat()


def patients_par_periode(jours=None):
    d = _filtre_date(jours)
    if d:
        curseur.execute(
            "SELECT COUNT(DISTINCT patient_id) FROM consultations WHERE date_heure >= ?", (d,))
    else:
        curseur.execute("SELECT COUNT(DISTINCT patient_id) FROM consultations")
    return curseur.fetchone()[0]


def repartition_par_specialite(jours=None):
    d = _filtre_date(jours)
    filtre = f"WHERE consultations.date_heure >= '{d}'" if d else ""
    curseur.execute(f"""
        SELECT specialites.nom, COUNT(*)
        FROM consultations
        JOIN medecins ON consultations.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        {filtre}
        GROUP BY specialites.nom ORDER BY COUNT(*) DESC""")
    return curseur.fetchall()


def temps_moyen_attente(jours=None):
    d = _filtre_date(jours)
    filtre = f"AND file_attente.date_heure_arrivee >= '{d}'" if d else ""
    curseur.execute(f"""
        SELECT specialites.nom,
               ROUND(AVG(
                   (julianday(file_attente.date_heure_appel) - julianday(file_attente.date_heure_arrivee)) * 1440
               ), 1)
        FROM file_attente
        JOIN medecins ON file_attente.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE file_attente.date_heure_appel IS NOT NULL {filtre}
        GROUP BY specialites.nom""")
    return curseur.fetchall()


def charge_par_medecin(jours=None):
    d = _filtre_date(jours)
    filtre = f"WHERE consultations.date_heure >= '{d}'" if d else ""
    curseur.execute(f"""
        SELECT medecins.nom || ' ' || medecins.prenom, COUNT(*)
        FROM consultations
        JOIN medecins ON consultations.medecin_id = medecins.id
        {filtre}
        GROUP BY consultations.medecin_id ORDER BY COUNT(*) DESC""")
    return curseur.fetchall()


def taux_rdv(jours=None):
    d = _filtre_date(jours)
    filtre = f"WHERE rendez_vous.date_heure >= '{d}'" if d else ""
    curseur.execute(f"SELECT statut, COUNT(*) FROM rendez_vous {filtre} GROUP BY statut")
    return curseur.fetchall()


def jour_plus_charge(jours=None):
    d = _filtre_date(jours)
    filtre = f"WHERE date_heure_arrivee >= '{d}'" if d else ""
    curseur.execute(f"""
        SELECT CASE CAST(strftime('%w', date_heure_arrivee) AS INTEGER)
                   WHEN 0 THEN 'Dimanche' WHEN 1 THEN 'Lundi' WHEN 2 THEN 'Mardi'
                   WHEN 3 THEN 'Mercredi' WHEN 4 THEN 'Jeudi' WHEN 5 THEN 'Vendredi'
                   WHEN 6 THEN 'Samedi' END as jour,
               COUNT(*)
        FROM file_attente {filtre} GROUP BY jour ORDER BY COUNT(*) DESC""")
    return curseur.fetchall()
