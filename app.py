# -*- coding: utf-8 -*-
"""
app.py
--------------------------------------------------------------------------------
Point d'entree principal de l'application Flask qui gere le routage et la configuration.

Responsabilites :
1. Configuration de l'application Flask et ses composants
2. Definition des routes pour :
   - Interface utilisateur du chatbot
   - Interface d'administration des prompts
   - Gestion des utilisateurs (superadmin)
3. Gestion de l'authentification et des sessions
4. Protection contre la mise en cache des reponses

Structure des routes :
- / : Page d'accueil du chatbot
- /start, /message, /regen : Endpoints API du chatbot
- /admin/* : Interface d'administration
- /login, /logout : Gestion de session
"""

import os
from flask import Flask, session
import logic  # Module principal contenant toute la logique metier
from logic.database import init_app  # Gestionnaire de la base de donnees SQLite

# --------------------------------------------------------------------------------
# CONFIGURATION DE L'APPLICATION FLASK
# --------------------------------------------------------------------------------


# Initialisation de l'application Flask avec configuration de base
# - template_folder : répertoire des templates HTML pour le rendu des pages
# - static_folder : répertoire des fichiers statiques (CSS, JS, images)
app = Flask(__name__)
app.secret_key = logic.SECRET_KEY  # Clé de sécurité pour chiffrer les sessions
app.config["SESSION_PERMANENT"] = False  # Sessions temporaires pour plus de sécurité

# Initialisation de la base de données SQLite
# Crée les tables si elles n'existent pas et configure la connexion
init_app(app)

# Injecte les données de session dans tous les templates
# Permet d'accéder à session.admin_username, session.admin_role, etc.
# Utile pour l'affichage conditionnel des éléments selon le rôle de l'utilisateur
from logic.users import find_user_by_id

@app.context_processor
def inject_user_role():
    user_info = None
    if session.get("user_id"):
        user = find_user_by_id(session["user_id"])
        if user:
            user_info = {"username": user.username}
    return dict(session=session, user_info=user_info)

# --------------------------------------------------------------------------------
# ROUTES UTILISATEUR (CHATBOT)
# --------------------------------------------------------------------------------

@app.route("/")
def index():
    """Page d'accueil du chatbot."""
    return logic.index()

@app.route("/start", methods=["GET"])
def start():
    """
    Démarre une nouvelle conversation.
    Réinitialise l'état de la conversation et retourne le message initial.
    """
    return logic.start()

@app.route("/message", methods=["POST"])
def message():
    """
    Traite un message de l'utilisateur.
    Reçoit les données du formulaire, les traite et retourne la réponse du bot.
    """
    return logic.handle_message()

@app.route("/regen", methods=["GET"])
def regenerate():
    """
    Régénère la dernière réponse.
    Permet à l'utilisateur de demander une nouvelle version de la dernière réponse du bot.
    """
    return logic.regenerate()

@app.route("/types", methods=["GET"])
def get_types():
    """
    Retourne la liste des types d'emails disponibles.
    Utilisé pour mettre à jour dynamiquement les options du formulaire.
    """
    return logic.get_types()

# --------------------------------------------------------------------------------
# ROUTES ADMIN (PROMPTS + UTILISATEURS)
# --------------------------------------------------------------------------------

# Décorateur @logic.admin_required : Vérifie que l'utilisateur est connecté en tant qu'admin
# Décorateur @logic.superadmin_required : Vérifie que l'utilisateur est un superadmin

@app.route("/admin", methods=["GET"])
@logic.admin_required
def admin_prompts():
    """
    Interface d'administration des prompts (accessible aux admins).
    Affiche l'interface de gestion des prompts et des types d'emails.
    """
    return logic.admin_prompts_page()

# Gestion des types d'emails
@app.route("/admin/type/add", methods=["POST"])
@logic.admin_required
def admin_add_type():
    """
    Ajoute un nouveau type d'email.
    Reçoit les données du formulaire et crée un nouveau type dans la base de données.
    """
    return logic.add_email_type()

@app.route("/admin/type/delete", methods=["POST"])
@logic.admin_required
def admin_delete_type():
    """
    Supprime un type d'email existant.
    Vérifie les dépendances avant la suppression pour éviter les erreurs.
    """
    return logic.delete_email_type()

