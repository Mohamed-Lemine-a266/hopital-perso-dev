from database import curseur

def charger_toutes():
    curseur.execute("SELECT id, nom FROM specialites ORDER BY nom")
    return curseur.fetchall()

def obtenir_par_id(sid):
    curseur.execute("SELECT id, nom FROM specialites WHERE id=?", (sid,))
    return curseur.fetchone()


def ajouter(nom):
    from database import connection
    curseur.execute("INSERT INTO specialites (nom) VALUES (?)", (nom,))
    connection.commit()
    return curseur.lastrowid


def modifier(sid, nom):
    from database import connection
    curseur.execute("UPDATE specialites SET nom=? WHERE id=?", (nom, sid))
    connection.commit()


def supprimer(sid):
    from database import connection
    curseur.execute("DELETE FROM specialites WHERE id=?", (sid,))
    connection.commit()


def nom_existe(nom, exclure_id=None):
    if exclure_id:
        curseur.execute("SELECT id FROM specialites WHERE nom=? AND id!=?", (nom, exclure_id))
    else:
        curseur.execute("SELECT id FROM specialites WHERE nom=?", (nom,))
    return curseur.fetchone() is not None


def a_des_medecins(sid):
    curseur.execute("SELECT COUNT(*) FROM medecins WHERE specialite_id=?", (sid,))
    return curseur.fetchone()[0] > 0
