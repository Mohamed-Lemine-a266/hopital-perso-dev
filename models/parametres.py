from database import curseur, connection


def obtenir(cle):
    curseur.execute("SELECT valeur FROM parametres WHERE cle=?", (cle,))
    r = curseur.fetchone()
    return r[0] if r else ""

def modifier(cle, valeur):
    curseur.execute("UPDATE parametres SET valeur=? WHERE cle=?", (valeur, cle))
    connection.commit()

def nom_hopital():
    return obtenir("nom_hopital") or "Hôpital"

def email():
    return obtenir("email_hopital")

def logo():
    return obtenir("logo_path")

def prefixe():
    return obtenir("prefixe_patient") or "HOP"

def duree_rdv():
    v = obtenir("duree_rdv_defaut")
    try:
        return int(v)
    except (ValueError, TypeError):
        return 30
