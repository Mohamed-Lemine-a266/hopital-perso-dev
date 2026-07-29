# ──────────────────────────────────────────────
# Configuration générale
# ──────────────────────────────────────────────

import os as _os
DB_NAME = _os.environ.get("HOPITAL_DB_NAME", "hopital.db")  # surchargeable (utile pour les tests)
APP_TITRE = "Système de Gestion Hospitalière"
APP_MIN_LARGEUR = 1024
APP_MIN_HAUTEUR = 600

# ── Données par défaut ──

SPECIALITES_DEFAUT = [
    "Médecine Générale", "Cardiologie", "Pédiatrie", "Gynécologie",
    "Chirurgie", "Dermatologie", "Ophtalmologie", "ORL", "Urgences", "Maternité"
]

JOURS_SEMAINE = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
JOURS_EN_FR = {"Mon": "Lun", "Tue": "Mar", "Wed": "Mer", "Thu": "Jeu",
               "Fri": "Ven", "Sat": "Sam", "Sun": "Dim"}
JOURS_TRAVAIL_DEFAUT = "Lun,Mar,Mer,Jeu,Ven"

SEXES = ["Masculin", "Féminin"]
GROUPES_SANGUINS = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
PRIORITES = ["normale", "urgente", "très urgente"]
STATUTS_MEDECIN = ["présent", "absent", "en congé"]
STATUTS_FILE = ["en attente", "appelé", "en consultation", "terminé", "absent"]
STATUTS_RDV = ["planifié", "confirmé", "annulé", "terminé"]

# ── Paramètres par défaut (table parametres) ──

PARAMS_DEFAUT = {
    "nom_hopital": "Hôpital Central",
    "email_hopital": "",
    "logo_path": "",
    "prefixe_patient": "HOP",
    "duree_rdv_defaut": "30",
}

# ── Couleurs de l'interface ──

C_SIDEBAR = "#1B3A4B"
C_SIDEBAR_BTN = "#274C5B"
C_SIDEBAR_ACTIVE = "#3A7CA5"
C_FOND = "#F0F2F5"
C_PRIMAIRE = "#2A6F97"
C_SUCCES = "#27AE60"
C_DANGER = "#C0392B"
C_AVERTISSEMENT = "#E67E22"
C_INFO = "#2980B9"
C_TEXTE = "#2C3E50"

# ── Délai de recherche instantanée (ms) ──

DELAI_RECHERCHE = 300

# ──────────────────────────────────────────────
# Système de design — typographie, icônes, espacements
# ──────────────────────────────────────────────

FONT_FAMILLE = "Segoe UI"          # repli automatique et silencieux si absente (Tk)
FONT_FAMILLE_MONO = "Consolas"

FONT_H1 = (FONT_FAMILLE, 19, "bold")        # titre de page
FONT_H2 = (FONT_FAMILLE, 14, "bold")        # titre de section
FONT_H3 = (FONT_FAMILLE, 11, "bold")        # sous-titre / en-tête de groupe
FONT_TEXTE = (FONT_FAMILLE, 10)             # texte courant
FONT_TEXTE_GRAS = (FONT_FAMILLE, 10, "bold")
FONT_PETIT = (FONT_FAMILLE, 9)              # légendes, aides
FONT_PETIT_ITAL = (FONT_FAMILLE, 9, "italic")
FONT_BOUTON = (FONT_FAMILLE, 10, "bold")
FONT_CHIFFRE = (FONT_FAMILLE, 26, "bold")   # grands nombres (cartes tableau de bord)

# Espacements standard (en pixels) — à utiliser pour pady/padx
ESP_XS = 2
ESP_S = 5
ESP_M = 10
ESP_L = 16
ESP_XL = 24

# ── Palette étendue ──
C_SURFACE = "#FFFFFF"          # fond des cartes / panneaux
C_BORDURE = "#E0E4E8"
C_TEXTE_SECONDAIRE = "#6B7785"
C_HOVER_PRIMAIRE = "#235A7A"
C_SIDEBAR_TEXTE_ATTENUE = "#89C2D9"

# ── Icônes (glyphes unicode — aucune dépendance externe) ──
ICONS = {
    "accueil": "🏠", "accueil_patient": "🧾", "patients": "🧍", "medecins": "🩺",
    "file_attente": "⏳", "rendez_vous": "📅", "consultations": "📋",
    "recherche": "🔎", "statistiques": "📊", "parametres": "⚙", "utilisateurs": "👥",
    "journal": "🕒", "documents": "📁", "deconnexion": "⏻",
    "specialites": "🏷", "dossier_patient": "🗂", "mon_profil": "👤",
    "ajouter": "➕", "modifier": "✎", "supprimer": "🗑", "imprimer": "🖶",
    "valider": "✔", "annuler": "✖", "chercher": "🔎", "suivant": "➜",
    "sauvegarder": "💾", "logo_defaut": "🏥",
}
