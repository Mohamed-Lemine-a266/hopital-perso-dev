"""Tests de la file d'attente : tickets, priorités, machine à états, doublons."""
import _env
from datetime import datetime
from database import creer_tables
from models import patient, medecin, specialite, file_attente

creer_tables()
specs = specialite.charger_toutes()
spec_id = specs[0][0]

p1 = patient.ajouter("SN200001", "Ndiaye", "Moussa", "Masculin", "1985-01-01", "770000001", "Thiès", "2026-07-23")
p2 = patient.ajouter("SN200002", "Sarr", "Aida", "Féminin", "1992-02-02", "770000002", "Dakar", "2026-07-23")
p3 = patient.ajouter("SN200003", "Fall", "Omar", "Masculin", "1978-03-03", "770000003", "Kaolack", "2026-07-23")
m1 = medecin.ajouter("Sow", "Amadou", "760000001", spec_id, "Lun,Mar,Mer,Jeu,Ven", "08:00", "17:00")

now = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Tickets séquentiels ──
fid1, t1 = file_attente.ajouter(p1, m1, now, "Consultation normale", "normale")
fid2, t2 = file_attente.ajouter(p2, m1, now, "Urgence", "urgente")
assert t1 == "T001" and t2 == "T002"
print(f"OK  tickets séquentiels ({t1}, {t2})")

# ── Doublon patient+spécialité ──
assert file_attente.patient_deja_en_attente(p1, spec_id) is True
assert file_attente.patient_deja_en_attente(p3, spec_id) is False
print("OK  détection de doublon par spécialité")

# ── Priorité : le patient urgent (p2) doit être appelé avant le normal (p1) ──
fid_appele = file_attente.appeler_suivant(m1)
info = file_attente.obtenir_info(fid_appele)
assert info[1] == p2, "Le patient urgent doit être appelé en premier malgré son arrivée après"
print("OK  tri par priorité (urgent avant normal)")

# ── Machine à états : appelé -> en consultation -> terminé ──
file_attente.changer_statut(fid_appele, "en consultation")
assert file_attente.obtenir_statut(fid_appele) == "en consultation"
file_attente.changer_statut(fid_appele, "terminé")
assert file_attente.obtenir_statut(fid_appele) == "terminé"
print("OK  machine à états (appelé -> en consultation -> terminé)")

# ── Patient absent : retour à 'en attente' ──
fid3, t3 = file_attente.ajouter(p3, m1, now, "Test absent", "normale")
file_attente.changer_statut(fid3, "appelé")
file_attente.changer_statut(fid3, "en attente")
assert file_attente.obtenir_statut(fid3) == "en attente"
print("OK  retour en file après absence")

# ── Comptages ──
compte_spec = file_attente.compter_en_attente_par_specialite()
assert any(spec == specs[0][1] for spec, _ in compte_spec)
print("OK  comptage par spécialité")

compte_statut = file_attente.compter_par_statut_jour()
assert compte_statut.get("terminé", 0) >= 1
print("OK  comptage par statut du jour")

# ── Retrait ──
file_attente.retirer(fid1)
assert file_attente.obtenir_info(fid1) is None
print("OK  retrait de la file")

_env.nettoyer()
print()
print("TOUS LES TESTS ONT RÉUSSI — test_file_attente.py")
