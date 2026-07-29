import tkinter as tk
from config import APP_TITRE, APP_MIN_LARGEUR, APP_MIN_HAUTEUR, C_FOND
from database import creer_tables
from views.login import LoginWindow
from views.navigation import Navigation
from views.accueil import VueAccueil
from views.accueil_patient import VueAccueilPatient
from views.patients import VuePatients
from views.medecins import VueMedecins
from views.file_attente import VueFileAttente
from views.rendez_vous import VueRendezVous
from views.consultations import VueConsultations
from views.recherche import VueRecherche
from views.statistiques import VueStatistiques
from views.parametres import VueParametres
from views.utilisateurs import VueUtilisateurs
from views.journal import VueJournal
from views.documents import VueDocuments
from views.specialites import VueSpecialites
from views.mon_profil import VueMonProfil
from views.dossier_patient import VueDossierPatient

creer_tables()

fenetre = tk.Tk()
fenetre.title(APP_TITRE)
fenetre.configure(bg=C_FOND)
fenetre.minsize(APP_MIN_LARGEUR, APP_MIN_HAUTEUR)

# Maximiser la fenêtre
try:
    fenetre.state("zoomed")
except Exception:
    try:
        fenetre.attributes("-zoomed", True)
    except Exception:
        fenetre.geometry("1200x800")


def lancer_application(utilisateur_info, permissions):
    vues = {
        "accueil": VueAccueil(),
        "accueil_patient": VueAccueilPatient(),
        "patients": VuePatients(),
        "medecins": VueMedecins(),
        "file_attente": VueFileAttente(),
        "rendez_vous": VueRendezVous(),
        "consultations": VueConsultations(),
        "recherche": VueRecherche(),
        "statistiques": VueStatistiques(),
        "parametres": VueParametres(),
        "utilisateurs": VueUtilisateurs(),
        "journal": VueJournal(),
        "documents": VueDocuments(),
        "specialites": VueSpecialites(),
        "mon_profil": VueMonProfil(),
        "dossier_patient": VueDossierPatient(),
    }
    nav = Navigation(fenetre, vues, permissions, utilisateur_info)
    nav.afficher_vue("accueil")


LoginWindow(fenetre, lancer_application)

fenetre.mainloop()
