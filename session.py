"""
Contexte de session — mémorise l'utilisateur connecté pour toute la durée
de l'exécution. Permet à n'importe quel module d'enregistrer une action
dans le journal d'audit sans avoir à faire circuler l'utilisateur partout.
"""

_utilisateur_courant = None
_permissions_courantes = set()


def definir_utilisateur(utilisateur_info, permissions):
    global _utilisateur_courant, _permissions_courantes
    _utilisateur_courant = utilisateur_info
    _permissions_courantes = permissions


def utilisateur_courant():
    return _utilisateur_courant


def utilisateur_id():
    return _utilisateur_courant["id"] if _utilisateur_courant else None


def utilisateur_nom_complet():
    if _utilisateur_courant:
        return f"{_utilisateur_courant['prenom']} {_utilisateur_courant['nom']}"
    return "Inconnu"


def medecin_id_courant():
    if _utilisateur_courant is None:
        return None
    from models import utilisateur
    return utilisateur.obtenir_medecin_id(_utilisateur_courant["id"])


def a_permission(code):
    return code in _permissions_courantes


def exiger_permission(code):
    """Vérifie une permission avant une action ; affiche un avertissement sinon.
    Renvoie True si l'action peut continuer, False sinon."""
    if code in _permissions_courantes:
        return True
    from tkinter import messagebox
    messagebox.showwarning("Action non autorisée",
        "Vous n'avez pas la permission nécessaire pour effectuer cette action.")
    return False


def permissions_courantes():
    return _permissions_courantes


def deconnecter():
    global _utilisateur_courant, _permissions_courantes
    _utilisateur_courant = None
    _permissions_courantes = set()