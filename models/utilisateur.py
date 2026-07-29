import bcrypt
from database import curseur, connection


def _hash(mot_de_passe):
    return bcrypt.hashpw(mot_de_passe.encode(), bcrypt.gensalt()).decode()


def _verifier_mdp(mot_de_passe, hash_stocke):
    return bcrypt.checkpw(mot_de_passe.encode(), hash_stocke.encode())


def authentifier(nom_utilisateur, mot_de_passe):
    """Retourne l'utilisateur si les identifiants sont corrects, sinon None."""
    curseur.execute("""
        SELECT utilisateurs.id, utilisateurs.nom_utilisateur, utilisateurs.nom, utilisateurs.prenom,
               utilisateurs.role_id, roles.nom, utilisateurs.actif, utilisateurs.mot_de_passe
        FROM utilisateurs JOIN roles ON utilisateurs.role_id = roles.id
        WHERE utilisateurs.nom_utilisateur=?""",
        (nom_utilisateur,))
    u = curseur.fetchone()
    if u and u[6] == 1 and _verifier_mdp(mot_de_passe, u[7]):
        return {"id": u[0], "nom_utilisateur": u[1], "nom": u[2], "prenom": u[3],
                "role_id": u[4], "role_nom": u[5]}
    return None


def obtenir_permissions(utilisateur_id, role_id):
    """Retourne l'ensemble des codes de permissions pour un utilisateur."""
    curseur.execute("""
        SELECT permissions.code FROM role_permissions
        JOIN permissions ON role_permissions.permission_id = permissions.id
        WHERE role_permissions.role_id=?""", (role_id,))
    perms = set(r[0] for r in curseur.fetchall())

    curseur.execute("""
        SELECT permissions.code, utilisateur_permissions.accorde
        FROM utilisateur_permissions
        JOIN permissions ON utilisateur_permissions.permission_id = permissions.id
        WHERE utilisateur_permissions.utilisateur_id=?""", (utilisateur_id,))
    for code, accorde in curseur.fetchall():
        if accorde:
            perms.add(code)
        else:
            perms.discard(code)
    return perms


def charger_tous():
    curseur.execute("""
        SELECT utilisateurs.id, utilisateurs.nom_utilisateur, utilisateurs.nom,
               utilisateurs.prenom, roles.nom, utilisateurs.actif
        FROM utilisateurs JOIN roles ON utilisateurs.role_id = roles.id
        ORDER BY utilisateurs.nom""")
    return curseur.fetchall()


def ajouter(nom_utilisateur, mot_de_passe, nom, prenom, role_id):
    curseur.execute(
        "INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, nom, prenom, role_id) VALUES (?,?,?,?,?)",
        (nom_utilisateur, _hash(mot_de_passe), nom, prenom, role_id))
    connection.commit()
    return curseur.lastrowid


def modifier(uid, nom_utilisateur, nom, prenom, role_id, actif):
    curseur.execute(
        "UPDATE utilisateurs SET nom_utilisateur=?, nom=?, prenom=?, role_id=?, actif=? WHERE id=?",
        (nom_utilisateur, nom, prenom, role_id, actif, uid))
    connection.commit()


def changer_mot_de_passe(uid, nouveau):
    curseur.execute("UPDATE utilisateurs SET mot_de_passe=? WHERE id=?", (_hash(nouveau), uid))
    connection.commit()


def supprimer(uid):
    curseur.execute("DELETE FROM utilisateurs WHERE id=?", (uid,))
    connection.commit()


def nom_utilisateur_existe(nom_u, exclure_id=None):
    if exclure_id:
        curseur.execute("SELECT id FROM utilisateurs WHERE nom_utilisateur=? AND id!=?", (nom_u, exclure_id))
    else:
        curseur.execute("SELECT id FROM utilisateurs WHERE nom_utilisateur=?", (nom_u,))
    return curseur.fetchone() is not None


def lier_medecin(uid, medecin_id):
    curseur.execute("UPDATE utilisateurs SET medecin_id=? WHERE id=?", (medecin_id, uid))
    connection.commit()


def obtenir_medecin_id(uid):
    curseur.execute("SELECT medecin_id FROM utilisateurs WHERE id=?", (uid,))
    r = curseur.fetchone()
    return r[0] if r and r[0] else None


def charger_roles():
    curseur.execute("SELECT id, nom, description FROM roles ORDER BY nom")
    return curseur.fetchall()


def ajouter_role(nom, description=""):
    curseur.execute("INSERT INTO roles (nom, description) VALUES (?,?)", (nom, description))
    connection.commit()
    return curseur.lastrowid


def modifier_role(rid, nom, description):
    curseur.execute("UPDATE roles SET nom=?, description=? WHERE id=?", (nom, description, rid))
    connection.commit()


def supprimer_role(rid):
    curseur.execute("SELECT COUNT(*) FROM utilisateurs WHERE role_id=?", (rid,))
    if curseur.fetchone()[0] > 0:
        return False
    curseur.execute("DELETE FROM roles WHERE id=?", (rid,))
    connection.commit()
    return True


def charger_permissions():
    curseur.execute("SELECT id, code, description FROM permissions ORDER BY code")
    return curseur.fetchall()


def permissions_du_role(role_id):
    curseur.execute("""
        SELECT permissions.id, permissions.code, permissions.description
        FROM role_permissions
        JOIN permissions ON role_permissions.permission_id = permissions.id
        WHERE role_permissions.role_id=? ORDER BY permissions.code""", (role_id,))
    return curseur.fetchall()


def definir_permissions_role(role_id, permission_ids):
    """Remplace toutes les permissions d'un rôle."""
    curseur.execute("DELETE FROM role_permissions WHERE role_id=?", (role_id,))
    for pid in permission_ids:
        curseur.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (?,?)", (role_id, pid))
    connection.commit()


def permissions_utilisateur_surcharges(uid):
    curseur.execute("""
        SELECT permissions.id, permissions.code, utilisateur_permissions.accorde
        FROM utilisateur_permissions
        JOIN permissions ON utilisateur_permissions.permission_id = permissions.id
        WHERE utilisateur_permissions.utilisateur_id=?""", (uid,))
    return curseur.fetchall()


def definir_surcharge_utilisateur(uid, permission_id, accorde):
    try:
        curseur.execute(
            "INSERT INTO utilisateur_permissions (utilisateur_id, permission_id, accorde) VALUES (?,?,?)",
            (uid, permission_id, accorde))
    except Exception:
        curseur.execute(
            "UPDATE utilisateur_permissions SET accorde=? WHERE utilisateur_id=? AND permission_id=?",
            (accorde, uid, permission_id))
    connection.commit()


def supprimer_surcharge_utilisateur(uid, permission_id):
    curseur.execute(
        "DELETE FROM utilisateur_permissions WHERE utilisateur_id=? AND permission_id=?",
        (uid, permission_id))
    connection.commit()