# logic/admin_ui.py
"""
admin_ui.py
──────────────────────────────────────────────────────────────
Gère l'affichage de la page admin et la sauvegarde du fichier prompts.json :
- Affiche les sections (prompts + utilisateurs),
- Sauvegarde du fichier JSON,
- Affichage de message d'erreur si besoin.
"""

import json
from flask import request, session, redirect, render_template, jsonify
import logic.shared as shared
from logic.models import User
from logic.database import db

# ──────────────────────────────────────────────────────────────────────────────
# INTERFACE D'ADMINISTRATION
# ──────────────────────────────────────────────────────────────────────────────

def admin_prompts_page():
    """Affiche la section prompts de l'interface d'administration avec la nouvelle interface interactive."""
    # Recharge les prompts depuis le fichier à chaque affichage
    shared.load_prompts()
    
    # Structure les données pour le template
    prompts_data = {
        "types": shared.PROMPTS["types"],
        "form_fields": shared.PROMPTS["form_fields"],
        "prompts": shared.PROMPTS["prompts"]
    }
    
    return render_template("admin_prompts.html",
        prompts_data=prompts_data,
        current=session.get("admin_username")
    )

def admin_users_page():
    """Affiche uniquement la section utilisateurs de l'interface d'administration."""
    users = User.query.all()
    flash_error = session.pop("flash_error", None)
    return render_template("admin_users.html",
        users=users,
        current=session.get("admin_username"),
        error=flash_error
    )

# ──────────────────────────────────────────────────────────────────────────────
# GESTION DES TYPES D'EMAILS
# ──────────────────────────────────────────────────────────────────────────────

def add_email_type():
    """Ajoute un nouveau type d'email."""
    try:
        new_type = request.form.get("type_name")
        if not new_type:
            return jsonify({"success": False, "message": "Le nom du type est requis"})
            
        # Vérifie que le type n'existe pas déjà
        if new_type in shared.PROMPTS["types"]:
            return jsonify({"success": False, "message": "Ce type existe déjà"})
            
        # Ajoute le nouveau type
        shared.PROMPTS["types"].append(new_type)
        shared.PROMPTS["form_fields"][new_type] = []
        shared.PROMPTS["prompts"][new_type] = ""
        
        # Sauvegarde les modifications
        shared.update_prompts(shared.PROMPTS)
        
        return jsonify({
            "success": True,
            "message": f"Type '{new_type}' ajouté avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout du type : {str(e)}"
        })

def delete_email_type():
    """Supprime un type d'email existant."""
    try:
        type_name = request.form.get("type_name")
        if not type_name:
            return jsonify({"success": False, "message": "Le nom du type est requis"})
            
        # Vérifie que le type existe
        if type_name not in shared.PROMPTS["types"]:
            return jsonify({"success": False, "message": "Ce type n'existe pas"})
            
        # Supprime le type et ses données associées
        shared.PROMPTS["types"].remove(type_name)
        del shared.PROMPTS["form_fields"][type_name]
        del shared.PROMPTS["prompts"][type_name]
        
        # Sauvegarde les modifications
        shared.update_prompts(shared.PROMPTS)
        
        return jsonify({
            "success": True,
            "message": f"Type '{type_name}' supprimé avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la suppression du type : {str(e)}"
        })

# ──────────────────────────────────────────────────────────────────────────────
# GESTION DES CHAMPS DE FORMULAIRE
# ──────────────────────────────────────────────────────────────────────────────

def add_form_field():
    """Ajoute un nouveau champ à un type d'email."""
    try:
        type_name = request.form.get("type_name")
        field_id = request.form.get("field_id")
        field_label = request.form.get("field_label")
        field_type = request.form.get("field_type", "text")
        
        if not all([type_name, field_id, field_label]):
            return jsonify({"success": False, "message": "Tous les champs sont requis"})
            
        # Vérifie que le type existe
        if type_name not in shared.PROMPTS["types"]:
            return jsonify({"success": False, "message": "Ce type n'existe pas"})
            
        # Vérifie que l'ID n'est pas déjà utilisé
        if any(f["id"] == field_id for f in shared.PROMPTS["form_fields"][type_name]):
            return jsonify({"success": False, "message": "Cet ID est déjà utilisé"})
            
        # Ajoute le nouveau champ
        shared.PROMPTS["form_fields"][type_name].append({
            "id": field_id,
            "label": field_label,
            "type": field_type
        })
        
        # Sauvegarde les modifications
        shared.update_prompts(shared.PROMPTS)
        
        return jsonify({
            "success": True,
            "message": f"Champ '{field_label}' ajouté avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout du champ : {str(e)}"
        })

def delete_form_field():
    """Supprime un champ d'un type d'email."""
    try:
        type_name = request.form.get("type_name")
        field_id = request.form.get("field_id")
        
        if not all([type_name, field_id]):
            return jsonify({"success": False, "message": "Tous les champs sont requis"})
            
        # Vérifie que le type existe
        if type_name not in shared.PROMPTS["types"]:
            return jsonify({"success": False, "message": "Ce type n'existe pas"})
            
        # Trouve et supprime le champ
        fields = shared.PROMPTS["form_fields"][type_name]
        field = next((f for f in fields if f["id"] == field_id), None)
        
        if not field:
            return jsonify({"success": False, "message": "Ce champ n'existe pas"})
            
        fields.remove(field)
        
        # Sauvegarde les modifications
        shared.update_prompts(shared.PROMPTS)
        
        return jsonify({
            "success": True,
            "message": f"Champ '{field['label']}' supprimé avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la suppression du champ : {str(e)}"
        })

# ──────────────────────────────────────────────────────────────────────────────
# GESTION DES PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

def update_prompt():
    """Met à jour le prompt d'un type d'email."""
    try:
        type_name = request.form.get("type_name")
        prompt_text = request.form.get("prompt_text")
        
        if not all([type_name, prompt_text]):
            return jsonify({"success": False, "message": "Tous les champs sont requis"})
            
        # Vérifie que le type existe
        if type_name not in shared.PROMPTS["types"]:
            return jsonify({"success": False, "message": "Ce type n'existe pas"})
            
        # Met à jour le prompt
        shared.PROMPTS["prompts"][type_name] = prompt_text
        
        # Sauvegarde les modifications
        shared.update_prompts(shared.PROMPTS)
        
        return jsonify({
            "success": True,
            "message": "Prompt mis à jour avec succès"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise à jour du prompt : {str(e)}"
        })

# ──────────────────────────────────────────────────────────────────────────────
# SAUVEGARDE DU FICHIER PROMPTS.JSON
# ──────────────────────────────────────────────────────────────────────────────

def save_prompts():
    """
    Sauvegarde les modifications apportées à prompts.json.
    Fonction appelée par requête AJAX : retourne un message sans redirection.
    """
    try:
        new_data = request.form.get("prompts_json", "")
        parsed = json.loads(new_data)

        # Écriture dans le fichier
        with open(shared.PROMPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        # Recharge immédiate en mémoire
        shared.update_prompts(parsed)

        # Maintient la session active
        session.modified = True

        return "OK", 200

    except Exception as e:
        return f"Erreur lors de la sauvegarde : {e}", 400
