# Système de Gestion Hospitalière

Application de bureau développée en **Python** avec **Tkinter** (interface graphique)
et **SQLite** (base de données) — aucune dépendance externe.

## Prérequis

- Python 3.8 ou supérieur (Tkinter est inclus dans l'installation standard de Python
  sur Windows et macOS ; sur Linux, installer le paquet `python3-tk` si nécessaire).

## Lancement

```bash
python3 main.py
```

Au premier lancement, la base de données `hopital.db` est créée automatiquement
avec les données par défaut (spécialités, paramètres, rôles, permissions et un
compte administrateur).

**Compte par défaut :** identifiant `admin`, mot de passe `admin`.
Il est recommandé de changer ce mot de passe dès la première connexion
(menu **Mon profil**, accessible en cliquant sur son nom en haut de la barre latérale).

## Architecture du projet

```
hopital/
├── main.py                  Point d'entrée de l'application
├── config.py                Constantes, couleurs, polices, icônes, données par défaut
├── database.py               Connexion SQLite, création et migration du schéma
├── session.py                 Contexte de l'utilisateur connecté (pour l'audit)
│
├── models/                  Accès aux données — aucune logique d'interface
│   ├── patient.py, medecin.py, specialite.py
│   ├── file_attente.py, rendez_vous.py, consultation.py
│   ├── constantes_vitales.py, document.py, absence.py
│   ├── utilisateur.py         Utilisateurs, rôles, permissions
│   ├── audit.py               Journal des actions
│   ├── parametres.py, statistiques.py
│
├── views/                   Interface graphique (une classe par écran)
│   ├── navigation.py, login.py, accueil.py
│   ├── accueil_patient.py      Point d'entrée principal (accueil + orientation)
│   ├── patients.py, medecins.py, specialites.py
│   ├── file_attente.py, rendez_vous.py, consultations.py
│   ├── documents.py, recherche.py, dossier_patient.py
│   ├── statistiques.py, parametres.py
│   ├── utilisateurs.py, journal.py, mon_profil.py, absences.py
│   ├── ecran_public.py         Affichage plein écran pour salle d'attente
│   └── widgets.py              Composants réutilisables (calendrier, sélecteur d'heure)
│
├── utils/
│   ├── impression.py           Génération de documents HTML imprimables
│   └── sauvegarde.py           Sauvegarde et restauration de la base
│
├── documents_patients/        Fichiers uploadés (ordonnances, radios, etc.)
└── tests/                     Tests automatisés (voir tests/README.md)
```

## Fonctionnalités principales

- **Gestion des utilisateurs, rôles et permissions**, entièrement configurable
  depuis l'application (aucun rôle codé en dur).
- **Accueil Patient** : recherche par CNI, création ou mise à jour du dossier,
  orientation automatique ou manuelle vers un médecin, placement en file d'attente.
- **File d'attente** par médecin/spécialité avec priorités, tickets journaliers,
  machine à états (en attente → appelé → en consultation → terminé).
- **Rendez-vous** avec validation complète (horaires, jours travaillés, absences
  planifiées, conflits de créneaux, dates passées).
- **Dossier médical** : allergies, antécédents, groupe sanguin, constantes vitales.
- **Documents patients** : ordonnances, analyses, imagerie — associés au dossier.
- **Dossier patient unifié** avec onglets (Informations / Constantes / Consultations /
  Rendez-vous / Documents).
- **Statistiques** avec graphiques et export CSV.
- **Écran public** pour salle d'attente (derniers tickets appelés).
- **Journal d'audit** : trace qui a fait quoi, avec les anciennes et nouvelles valeurs
  lors des modifications.
- **Sauvegarde et restauration** de la base de données.

## Notes techniques

- Toutes les dates sont stockées au format `AAAA-MM-JJ` et les heures au format `HH:MM`,
  ce qui permet un tri correct par simple comparaison de texte.
- La connexion SQLite est unique et partagée (`database.py`), avec
  `PRAGMA foreign_keys = ON` activé.
- Les migrations de schéma (ajout de colonnes/tables sur une base existante) sont
  gérées de façon idempotente dans `database.py` — aucune perte de données lors
  des mises à jour de l'application.
