"""
Prépare un environnement de test isolé : redirige la base de données vers
un fichier temporaire AVANT que les autres modules ne soient importés.
À importer en tout premier dans chaque script de test.
"""
import sys
import os
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

_fd, _chemin_db_test = tempfile.mkstemp(suffix="_test.db")
os.close(_fd)
os.remove(_chemin_db_test)  # sqlite3.connect recrée le fichier
os.environ["HOPITAL_DB_NAME"] = _chemin_db_test


def nettoyer():
    try:
        os.remove(_chemin_db_test)
    except OSError:
        pass