# Gestion des champs de formulaire
@app.route("/admin/field/add", methods=["POST"])
@logic.admin_required
def admin_add_field():
    """
    Ajoute un nouveau champ à un type d'email.
    Configure les propriétés du champ (label, type, options, etc.).
    """
    return logic.add_form_field()

@app.route("/admin/field/delete", methods=["POST"])
@logic.admin_required
def admin_delete_field():
    """
    Supprime un champ d'un type d'email.
    Met à jour la structure du formulaire associé.
    """
    return logic.delete_form_field()

# Gestion des prompts
@app.route("/admin/prompt/update", methods=["POST"])
@logic.admin_required
def admin_update_prompt():
    """
    Met à jour le prompt d'un type d'email.
    Modifie le template utilisé pour générer les réponses.
    """
    return logic.update_prompt()

@app.route("/admin/save", methods=["POST"])
@logic.admin_required
def save_prompts():
    """
    Sauvegarde les modifications des prompts (accessible aux admins).
    Persiste les changements dans la base de données.
    """
    return logic.save_prompts()

# Gestion des comptes utilisateurs (superadmin uniquement)
@app.route("/admin/users", methods=["GET"])
@logic.admin_required
@logic.superadmin_required
def admin_users():
    """
    Interface de gestion des utilisateurs (accessible uniquement aux superadmins).
    Permet de voir, ajouter, modifier et supprimer les comptes administrateurs.
    """
    return logic.admin_users_page()

@app.route("/admin/users/add", methods=["POST"])
@logic.admin_required
@logic.superadmin_required
def admin_add_user():
    """
    Ajoute un nouvel utilisateur admin (superadmin uniquement).
    Vérifie la validité des données et crée le compte avec le rôle spécifié.
    """
    return logic.add_user()

@app.route("/admin/users/delete", methods=["POST"])
@logic.admin_required
@logic.superadmin_required
def admin_delete_user():
    """
    Supprime un utilisateur admin existant (superadmin uniquement).
    Empêche la suppression du dernier superadmin.
    """
    return logic.delete_user()

@app.route("/admin/users/update", methods=["POST"])
@logic.admin_required
@logic.superadmin_required
def admin_update_password():
    """
    Met à jour le mot de passe d'un utilisateur admin (superadmin uniquement).
    Applique le hachage de sécurité avant la sauvegarde.
    """
    return logic.update_password()

@app.route("/admin/users/table")
@logic.admin_required
@logic.superadmin_required
def admin_users_table():
    """
    Affiche le tableau des utilisateurs admin (superadmin uniquement).
    Génère le HTML du tableau avec les actions disponibles.
    """
    return logic.render_users_table()

# --------------------------------------------------------------------------------
# AUTHENTIFICATION
# --------------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Gère l'authentification des administrateurs :
    - GET : affiche le formulaire de connexion
    - POST : vérifie les identifiants et crée la session
    La session contient le nom d'utilisateur et le rôle pour les vérifications ultérieures.
    """
    return logic.login_page()

@app.route("/logout")
def logout():
    """
    Déconnecte l'utilisateur en supprimant sa session.
    Redirige vers la page de connexion après la déconnexion.
    """
    return logic.logout()

@app.after_request
def add_header(response):
    """
    Ajoute des en-têtes HTTP pour empêcher la mise en cache des réponses.
    Important pour :
    - La sécurité : empêche l'accès aux données sensibles en cache
    - La cohérence : garantit que les données sont toujours à jour
    - L'expérience utilisateur : évite les problèmes de données périmées
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --------------------------------------------------------------------------------
# AUTHENTIFICATION UTILISATEUR CLASSIQUE (chatbot)
# --------------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    return logic.signup_page()

@app.route("/login-user", methods=["GET", "POST"])
def login_user():
    return logic.login_user_page()

@app.route("/logout-user")
def logout_user():
    return logic.logout_user()

# --------------------------------------------------------------------------------
# DEMARRAGE DE L'APPLICATION
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    # Note : En production, l'application est servie par Gunicorn (voir Dockerfile)
    # Le mode debug est activé uniquement en développement
    app.run(debug=True)
