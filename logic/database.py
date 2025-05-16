# logic/database.py
"""
database.py
--------------------------------------------------------------------------------
Configuration et initialisation de la base de données SQLite avec SQLAlchemy.

Responsabilités :
1. Configuration de la base de données :
   - Utilisation de SQLite pour la simplicité
   - Fichier data.db créé dans l'instance Flask
   - Désactivation du suivi des modifications pour les performances

2. Initialisation de SQLAlchemy :
   - Instance globale unique de SQLAlchemy
   - Configuration via l'application Flask
   - Point d'entrée pour les modèles

3. Utilisation :
   - Importer 'db' dans les modèles pour définir les tables
   - Appeler init_app() dans app.py pour initialiser
   - Les modèles utilisent db.Model comme classe de base

Note technique :
Le fichier data.db est créé automatiquement dans le dossier instance/
de l'application Flask. Pour la production, considérer :
- Utiliser une base de données plus robuste (PostgreSQL)
- Configurer les sauvegardes automatiques
- Gérer les migrations avec Flask-Migrate
"""

from flask_sqlalchemy import SQLAlchemy

# --------------------------------------------------------------------------------
# INSTANCE SQLALCHEMY
# --------------------------------------------------------------------------------

# Instance globale unique de SQLAlchemy
# Utilisée par tous les modèles pour définir les tables
db = SQLAlchemy()

def init_app(app):
    """
    Configure et initialise la base de données pour l'application Flask.

    Cette fonction doit être appelée après la création de l'application Flask
    mais avant toute utilisation des modèles ou de la base de données.

    Args:
        app (Flask): L'instance de l'application Flask

    Configuration :
        - SQLALCHEMY_DATABASE_URI : Chemin vers la base SQLite
        - SQLALCHEMY_TRACK_MODIFICATIONS : Désactivé pour les performances

    Note :
        Le fichier data.db sera créé automatiquement dans le dossier instance/
        lors de la première utilisation ou via create_db.py
    """
    # Configuration de la base SQLite dans le dossier instance/
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

    # Désactive le suivi des modifications de SQLAlchemy
    # Améliore les performances car on n'utilise pas cette fonctionnalité
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise l'extension SQLAlchemy avec notre application
    db.init_app(app)
