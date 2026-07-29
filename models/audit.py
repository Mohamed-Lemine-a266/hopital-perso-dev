"""
Journal d'audit — trace qui a fait quoi et quand, avec (si fourni) l'ancienne
et la nouvelle valeur pour les modifications.
"""
from datetime import datetime
from database import curseur, connection


def enregistrer(utilisateur_id, utilisateur_nom, action, module, cible_id=None,
                 details="", ancien_valeur=None, nouvelle_valeur=None):
    curseur.execute(
        """INSERT INTO journal_audit
           (date_heure, utilisateur_id, utilisateur_nom, action, module, cible_id,
            details, ancien_valeur, nouvelle_valeur)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), utilisateur_id, utilisateur_nom,
         action, module, cible_id, details, ancien_valeur, nouvelle_valeur))
    connection.commit()


def charger_tout(limite=200):
    curseur.execute(
        "SELECT date_heure, utilisateur_nom, action, module, cible_id, details, "
        "ancien_valeur, nouvelle_valeur FROM journal_audit ORDER BY id DESC LIMIT ?", (limite,))
    return curseur.fetchall()


def charger_par_module(module, limite=200):
    curseur.execute(
        "SELECT date_heure, utilisateur_nom, action, module, cible_id, details, "
        "ancien_valeur, nouvelle_valeur FROM journal_audit WHERE module=? ORDER BY id DESC LIMIT ?",
        (module, limite))
    return curseur.fetchall()


def charger_par_utilisateur(utilisateur_id, limite=200):
    curseur.execute(
        "SELECT date_heure, utilisateur_nom, action, module, cible_id, details, "
        "ancien_valeur, nouvelle_valeur FROM journal_audit WHERE utilisateur_id=? ORDER BY id DESC LIMIT ?",
        (utilisateur_id, limite))
    return curseur.fetchall()
