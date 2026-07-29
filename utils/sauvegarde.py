import shutil
import os
from datetime import datetime
from config import DB_NAME
from database import connection


def sauvegarder_base(destination):
    """Sauvegarde la base de données vers le chemin choisi."""
    connection.commit()
    shutil.copy2(DB_NAME, destination)


def restaurer_base(source):
    """
    Restaure une sauvegarde. L'application doit être redémarrée après
    restauration (la connexion active pointe encore sur l'ancien fichier).
    Une copie de sécurité de la base actuelle est créée avant l'écrasement.
    """
    if not os.path.exists(source):
        raise FileNotFoundError("Le fichier de sauvegarde est introuvable.")

    connection.commit()

    if os.path.exists(DB_NAME):
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        secours = f"{DB_NAME}.avant_restauration_{horodatage}.bak"
        shutil.copy2(DB_NAME, secours)

    shutil.copy2(source, DB_NAME)
