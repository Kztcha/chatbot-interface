# logic/users.py
"""
users.py
--------------------------------------------------------------------------------
Gestion des utilisateurs administrateurs, utilisateurs classiques, et de l'authentification.

Responsabilités :
1. Gestion des comptes :
   - Création de nouveaux administrateurs ou utilisateurs
   - Suppression de comptes existants
   - Mise à jour des mots de passe
   - Chargement de la liste des utilisateurs

2. Authentification :
   - Login/logout des administrateurs
   - Login/logout des utilisateurs
   - Gestion des sessions Flask
   - Stockage des rôles ou identifiants en session

3. Contrôle d'accès :
   - Décorateur @admin_required pour les routes protégées admin
   - Décorateur @superadmin_required pour les actions sensibles
   - Décorateur @login_required pour le chatbot
   - Vérification des permissions à chaque action

4. Interface utilisateur :
   - Rendu des templates d'authentification
   - Affichage du tableau des utilisateurs
   - Messages d'erreur et redirections

Note de sécurité :
Cette implémentation est basique et nécessite des améliorations :
- Hachage des mots de passe
- Protection contre les attaques par force brute
- Gestion des tokens CSRF
- Validation plus stricte des entrées
"""

from functools import wraps
from flask import request, session, redirect, render_template
from logic.models import User
from logic.database import db

# --------------------------------------------------------------------------------
# FONCTIONS UTILISATEURS
# --------------------------------------------------------------------------------

def load_users():
    """Charge la liste complète des utilisateurs depuis la base de données."""
    return User.query.all()

def save_users(users):
    """Fonction maintenue pour compatibilité historique (inutile avec SQLAlchemy)."""
    pass

def find_user(username):
    """Recherche un utilisateur par son nom d'utilisateur."""
    return User.query.filter_by(username=username).first()

def find_user_by_id(user_id):
    """Recherche un utilisateur par son identifiant numérique."""
    return User.query.filter_by(id=user_id).first()

# --------------------------------------------------------------------------------
# AUTHENTIFICATION ADMIN
# --------------------------------------------------------------------------------

def login_page():
    """Connexion administrateur (GET : formulaire, POST : vérification)."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username)
        if user and user.password == password and user.role in ("admin", "super"):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session["admin_role"] = user.role
            return redirect("/admin")
        return "Identifiants incorrects", 401
    return render_template("login.html")

def logout():
    """Déconnecte un administrateur en supprimant sa session."""
    session.clear()
    return redirect("/")

# --------------------------------------------------------------------------------
# AUTHENTIFICATION UTILISATEUR (chatbot)
# --------------------------------------------------------------------------------

def signup_page():
    """Page d'inscription utilisateur classique (GET/POST)."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Champs requis", 400
        if find_user(username):
            return "Nom d'utilisateur déjà utilisé", 400
        user = User(username=username, password=password, role="user")
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect("/")
    return render_template("signup.html")

def login_user_page():
    """Connexion utilisateur classique (GET/POST)."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username)
        if user and user.password == password and user.role == "user":
            session["user_id"] = user.id
            return redirect("/")
        return "Identifiants incorrects", 401
    return render_template("login_user.html")

def logout_user():
    """Déconnecte un utilisateur classique."""
    session.pop("user_id", None)
    return redirect("/login-user")

# --------------------------------------------------------------------------------
# CONTRÔLE D'ACCÈS : DÉCORATEURS
# --------------------------------------------------------------------------------

def admin_required(f):
    """Protection des routes nécessitant une session administrateur."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def superadmin_required(f):
    """Protection des routes réservées au super admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("admin_role") != "super":
            session["flash_error"] = "Accès refusé : seuls les super admin peuvent effectuer cette action."
            return redirect("/admin?section=users")
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    """Protection des routes utilisateur nécessitant d'être connecté au chatbot."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login-user")
        return f(*args, **kwargs)
    return decorated

# --------------------------------------------------------------------------------
# GESTION UTILISATEURS : AJOUT, SUPPRESSION, MODIFICATION (ADMIN)
# --------------------------------------------------------------------------------

def add_user():
    """Ajoute un utilisateur admin (via l'interface admin)."""
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role", "admin")
    if find_user(username):
        return "Utilisateur déjà existant", 400
    user = User(username=username, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    return redirect("/admin?section=users")

def delete_user():
    """Supprime un compte administrateur, sauf son propre compte."""
    username = request.form.get("username")
    if username == session.get("admin_username"):
        return "Impossible de supprimer votre propre compte.", 400
    user = find_user(username)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect("/admin?section=users")

def update_password():
    """Modifie le mot de passe d'un compte administrateur."""
    username = request.form.get("username")
    new_password = request.form.get("password")
    user = find_user(username)
    if user:
        user.password = new_password
        db.session.commit()
    return redirect("/admin?section=users")

# --------------------------------------------------------------------------------
# AFFICHAGE PARTIEL DU TABLEAU UTILISATEURS
# --------------------------------------------------------------------------------

def render_users_table():
    """Génère le tableau HTML partiel des utilisateurs pour l'admin."""
    users = load_users()
    return render_template("partials/users_table.html", users=users)
