Développement d'un Chat Bot de Génération de Courriers ou de Mails 

Objectif 

Développer une application web utilisant une Intelligence Artificielle générative hébergée en local, capable de générer des mails et des courriers en fonction de contextes particuliers et de modèles. 

🔹 Une application web complète a été développée : interface utilisateur, backend Flask. 

Moteur IA 

Installation d'un moteur IA en local sur une machine virtuelle (Environnement Proxmox) 

🔹 Moteur IA local (Ollama : mannix/hermes-3-llama-3.1-8b) pour générer des emails. 

 🔹 Mais actuellement j'utilise qwen2.5:0.5b pour des tests plus rapides en dépit de la qualité de génération. 

Base de Données 

Création d'une base de données (Prompts, logs) 

🔹 Base de données SQLite implémentée avec SQLAlchemy : 

Table User : gestion des comptes administrateurs (username, password, role) 

Table ChatLog : historique des conversations (user_id, sender, message, timestamp) 

🔹 Stockage des prompts dans prompts.json 

 

API Backend 

Développement d'une API en Python pour la gestion du moteur IA (Paramétrage, Prompts/Réponses, Gestion des erreurs, Logs) 

🔹 Le backend de l'application repose sur deux éléments principaux situés dans : 

 jarvis@Jarvis:/opt/chatbot-docker/backend/ 

Le dossier logic représente l'API backend. Il contient la logique liée au moteur d'intelligence artificielle : 

Le paramétrage 

La gestion des prompts et des réponses 

La gestion des erreurs 

Et le fichier app.py : 

Ce fichier contient la logique Flask. Il permet : 

D'afficher les pages HTML via différentes routes, la page principale étant index.html 

De définir des routes supplémentaires accessibles via URL (ex. : /start) qui permettent au JavaScript d'interagir dynamiquement avec logic.py. Ces routes ne retournent pas de page HTML directement mais permettent de charger des contenus au démarrage ou en action utilisateur. 

🔹 L'API communique avec le moteur Ollama via des appels HTTP (API REST). 

 La fonction ollama_chat envoie les prompts et récupère les réponses du modèle local. 

Frontend 

Développement d'une interface utilisateur pour l'exploitation du chatbot (Sélection du type de document, formulaire contextuel, génération du texte, copie de la réponse) 

🔹 HTML/CSS assurent l'affichage de l'interface. 

 JavaScript gère les interactions dynamiques avec le backend, comme l'affichage des messages, la génération des formulaires et l'envoi des requêtes vers l'API Flask. 

Frontend Admin 

Développement d'une interface utilisateur pour la gestion des prompts (formulaires) et consultation des logs 

🔹 Interface d'administration implémentée avec : 

Gestion des utilisateurs (admin/superadmin) 

Authentification sécurisée 

Interface de gestion des prompts 

Visualisation des logs de conversation 

Structure 

Serveur Ubuntu : 

XXX.XXX.XXX.XXX

🔹 Tous les services sont hébergés sur ce serveur via Docker : 

backend Flask 

frontend statique 

serveur Nginx 

moteur IA Ollama 

Moteur IA 

🔹 Déployé dans un conteneur Docker via l'image ollama/ollama, modèle utilisé : qwen2.5:0.5b. 

API Backend 

🔹 Backend Python (Flask + Gunicorn), contenu dans un conteneur chatbot-backend. 

 Expose des routes pour l'interface et la génération. 

Base de Données 

🔹 SQLite avec SQLAlchemy, stockée localement dans le conteneur backend 

Portainer 

Frontend 

🔹 Fichiers HTML, CSS et JS statiques servis par Nginx depuis nginx/www. 

 Interface utilisateur principale. 

Évolutions Possibles 

Connexion SSO (AD) à l'interface web 

Historique de génération consultable 

Génération de documents (.doc, .xls) selon des modèles 

Amélioration de la sécurité (hachage des mots de passe) 

 

 
