"""
chat.py
--------------------------------------------------------------------------------
Gère toutes les étapes du chatbot utilisateur et le flux de conversation.

Fonctionnement :
1. Étapes de la conversation (stockées dans session["step"]) :
   - STEP_TYPE : Sélection du type d'email
   - STEP_INFO : Saisie du destinataire et de l'objet
   - STEP_PRECISIONS : Questions supplémentaires selon le type
   - STEP_GENERATION : Génération du document final

2. Stockage des données :
   - Toutes les réponses sont conservées dans session["answers"]
   - Format : {type, dest, obj, details}
   - Historique sauvegardé en base de données via ChatLog

3. Sécurité et validation :
   - Vérification des entrées à chaque étape
   - Protection contre les sauts d'étapes
   - Nettoyage des données utilisateur

4. Intégration avec Ollama :
   - Génération du contenu final uniquement
   - Possibilité de régénération en cas d'erreur
"""

import json
from flask import render_template, request, jsonify, session, redirect
import logic.shared as shared
from logic.shared import STEP_TYPE, STEP_INFO, STEP_PRECISIONS, STEP_GENERATION
from logic.ollama_client import ollama_chat
from logic.database import db
from logic.models import ChatLog
from logic.users import find_user_by_id, find_user

# --------------------------------------------------------------------------------
# ROUTES UTILISATEUR : CHATBOT
# --------------------------------------------------------------------------------

def index():
    """
    Point d'entrée du chatbot :
    - Redirige vers la page de connexion si l'utilisateur n'est pas authentifié
    - Réinitialise la session de chat (pas la session globale) pour démarrer une nouvelle conversation
    - Affiche la page d'accueil
    """
    if not session.get("user_id") and not session.get("admin_logged_in"):
        return redirect("/login-user")
    
    # Ne pas supprimer la session globale, uniquement les variables du chatbot
    session.pop("step", None)
    session.pop("answers", None)
    return render_template("index.html")

def start():
    """
    Initialise une nouvelle conversation :
    - Définit l'étape initiale (choix du type)
    - Prépare le dictionnaire des réponses
    - Retourne le premier message et les champs du formulaire
    """
    try:
        prompts = shared.get_prompts()
        session["step"] = STEP_TYPE
        session["answers"] = {}
        return jsonify({
            "bot": prompts["select_type"],
            "fields": [{"id": "type", "label": "Type d'e-mail", "type": "select", "options": prompts["types"]}],
            "end": False
        })
    except Exception as e:
        return jsonify({
            "bot": "Une erreur est survenue lors du démarrage de la conversation.",
            "error": str(e),
            "end": True
        })

