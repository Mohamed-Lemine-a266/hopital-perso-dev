"""Tests du module patient : CRUD, unicité du CNI, validation du format, recherche."""
import _env
from database import creer_tables
from models import patient

creer_tables()

# ── Création ──
pid = patient.ajouter("SN100001", "Diallo", "Fatou", "Féminin", "1990-05-15",
                      "781234567", "Dakar", "2026-07-23")
assert pid is not None, "L'ajout doit renvoyer un identifiant"
print("OK  ajout d'un patient")

# ── Unicité du CNI ──
assert patient.cni_existe("SN100001") is True
assert patient.cni_existe("INEXISTANT") is False
print("OK  détection de doublon CNI")

# ── Recherche par CNI exact ──
p = patient.rechercher_par_cni("SN100001")
assert p is not None and p[2] == "Diallo"
print("OK  recherche par CNI exact")

# ── Recherche partielle (nom, prénom, téléphone) ──
assert len(patient.rechercher("Diallo")) == 1
assert len(patient.rechercher("781234")) == 1
assert len(patient.rechercher("Fatou")) == 1
assert len(patient.rechercher("INTROUVABLE_XYZ")) == 0
print("OK  recherche multi-critères")

# ── Modification ──
patient.modifier(pid, "SN100001", "Diallo", "Fatou-Marie", "Féminin",
                 "1990-05-15", "781234567", "Nouvelle Adresse")
p2 = patient.obtenir_par_id(pid)
assert p2[3] == "Fatou-Marie" and p2[7] == "Nouvelle Adresse"
print("OK  modification")

# ── Validation du format CNI ──
assert patient.format_cni_valide("SN100001") is True
assert patient.format_cni_valide("HOP-0001") is True
assert patient.format_cni_valide("HOP-0001", "HOP") is True
assert patient.format_cni_valide("") is False
assert patient.format_cni_valide("ab") is False  # trop court
print("OK  validation du format CNI")

# ── Numéro auto-généré séquentiel ──
suivant1 = patient.prochain_numero_auto("HOP")
patient.ajouter(suivant1, "Sans", "CNI", "", "", "", "", "2026-07-23")
suivant2 = patient.prochain_numero_auto("HOP")
assert suivant1 != suivant2
print(f"OK  numérotation auto séquentielle ({suivant1} -> {suivant2})")

# ── Infos médicales (additives) ──
patient.modifier_infos_medicales(pid, "Pénicilline", "Diabète", "Aucun", "O+")
infos = patient.obtenir_infos_medicales(pid)
assert infos == ("Pénicilline", "Diabète", "Aucun", "O+")
print("OK  informations médicales")

# ── Protection contre suppression avec enregistrements liés ──
assert patient.a_des_enregistrements(pid) is False
print("OK  a_des_enregistrements (aucun enregistrement lié)")

# ── Suppression ──
patient.supprimer(pid)
assert patient.obtenir_par_id(pid) is None
print("OK  suppression")

_env.nettoyer()
print()
print("TOUS LES TESTS ONT RÉUSSI — test_patient.py")
