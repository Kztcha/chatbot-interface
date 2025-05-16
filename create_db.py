# create_db.py
"""
create_db.py
──────────────────────────────────────────────────────────────
Script utilitaire pour :
- Créer la base de données (data.db),
- Créer les tables si elles n'existent pas,
- Ajouter un superadmin initial si besoin.

Ce script est utilisé lors du premier démarrage de l'application
ou pour réinitialiser la base de données en cas de besoin.
"""

from flask import Flask
from logic.database import init_app, db
from logic.models import User

# Configuration d'une app Flask minimale pour l'initialisation
# Cette configuration est temporaire et uniquement pour la création de la DB
app = Flask(__name__)
# Configuration de la base de données SQLite
# Le fichier data.db sera créé dans le répertoire courant
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Désactive le suivi des modifications pour optimiser les performances
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialise la connexion à la base de données
init_app(app)

# Création et insertion des données dans un contexte d'application
# Le contexte est nécessaire pour les opérations de base de données
with app.app_context():
    # Création des tables définies dans les modèles
    # Si les tables existent déjà, cette opération est ignorée
    db.create_all()

    # Vérification de l'existence du superadmin par défaut
    # Ce compte est créé uniquement s'il n'existe pas déjà
    existing = User.query.filter_by(username="admin").first()
    if not existing:
        # Création du superadmin avec les identifiants par défaut
        # Note: Ces identifiants doivent être changés en production
        admin = User(username="admin", password="admin", role="super")
        db.session.add(admin)
        db.session.commit()
        print("✔️ Superadmin créé : admin / admin")
    else:
        print("ℹ️ Le superadmin existe déjà.")

print("✅ Base de données initialisée.")
