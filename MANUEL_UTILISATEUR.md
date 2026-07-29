# Manuel utilisateur — Système de Gestion Hospitalière

## 1. Connexion

Au lancement, saisissez votre identifiant et votre mot de passe.
Compte par défaut : `admin` / `admin` (à changer immédiatement après la première connexion).

## 2. Prendre en charge un patient (module « Accueil Patient »)

C'est l'écran utilisé pour chaque nouvelle arrivée.

1. Saisissez le **numéro de CNI** du patient et validez.
   - Si le patient existe déjà, ses informations apparaissent automatiquement.
   - S'il n'existe pas, remplissez le formulaire (nom, prénom, sexe, date de
     naissance, téléphone, adresse). Si le patient n'a pas de CNI (enfant,
     étranger), cochez **« Sans CNI »** : un numéro est généré automatiquement.
2. Choisissez la **spécialité**, puis le **médecin** (le médecin le moins chargé
   est présélectionné automatiquement).
3. Choisissez la **priorité** (normale, urgente, très urgente) et indiquez le motif.
4. Cliquez sur **« Enregistrer et placer en file d'attente »**.

Un ticket (ex : T014) est attribué. Le patient apparaît dans la file du médecin choisi.

## 3. Gérer la file d'attente

Dans le module **File d'attente** :

- **Appeler suivant** : appelle le patient prioritaire suivant pour le médecin
  sélectionné (priorité, puis ordre d'arrivée).
- **Patient absent** : si le patient appelé ne se présente pas, il est remis
  en fin de file.
- **Début consultation** : passe le patient en consultation.
- **Terminer** : clôture la prise en charge et ouvre directement le formulaire
  de consultation (diagnostic obligatoire).
- **Écran public** : ouvre un affichage plein écran (à projeter en salle
  d'attente) montrant les derniers tickets appelés. Fermer avec la touche Échap.

## 4. Rendez-vous

Le module **Rendez-vous** empêche automatiquement :
- les rendez-vous dans le passé ;
- les créneaux hors des horaires de travail du médecin ;
- les jours où le médecin ne travaille pas ;
- les absences planifiées (congés) ;
- les chevauchements avec un autre rendez-vous du même médecin.

Le bouton **« Patient arrivé »** place directement le patient dans la file
d'attente le jour du rendez-vous.

## 5. Dossier médical et documents

- Dans **Patients**, le bouton **« Infos médicales »** permet de renseigner
  allergies, antécédents et groupe sanguin.
- Dans **Consultations**, les constantes vitales (taille, poids, température,
  tension, fréquence cardiaque, saturation) peuvent être saisies en même temps
  que le diagnostic.
- Le module **Documents** permet d'associer des fichiers (ordonnances, analyses,
  imagerie) à un dossier patient.
- Le module **Dossier patient** regroupe tout cela dans une seule fenêtre à onglets.

## 6. Statistiques

Le module **Statistiques** affiche, pour la période choisie : le nombre de
patients reçus, la répartition par spécialité (graphique), la charge par
médecin (graphique), le temps moyen d'attente, le taux de rendez-vous honorés/
annulés et le jour le plus chargé. Le bouton **« Exporter en CSV »** permet
d'extraire ces données vers un tableur.

## 7. Administration

- **Spécialités** : ajouter, renommer ou supprimer les spécialités de l'établissement.
- **Médecins** : gérer les médecins, leurs horaires, jours de travail, statut,
  et leurs **absences planifiées** (bouton dédié).
- **Utilisateurs** : créer des comptes, définir des rôles personnalisés et
  leurs permissions, ou accorder/retirer une permission individuelle.
- **Journal d'audit** : historique complet des créations, modifications et
  suppressions, avec l'utilisateur responsable et (si disponible) l'ancienne
  et la nouvelle valeur.
- **Paramètres** : nom et logo de l'hôpital, préfixe des numéros auto-générés,
  durée par défaut des rendez-vous, sauvegarde et restauration de la base de données.

## 8. Mon profil

Cliquez sur votre nom en haut de la barre latérale pour changer votre mot de
passe sans passer par un administrateur.