def handle_message():
    """
    Gère chaque message de l'utilisateur selon l'étape actuelle.
    Enregistre également l'historique dans la base de données.
    
    Flux de traitement :
    1. Récupère l'étape actuelle et les réponses précédentes
    2. Valide les données reçues selon l'étape
    3. Met à jour la session avec les nouvelles données
    4. Retourne la réponse appropriée et les champs suivants
    
    Retourne toujours un objet JSON avec :
    - bot : message du chatbot
    - fields : champs du formulaire à afficher (optionnel)
    - end : True si c'est la fin de la conversation
    """
    try:
        step = session.get("step", STEP_TYPE)
        answers = session.get("answers", {})
        prompts = shared.get_prompts()
        
        # Vérification que request.json est bien présent
        if not request.is_json:
            return jsonify({
                "bot": "Erreur : Les données doivent être envoyées au format JSON",
                "end": False
            })
            
        data = request.json or {}
        
        # Récupère l'utilisateur connecté (admin ou user)
        user_id = None
        if session.get("admin_logged_in"):
            user = find_user(session.get("admin_username"))
            if user:
                user_id = user.id
        elif session.get("user_id"):
            user = find_user_by_id(session.get("user_id"))
            if user:
                user_id = user.id

        # Enregistre le message de l'utilisateur
        if data and user_id:
            chat_log = ChatLog(
                user_id=user_id,
                sender='user',
                message=json.dumps(data, ensure_ascii=False)
            )
            db.session.add(chat_log)
            db.session.commit()

        # Étapes du chatbot
        if step == STEP_TYPE:
            if "type" not in data:
                return jsonify({
                    "bot": prompts["select_type"],
                    "fields": [{"id": "type", "label": "Type d'e-mail", "type": "select", "options": prompts["types"]}],
                    "end": False
                })
                
            email_type = data["type"]
            if email_type not in prompts["types"]:
                return jsonify({
                    "bot": "Type d'e-mail non valide. Veuillez choisir parmi : " + ", ".join(prompts["types"]),
                    "fields": [{"id": "type", "label": "Type d'e-mail", "type": "select", "options": prompts["types"]}],
                    "end": False
                })
                
            answers["type"] = email_type
            session["answers"] = answers
            session["step"] = STEP_INFO
            return jsonify({
                "bot": prompts["initial"],
                "fields": [
                    {"id": "dest", "label": "Destinataire", "type": "text"},
                    {"id": "obj", "label": "Objet", "type": "text"}
                ],
                "end": False
            })

        if step == STEP_INFO:
            dest = data.get("dest", "").strip()
            obj = data.get("obj", "").strip()
            if not dest or not obj:
                return jsonify({"bot": "Merci de remplir les deux champs.", "end": False})
            answers.update(dest=dest, obj=obj)
            session["answers"] = answers
            session["step"] = STEP_PRECISIONS

            email_type = answers["type"]
            fields = prompts["form_fields"].get(email_type, [])

            return jsonify({
                "bot": "Merci de compléter les informations suivantes :",
                "fields": fields,
                "end": False
            })

        if step == STEP_PRECISIONS:
            details = data.get("details", {})
            if not isinstance(details, dict) or not details:
                return jsonify({"bot": "Merci de répondre à toutes les questions.", "end": False})
            answers["details"] = details
            session["answers"] = answers
            session["step"] = STEP_GENERATION
            return _generate_doc(answers, user_id)

        return jsonify({"bot": "Erreur interne : étape inconnue.", "end": True})
        
    except Exception as e:
        print(f"Erreur dans handle_message: {str(e)}")
        return jsonify({
            "bot": "Une erreur est survenue lors du traitement de votre message. Veuillez réessayer.",
            "error": str(e),
            "end": False
        })

def _generate_doc(ans: dict, user_id=None):
    """
    Génère le document final en utilisant Ollama.
    
    Args:
        ans (dict): Dictionnaire contenant toutes les réponses de l'utilisateur
        user_id (int|None): Identifiant de l'utilisateur pour sauvegarde

    Returns:
        JSON avec le contenu généré et end=True
    """
    try:
        email_type = ans["type"]
        prompts = shared.get_prompts()
        
        if email_type not in prompts["types"]:
            return jsonify({
                "bot": "Ce type d'email n'est plus disponible. Veuillez recommencer avec un nouveau type.",
                "end": True
            })
            
        prompt = prompts["prompts"][email_type].format(
            dest=ans["dest"],
            obj=ans["obj"],
            **ans["details"]
        )
        content = ollama_chat(prompt)

        # Log du message généré par le bot
        if user_id:
            chat_log = ChatLog(
                user_id=user_id,
                sender='bot',
                message=content
            )
            db.session.add(chat_log)
            db.session.commit()

        return jsonify({"bot": content, "end": True})
    except Exception as e:
        return jsonify({
            "bot": "Une erreur est survenue lors de la génération du document.",
            "error": str(e),
            "end": True
        })

def regenerate():
    """
    Régénère le document avec les mêmes données.
    Utile en cas de résultat non satisfaisant.
    """
    try:
        answers = session.get("answers")
        if not answers:
            return jsonify({"bot": "Impossible de régénérer : aucune donnée disponible.", "end": True})
        
        prompts = shared.get_prompts()
        email_type = answers.get("type")
        if not email_type or email_type not in prompts["types"]:
            return jsonify({
                "bot": "Ce type d'email n'est plus disponible. Veuillez recommencer avec un nouveau type.",
                "end": True
            })

        user_id = None
        if session.get("admin_logged_in"):
            user = find_user(session.get("admin_username"))
            if user:
                user_id = user.id
        elif session.get("user_id"):
            user = find_user_by_id(session.get("user_id"))
            if user:
                user_id = user.id

        return _generate_doc(answers, user_id)
    except Exception as e:
        return jsonify({
            "bot": "Une erreur est survenue lors de la régénération du document.",
            "error": str(e),
            "end": True
        })

def get_types():
    """
    Retourne la liste à jour des types d'emails disponibles.
    Recharge les prompts depuis le fichier pour avoir les dernières modifications.
    """
    shared.load_prompts()
    return jsonify({"types": shared.get_prompts()["types"]})
