from database import curseur, connection


def ajouter(patient_id, medecin_id, date_heure, diagnostic, traitement, observations):
    curseur.execute(
        """INSERT INTO consultations (patient_id,medecin_id,date_heure,diagnostic,traitement,observations)
           VALUES (?,?,?,?,?,?)""",
        (patient_id, medecin_id, date_heure, diagnostic, traitement, observations))
    connection.commit()
    return curseur.lastrowid


def charger_par_patient(pid):
    curseur.execute("""
        SELECT consultations.id, consultations.date_heure,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               consultations.diagnostic, consultations.traitement, consultations.observations
        FROM consultations
        JOIN medecins ON consultations.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        WHERE consultations.patient_id=?
        ORDER BY consultations.date_heure DESC""", (pid,))
    return curseur.fetchall()


def charger_toutes():
    curseur.execute("""
        SELECT consultations.id, consultations.date_heure,
               patients.nom || ' ' || patients.prenom,
               medecins.nom || ' ' || medecins.prenom, specialites.nom,
               consultations.diagnostic, consultations.traitement
        FROM consultations
        JOIN patients ON consultations.patient_id = patients.id
        JOIN medecins ON consultations.medecin_id = medecins.id
        JOIN specialites ON medecins.specialite_id = specialites.id
        ORDER BY consultations.date_heure DESC""")
    return curseur.fetchall()
