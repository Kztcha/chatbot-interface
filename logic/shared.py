# logic/shared.py
"""
shared.py
--------------------------------------------------------------------------------
Module de configuration et constantes partagées pour l'application.

Configuration globale :
1. Chemins et fichiers :
   - BASE_DIR : Répertoire racine du module logic/
   - PROMPTS_PATH : Chemin vers le fichier de configuration des prompts

2. Sécurité :
   - SECRET_KEY : Clé de chiffrement pour les sessions Flask
   - Configurable via la variable d'environnement FLASK_SECRET_KEY

3. Configuration Ollama :
   - OLLAMA_URL : URL du serveur Ollama (par défaut sur le réseau local)
   - MODEL_NAME : Nom du modèle à utiliser (configurable via OLLAMA_MODEL_NAME)

4. Gestion des prompts :
   - PROMPTS : Dictionnaire des prompts chargé depuis prompts.json
   - Fonctions de chargement et mise à jour
   - Structure : {
     "select_type": str,
     "types": list[str],
     "initial": str,
     "form_fields": dict,
     "prompts": dict
   }

5. États de conversation :
   - STEP_* : Constantes pour suivre l'état de la conversation
   - Progression linéaire du type à la génération
"""

import os
import json

# --------------------------------------------------------------------------------
# CONFIGURATION DES CHEMINS
# --------------------------------------------------------------------------------

# Chemin de base du module logic/
BASE_DIR = os.path.dirname(__file__)

# Chemin vers le fichier de configuration des prompts
PROMPTS_PATH = os.path.join(BASE_DIR, "../prompts.json")

# --------------------------------------------------------------------------------
# CONFIGURATION DE SÉCURITÉ
# --------------------------------------------------------------------------------

# Clé secrète pour Flask (sessions, CSRF, etc.)
# À définir via FLASK_SECRET_KEY en production
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "votre_clé_secrète_flask")

# --------------------------------------------------------------------------------
# CONFIGURATION OLLAMA
# --------------------------------------------------------------------------------

# URL du serveur Ollama (adapter selon l'environnement)
OLLAMA_URL = ""

# Modèle à utiliser (configurable via variable d'environnement)
MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "qwen2.5:0.5b")

# --------------------------------------------------------------------------------
# GESTION DES PROMPTS
# --------------------------------------------------------------------------------

# Variables globales pour stocker les prompts et le timestamp
PROMPTS = None
LAST_MTIME = 0

def should_reload_prompts():
    """Vérifie si le fichier prompts.json a été modifié depuis le dernier chargement"""
    global LAST_MTIME
    try:
        current_mtime = os.path.getmtime(PROMPTS_PATH)
        if current_mtime > LAST_MTIME:
            LAST_MTIME = current_mtime
            return True
        return False
    except Exception:
        return True

def get_prompts():
    """
    Retourne les prompts, en rechargeant si le fichier a été modifié.
    À utiliser au lieu d'accéder directement à la variable PROMPTS.
    """
    global PROMPTS
    if should_reload_prompts():
        load_prompts()
    return PROMPTS

def load_prompts():
    """
    Charge le fichier prompts.json dans la variable globale PROMPTS.
    Met aussi à jour le timestamp de dernière modification.
    
    Le fichier doit contenir un objet JSON valide avec la structure attendue :
    {
        "select_type": str,  # Message pour choisir le type d'email
        "types": list[str],  # Liste des types disponibles
        "initial": str,  # Message après choix du type
        "form_fields": dict,  # Champs supplémentaires par type
        "prompts": dict  # Templates de génération par type
    }
    
    Raises:
        FileNotFoundError: Si prompts.json n'existe pas
        json.JSONDecodeError: Si le fichier n'est pas un JSON valide
        ValueError: Si la structure n'est pas cohérente
    """
    global PROMPTS, LAST_MTIME
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        PROMPTS = json.load(f)
    LAST_MTIME = os.path.getmtime(PROMPTS_PATH)

    # Validation de la cohérence des types
    types_set = set(PROMPTS["types"])
    form_fields_set = set(PROMPTS["form_fields"].keys())
    prompts_set = set(PROMPTS["prompts"].keys())
    
    # Vérifie que tous les types ont leurs champs et prompts
    if not types_set.issubset(form_fields_set):
        missing = types_set - form_fields_set
        raise ValueError(f"Types manquants dans form_fields : {missing}")
        
    if not types_set.issubset(prompts_set):
        missing = types_set - prompts_set
        raise ValueError(f"Types manquants dans prompts : {missing}")
        
    # Supprime les types obsolètes
    for obsolete in form_fields_set - types_set:
        del PROMPTS["form_fields"][obsolete]
    for obsolete in prompts_set - types_set:
        del PROMPTS["prompts"][obsolete]

def update_prompts(new_data):
    """
    Met à jour les prompts en mémoire et sur le disque.
    Met aussi à jour le timestamp de dernière modification.
    
    Args:
        new_data (dict): Nouveau dictionnaire de prompts
            Doit avoir la même structure que le fichier prompts.json
    
    Raises:
        TypeError: Si new_data n'est pas un dictionnaire
        IOError: Si l'écriture du fichier échoue
    """
    if not isinstance(new_data, dict):
        raise TypeError("Les nouveaux prompts doivent être un dictionnaire")
    
    global PROMPTS, LAST_MTIME
    PROMPTS = new_data
    with open(PROMPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(PROMPTS, f, indent=2, ensure_ascii=False)
    LAST_MTIME = os.path.getmtime(PROMPTS_PATH)

# Chargement initial des prompts
load_prompts()

# --------------------------------------------------------------------------------
# ÉTAPES DU FLUX CONVERSATIONNEL
# --------------------------------------------------------------------------------

# Constantes pour suivre la progression de la conversation
# L'ordre est important et représente le flux linéaire
STEP_TYPE       = 0  # Choix du type d'email
STEP_INFO       = 1  # Informations de base (dest, objet)
STEP_PRECISIONS = 2  # Détails supplémentaires selon le type
STEP_GENERATION = 3  # Génération du document final
