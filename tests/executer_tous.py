"""Exécute tous les scripts de test du dossier et affiche un résumé final."""
import subprocess
import sys
import os

DOSSIER = os.path.dirname(os.path.abspath(__file__))
TESTS = ["test_patient.py", "test_file_attente.py", "test_rendez_vous.py", "test_audit_permissions.py"]

reussis, echoues = [], []

for nom_test in TESTS:
    chemin = os.path.join(DOSSIER, nom_test)
    print(f"\n{'=' * 60}\n{nom_test}\n{'=' * 60}")
    resultat = subprocess.run([sys.executable, chemin], capture_output=True, text=True)
    print(resultat.stdout)
    if resultat.returncode == 0:
        reussis.append(nom_test)
    else:
        echoues.append(nom_test)
        print(resultat.stderr)

print(f"\n{'=' * 60}")
print(f"RÉSUMÉ : {len(reussis)}/{len(TESTS)} scripts réussis")
if echoues:
    print(f"ÉCHOUÉS : {', '.join(echoues)}")
    sys.exit(1)
else:
    print("TOUS LES TESTS ONT RÉUSSI")
