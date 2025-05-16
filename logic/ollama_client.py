"""
ollama_client.py
--------------------------------------------------------------------------------
Interface de communication avec le modèle de langage Ollama.

Responsabilités :
1. Communication avec l'API Ollama :
   - Formatage des requêtes selon l'API chat/completions
   - Gestion des prompts utilisateur
   - Traitement des réponses

2. Configuration :
   - Utilise shared.OLLAMA_URL pour l'endpoint de l'API
   - Utilise shared.MODEL_NAME pour le modèle à utiliser

3. Format des messages :
   - User : Prompt principal avec les instructions
   - Assistant : Réponse générée par le modèle

4. Gestion des erreurs :
   - Validation des réponses HTTP
   - Nettoyage des prompts et réponses
   - Levée d'exceptions en cas d'erreur API
"""

import requests
import logic.shared as shared
import json

# --------------------------------------------------------------------------------
# APPEL AU MODÈLE OLLAMA
# --------------------------------------------------------------------------------

def ollama_chat(prompt: str) -> str:
    """
    Envoie une requête au modèle Ollama et retourne sa réponse.

    Le flux de traitement est le suivant :
    1. Préparation du message utilisateur
    2. Envoi de la requête à l'API Ollama
    3. Validation et extraction de la réponse
    4. Nettoyage et renvoi du texte généré

    Args:
        prompt (str): Le texte du prompt principal

    Returns:
        str: Le texte généré par le modèle, nettoyé des espaces

    Raises:
        requests.exceptions.RequestException: En cas d'erreur de communication
        ValueError: Si le prompt est vide ou invalide
    """
    # Validation des entrées
    if not prompt or not prompt.strip():
        raise ValueError("Le prompt ne peut pas être vide")

    # Préparation de la requête
    payload = {
        "model": shared.MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }

    print(f"Envoi de la requête à Ollama ({shared.OLLAMA_URL})")
    print(f"Modèle utilisé: {shared.MODEL_NAME}")
    print(f"Prompt: {prompt}")
    
    try:
        # Envoi de la requête à l'API avec stream=True
        response = requests.post(
            f"{shared.OLLAMA_URL}/api/chat",
            json=payload,
            stream=True  # Active le streaming
        )
        
        # Vérification du statut HTTP
        response.raise_for_status()
        
        # Accumulation de la réponse complète
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    # Décode chaque ligne JSON
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        content = chunk["message"]["content"]
                        full_response += content
                except json.JSONDecodeError as e:
                    print(f"Erreur de décodage JSON pour la ligne: {line}")
                    continue
        
        # Nettoyage et renvoi de la réponse complète
        return full_response.strip()
        
    except requests.exceptions.ConnectionError as e:
        print(f"Erreur de connexion à Ollama: {str(e)}")
        raise ValueError("Impossible de se connecter au serveur Ollama")
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP: {str(e)}")
        raise ValueError(f"Erreur de communication avec Ollama: {str(e)}")
        
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        print(f"Type d'erreur: {type(e)}")
        raise ValueError(f"Erreur inattendue lors de la génération: {str(e)}")
