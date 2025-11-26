# Evaluation du démarrage backend

## Constat actuel
- Le script `backend/scripts/start_backend.sh` privilégie Poetry puis bascule sur un environnement virtuel local si nécessaire. Les variables `BACKEND_START_MODE` et `BACKEND_SKIP_INSTALL` permettent de tester le bootstrap sans installer ni lancer le serveur.
- Le README documente le chemin standard et les flags de test/CI, ce qui facilite la prise en main.
- Des tests unitaires (`backend/tests/test_start_backend.py`) valident le choix du lanceur (Poetry vs virtualenv) en mode impression.

## Points forts
- **Robustesse du bootstrap** : le fallback virtuel évite les blocages en absence de Poetry.
- **Observabilité** : le mode `print` fournit un signal clair sur le chemin exécuté, utile en CI.
- **Couverture minimale** : les tests couvrent les chemins de sélection du lanceur.

## Limites identifiées
- **Pas de vérification du fichier `.env`** : le démarrage ne signale pas l’absence de configuration environnementale potentiellement requise par l’app.
- **Tests d’intégration absents** : aucune validation de bout en bout (install + lancement réel d’Uvicorn) n’est automatisée.
- **Gestion des erreurs réseau** : en cas d’échec `poetry install`/`pip install`, le script échoue sans proposer de reprise (cache ou miroir).

## Recommandations prioritaires
1. Ajouter un pré-check optionnel pour vérifier la présence de `backend/.env` et afficher un avertissement clair s’il manque.
2. Intégrer un test d’intégration léger qui lance Uvicorn sur un port éphémère avec `BACKEND_SKIP_INSTALL=1` et vérifie une réponse basique (healthcheck) pour s’assurer que le code démarre.
3. Documenter un mécanisme de retry ou de configuration de miroirs PyPI pour les environnements réseau restreints.

## Note globale
Sur la solution actuelle après modifications : **7/10**. Le bootstrap est plus résilient et testé, mais il manque encore des garde-fous de configuration et des tests d’intégration pour couvrir le démarrage réel de l’application.
