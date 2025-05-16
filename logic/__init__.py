"""
__init__.py
--------------------------------------------------------------------------------
Point d'entrée du module logic qui expose l'API interne vers app.py.

Organisation du module :
1. Interface utilisateur (chat.py) :
   - index : Page d'accueil
   - start : Démarrage d'une conversation
   - handle_message : Traitement des messages
   - regenerate : Régénération de réponse

2. Interface admin (admin_ui.py) :
   - admin_prompts_page : Gestion des prompts
   - admin_users_page : Gestion des utilisateurs
   - save_prompts : Sauvegarde des modifications
   - add_email_type : Ajout d'un type d'email
   - delete_email_type : Suppression d'un type d'email
   - add_form_field : Ajout d'un champ de formulaire
   - delete_form_field : Suppression d'un champ
   - update_prompt : Mise à jour d'un prompt

3. Authentification (users.py) :
   - login_page, logout : Gestion des sessions
   - admin_required : Protection des routes admin
   - superadmin_required : Protection des actions sensibles
   - Gestion des comptes : add_user, delete_user, update_password
   - Utilitaires : load_users, render_users_table

4. Configuration (shared.py) :
   - SECRET_KEY : Clé de chiffrement des sessions
   - Autres constantes et configurations partagées

Note d'architecture :
Ce module suit une architecture en couches :
- Interface (app.py) : Routage HTTP
- Logique (logic/) : Traitement métier
- Données (models.py, database.py) : Persistance
"""

# --------------------------------------------------------------------------------
# INTERFACE UTILISATEUR (CHATBOT)
# --------------------------------------------------------------------------------

from logic.chat import (
    index,          # GET / : Page d'accueil
    start,          # GET /start : Nouvelle conversation
    handle_message, # POST /message : Traitement des messages
    regenerate      # GET /regen : Régénération de réponse
)

# --------------------------------------------------------------------------------
# INTERFACE ADMINISTRATEUR
# --------------------------------------------------------------------------------

from logic.admin_ui import (
    admin_prompts_page,  # GET /admin : Interface prompts
    admin_users_page,    # GET /admin/users : Interface utilisateurs
    save_prompts,        # POST /admin/save : Sauvegarde des prompts
    add_email_type,      # POST /admin/type/add : Ajout d'un type
    delete_email_type,   # POST /admin/type/delete : Suppression d'un type
    add_form_field,      # POST /admin/field/add : Ajout d'un champ
    delete_form_field,   # POST /admin/field/delete : Suppression d'un champ
    update_prompt        # POST /admin/prompt/update : Mise à jour d'un prompt
)

# --------------------------------------------------------------------------------
# AUTHENTIFICATION ET GESTION UTILISATEURS
# --------------------------------------------------------------------------------

from logic.users import (
    # Authentification
    login_page,          # GET, POST /login
    logout,              # GET /logout

    # Authentification utilisateur classique
    signup_page,         # GET, POST /signup
    login_user_page,     # GET, POST /login-user
    logout_user,         # GET /logout-user

    # Décorateurs de sécurité
    admin_required,      # Vérifie la connexion admin
    superadmin_required, # Vérifie les droits superadmin

    # Gestion des comptes
    add_user,           # POST /admin/users/add
    delete_user,        # POST /admin/users/delete
    update_password,    # POST /admin/users/update

    # Utilitaires
    load_users,         # Charge la liste des utilisateurs
    render_users_table  # Génère le HTML du tableau
)

# --------------------------------------------------------------------------------
# CONFIGURATION PARTAGÉE
# --------------------------------------------------------------------------------

from logic.shared import (
    SECRET_KEY,  # Clé de chiffrement des sessions
    PROMPTS,     # Dictionnaire des prompts
    load_prompts # Fonction de chargement des prompts
)
