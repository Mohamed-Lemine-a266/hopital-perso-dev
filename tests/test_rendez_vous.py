"""Tests des rendez-vous : conflits de créneaux, absences planifiées, doublons."""
import _env
from database import creer_tables
from models import patient, medecin, specialite, rendez_vous, absence

creer_tables()
specs = specialite.charger_toutes()
spec_id = specs[0][0]

p1 = patient.ajouter("SN300001", "Ba", "Mariama", "Féminin", "1988-01-01", "770000010", "Dakar", "2026-07-23")
m1 = medecin.ajouter("Diop", "Cheikh", "760000010", spec_id, "Lun,Mar,Mer,Jeu,Ven", "08:00", "17:00")

# ── Planification de base ──
rid = rendez_vous.ajouter(p1, m1, "2026-08-17 10:00", 30, "Contrôle")
assert rid is not None
print("OK  planification d'un rendez-vous")

# ── Conflit de créneau (chevauchement) ──
assert rendez_vous.conflit_horaire(m1, "2026-08-17 10:15", 30) is True   # chevauche
assert rendez_vous.conflit_horaire(m1, "2026-08-17 10:30", 30) is False  # juste après, pas de chevauchement
assert rendez_vous.conflit_horaire(m1, "2026-08-17 09:30", 30) is False  # juste avant, pas de chevauchement
assert rendez_vous.conflit_horaire(m1, "2026-08-17 09:45", 30) is True   # chevauche la fin
print("OK  détection de conflit de créneau (cas limites inclus)")

# ── Doublon exact ──
assert rendez_vous.existe_deja(p1, m1, "2026-08-17 10:00") is True
assert rendez_vous.existe_deja(p1, m1, "2026-08-18 10:00") is False
print("OK  détection de doublon exact")

# ── Absences planifiées ──
aid = absence.ajouter(m1, "2026-08-20", "2026-08-25", "Congé annuel")
assert absence.est_absent_a_la_date(m1, "2026-08-22") is True
assert absence.est_absent_a_la_date(m1, "2026-08-19") is False
assert absence.est_absent_a_la_date(m1, "2026-08-26") is False
print("OK  vérification des absences planifiées")

# ── Suppression d'une absence ──
absence.supprimer(aid)
assert absence.est_absent_a_la_date(m1, "2026-08-22") is False
print("OK  suppression d'une absence")

# ── Changement de statut ──
rendez_vous.changer_statut(rid, "annulé")
rdv = rendez_vous.obtenir_par_id(rid)
assert rdv[6] == "annulé"
print("OK  changement de statut du rendez-vous")

# ── Un RDV annulé ne bloque plus le créneau ──
assert rendez_vous.conflit_horaire(m1, "2026-08-17 10:00", 30) is False
print("OK  un rendez-vous annulé libère le créneau")

_env.nettoyer()
print()
print("TOUS LES TESTS ONT RÉUSSI — test_rendez_vous.py")
