# BullSmart

BullSmart est une application de gestion scolaire développée avec Django.

## Fonctionnalités principales
- Gestion des élèves, classes, enseignants, matières et bulletins
- Génération automatique des bulletins PDF
- Attribution des sanctions et mentions
- Administration via l'interface Django
- Personnalisation des templates de bulletins

## Structure du projet
- **Bull/** : Application principale (modèles, vues, formulaires, serializers, commandes, migrations, statiques, templates)
- **SmartBull/** : Configuration du projet Django (settings, urls, wsgi, asgi)
- **bulletin_templates/** : Modèles Word pour les bulletins (headers et footers)
- **bulletins/** : Bulletins PDF générés
- **students/** : Images et documents liés aux élèves
- **db.sqlite3** : Base de données SQLite
- **manage.py** : Script de gestion Django

## Installation
1. Cloner le projet
2. Installer les dépendances Python
3. Appliquer les migrations :
   ```powershell
   python manage.py migrate
   ```
4. Lancer le serveur de développement :
   ```powershell
   python manage.py runserver
   ```

## Auteur
Projet personnel pour la gestion scolaire

## Licence
Usage personnel et éducatif
