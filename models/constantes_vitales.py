from database import curseur, connection


def ajouter(patient_id, consultation_id, date_heure, taille_cm=None, poids_kg=None,
            temperature_c=None, tension_arterielle=None, frequence_cardiaque=None,
            saturation_oxygene=None):
    curseur.execute(
        """INSERT INTO constantes_vitales
           (patient_id, consultation_id, date_heure, taille_cm, poids_kg, temperature_c,
            tension_arterielle, frequence_cardiaque, saturation_oxygene)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (patient_id, consultation_id, date_heure, taille_cm, poids_kg, temperature_c,
         tension_arterielle, frequence_cardiaque, saturation_oxygene))
    connection.commit()
    return curseur.lastrowid


def charger_par_patient(patient_id, limite=20):
    curseur.execute(
        """SELECT id, date_heure, taille_cm, poids_kg, temperature_c, tension_arterielle,
                  frequence_cardiaque, saturation_oxygene
           FROM constantes_vitales WHERE patient_id=? ORDER BY date_heure DESC LIMIT ?""",
        (patient_id, limite))
    return curseur.fetchall()


def derniere_par_patient(patient_id):
    curseur.execute(
        """SELECT id, date_heure, taille_cm, poids_kg, temperature_c, tension_arterielle,
                  frequence_cardiaque, saturation_oxygene
           FROM constantes_vitales WHERE patient_id=? ORDER BY date_heure DESC LIMIT 1""",
        (patient_id,))
    return curseur.fetchone()
