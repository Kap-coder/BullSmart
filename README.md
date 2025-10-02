# BullSmart

BullSmart est une application de gestion scolaire développée avec Django. Elle permet la gestion des bulletins, des étudiants, des templates de bulletins, et d'autres fonctionnalités liées à l'administration scolaire.

## Structure du projet
- **Bull/** : Application principale contenant les modèles, vues, formulaires, serializers, commandes de gestion, migrations, fichiers statiques et templates.
- **SmartBull/** : Configuration du projet Django (settings, urls, wsgi, asgi).
- **bulletin_templates/** : Modèles de documents Word pour les bulletins (headers et footers).
- **bulletins/** : Bulletins PDF générés pour les étudiants.
- **students/** : Images et documents liés aux étudiants.
- **db.sqlite3** : Base de données SQLite du projet.
- **manage.py** : Script de gestion Django.

## Installation
1. Cloner le projet.
2. Installer les dépendances Python (voir requirements.txt si disponible).
3. Appliquer les migrations :
   ```powershell
   python manage.py migrate
   ```
4. Lancer le serveur de développement :
   ```powershell
   python manage.py runserver
   ```

## Fonctionnalités principales
- Gestion des étudiants et des bulletins
- Génération de bulletins PDF
- Administration via l'interface Django
- Personnalisation des templates de bulletins

## Auteur
Projet personnel pour la gestion scolaire.

## Licence
Ce projet est à usage personnel et éducatif.