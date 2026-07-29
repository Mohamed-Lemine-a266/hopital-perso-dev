"""Tests du système d'authentification, des rôles/permissions et du journal d'audit."""
import _env
from database import creer_tables
from models import utilisateur, audit

creer_tables()

# ── Compte administrateur par défaut ──
u = utilisateur.authentifier("admin", "admin")
assert u is not None and u["role_nom"] == "Administrateur"
print("OK  authentification du compte admin par défaut")

assert utilisateur.authentifier("admin", "mauvais_mot_de_passe") is None
print("OK  rejet d'un mot de passe incorrect")

# ── Permissions de l'administrateur (doit tout avoir) ──
perms_admin = utilisateur.obtenir_permissions(u["id"], u["role_id"])
assert "patients_gerer" in perms_admin
assert "utilisateurs_gerer" in perms_admin
assert len(perms_admin) >= 15
print(f"OK  permissions de l'administrateur ({len(perms_admin)} permissions)")

# ── Création d'un rôle personnalisé sans permission ──
role_id = utilisateur.ajouter_role("Stagiaire", "Rôle de test")
uid = utilisateur.ajouter("stagiaire1", "motdepasse", "Test", "Stagiaire", role_id)
perms_stagiaire = utilisateur.obtenir_permissions(uid, role_id)
assert len(perms_stagiaire) == 0
print("OK  un nouveau rôle démarre sans permission")

# ── Attribution de permissions au rôle ──
toutes_perms = utilisateur.charger_permissions()
perm_recherche = next(p for p in toutes_perms if p[1] == "recherche")
utilisateur.definir_permissions_role(role_id, [perm_recherche[0]])
perms_stagiaire2 = utilisateur.obtenir_permissions(uid, role_id)
assert "recherche" in perms_stagiaire2
print("OK  attribution de permission à un rôle personnalisé")

# ── Surcharge individuelle : retirer une permission héritée du rôle ──
utilisateur.definir_surcharge_utilisateur(uid, perm_recherche[0], accorde=0)
perms_stagiaire3 = utilisateur.obtenir_permissions(uid, role_id)
assert "recherche" not in perms_stagiaire3
print("OK  surcharge individuelle (retrait d'une permission héritée)")

# ── Surcharge individuelle : accorder une permission hors du rôle ──
perm_stats = next(p for p in toutes_perms if p[1] == "statistiques")
utilisateur.definir_surcharge_utilisateur(uid, perm_stats[0], accorde=1)
perms_stagiaire4 = utilisateur.obtenir_permissions(uid, role_id)
assert "statistiques" in perms_stagiaire4
print("OK  surcharge individuelle (ajout d'une permission hors rôle)")

# ── Unicité du nom d'utilisateur ──
assert utilisateur.nom_utilisateur_existe("admin") is True
assert utilisateur.nom_utilisateur_existe("admin", exclure_id=u["id"]) is False
print("OK  détection de doublon d'identifiant")

# ── Journal d'audit : enregistrement simple (rétrocompatible) ──
audit.enregistrer(u["id"], "Admin Test", "création", "patients", 1, "Patient de test")
journal = audit.charger_tout()
assert len(journal) == 1
assert journal[0][2] == "création"
print("OK  enregistrement d'audit simple")

# ── Journal d'audit avec ancienne/nouvelle valeur ──
audit.enregistrer(u["id"], "Admin Test", "modification", "patients", 1,
                   "Téléphone modifié", ancien_valeur="700000000", nouvelle_valeur="770000000")
journal2 = audit.charger_tout()
assert journal2[0][6] == "700000000" and journal2[0][7] == "770000000"
print("OK  enregistrement d'audit avec ancienne/nouvelle valeur")

# ── Filtrage du journal par module ──
audit.enregistrer(u["id"], "Admin Test", "création", "medecins", 1, "Médecin de test")
journal_patients = audit.charger_par_module("patients")
assert all(a[3] == "patients" for a in journal_patients)
assert len(journal_patients) == 2
print("OK  filtrage du journal par module")

_env.nettoyer()
print()
print("TOUS LES TESTS ONT RÉUSSI — test_audit_permissions.py")
