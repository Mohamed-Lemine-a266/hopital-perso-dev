# Tests automatisés

Ces tests vérifient la logique métier critique (modèles) sur une base de
données temporaire, isolée de la base réelle. Ils ne nécessitent aucune
bibliothèque externe (assertions Python standard uniquement).

## Exécution

Depuis le dossier `hopital/` :

```bash
python3 tests/test_patient.py
python3 tests/test_file_attente.py
python3 tests/test_rendez_vous.py
python3 tests/test_audit_permissions.py
```

Ou tous en une fois :

```bash
python3 tests/executer_tous.py
```

Chaque script affiche `OK` pour chaque vérification et se termine par
`TOUS LES TESTS ONT RÉUSSI` s'il n'y a eu aucune erreur. Toute assertion
échouée interrompt le script avec un message d'erreur explicite.
