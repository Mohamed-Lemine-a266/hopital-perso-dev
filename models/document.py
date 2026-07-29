from datetime import datetime
from database import curseur, connection


TYPES_DOCUMENT = ["Ordonnance", "Analyse", "Radio", "Scanner", "IRM", "Autre"]


def ajouter(patient_id, type_document, nom_fichier, chemin_fichier, ajoute_par=""):
    date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M")
    curseur.execute(
        """INSERT INTO documents (patient_id, type_document, nom_fichier, chemin_fichier, date_ajout, ajoute_par)
           VALUES (?,?,?,?,?,?)""",
        (patient_id, type_document, nom_fichier, chemin_fichier, date_ajout, ajoute_par))
    connection.commit()
    return curseur.lastrowid


def charger_par_patient(patient_id):
    curseur.execute(
        """SELECT id, type_document, nom_fichier, chemin_fichier, date_ajout, ajoute_par
           FROM documents WHERE patient_id=? ORDER BY date_ajout DESC""",
        (patient_id,))
    return curseur.fetchall()


def supprimer(doc_id):
    curseur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    connection.commit()


def obtenir_par_id(doc_id):
    curseur.execute(
        "SELECT id, patient_id, type_document, nom_fichier, chemin_fichier, date_ajout, ajoute_par "
        "FROM documents WHERE id=?", (doc_id,))
    return curseur.fetchone()
