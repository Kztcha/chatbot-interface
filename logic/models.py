# logic/models.py
"""
models.py
--------------------------------------------------------------------------------
Définition des modèles SQLAlchemy pour la persistance des données.

Structure de la base de données :

1. Table User (Utilisateurs) :
   - Gestion des comptes administrateurs
   - Hiérarchie des rôles (user < admin < super)
   - Authentification simple (mot de passe en clair)
   - Traçabilité (date de création)

2. Table ChatLog (Historique) :
   - Stockage des conversations
   - Lien avec l'utilisateur (foreign key)
   - Horodatage des messages
   - Distinction user/bot

Relations :
- Un User peut avoir plusieurs ChatLog (one-to-many)
- Chaque ChatLog appartient à un seul User (many-to-one)

Note de sécurité :
Le stockage des mots de passe en clair n'est pas sécurisé.
À améliorer avec :
- Hachage des mots de passe (bcrypt/argon2)
- Sel unique par utilisateur
- Politique de complexité des mots de passe
"""

from datetime import datetime
from .database import db

# --------------------------------------------------------------------------------
# MODÈLE UTILISATEUR
# --------------------------------------------------------------------------------

class User(db.Model):
    """
    Modèle pour la gestion des utilisateurs et de leurs droits.

    Attributs :
        id (int) : Identifiant unique auto-incrémenté
        username (str) : Nom d'utilisateur unique (max 80 caractères)
        password (str) : Mot de passe en clair (à sécuriser)
        role (str) : Niveau de privilège de l'utilisateur
            - 'user' : Utilisateur standard (par défaut)
            - 'admin' : Peut modifier les prompts
            - 'super' : Peut gérer les utilisateurs
        created_at (datetime) : Date de création du compte (UTC)

    Relations :
        messages : Liste des messages de l'utilisateur (via ChatLog)

    Contraintes :
        - username unique
        - Tous les champs sont obligatoires
        - role limité aux valeurs valides
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Représentation lisible de l'utilisateur pour le débogage."""
        return f"<User(username={self.username}, role={self.role})>"

# --------------------------------------------------------------------------------
# MODÈLE HISTORIQUE DES CONVERSATIONS
# --------------------------------------------------------------------------------

class ChatLog(db.Model):
    """
    Modèle pour l'historique des conversations avec le chatbot.

    Attributs :
        id (int) : Identifiant unique auto-incrémenté
        user_id (int) : Clé étrangère vers l'utilisateur
        sender (str) : Source du message
            - 'user' : Message de l'utilisateur
            - 'bot' : Réponse du chatbot
        message (str) : Contenu du message
        timestamp (datetime) : Date et heure du message (UTC)

    Relations :
        user : Référence vers l'utilisateur (User)
            - Relation many-to-one
            - Suppression en cascade si l'utilisateur est supprimé

    Contraintes :
        - Tous les champs sont obligatoires
        - sender limité à 'user' ou 'bot'
        - Clé étrangère vers user.id
    """
    __tablename__ = 'chat_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' ou 'bot'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Définition de la relation avec User
    user = db.relationship(
        'User',
        backref=db.backref('messages', lazy=True, cascade='all, delete-orphan')
    )

    def __repr__(self):
        """Représentation lisible du message pour le débogage."""
        return f"<ChatLog(user_id={self.user_id}, sender={self.sender}, time={self.timestamp})>"
