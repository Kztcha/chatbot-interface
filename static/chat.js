/**
 * chat.js - Logique principale du chat
 * Ce fichier gère toute la logique d'interaction du chat, incluant :
 * - L'initialisation des composants
 * - La gestion des messages
 * - Le rendu des formulaires dynamiques
 * - La communication avec le backend
 */

document.addEventListener("DOMContentLoaded", () => {
  // Éléments DOM principaux
  const chatBox       = document.getElementById("chat-box");      // Conteneur des messages
  const formContainer = document.getElementById("form-container"); // Zone du formulaire dynamique
  const loadingEl     = document.getElementById("loading");        // Indicateur de chargement
  const headerActions = document.getElementById("header-actions"); // Boutons d'action (regen, restart)

  /**
   * Ajoute un nouveau message dans la zone de chat
   * @param {string} text - Le contenu du message
   * @param {string} sender - L'expéditeur ('user' ou 'bot')
   * - Crée un nouvel élément div avec les classes appropriées
   * - Ajoute le message à la fin de la conversation
   * - Fait défiler automatiquement vers le bas
   */
  function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  /**
   * Charge les types d'emails à jour depuis le serveur
   * et met à jour le formulaire si nécessaire
   * - Récupère la liste des types via l'API
   * - Met à jour le select tout en préservant la sélection actuelle
   * - Gère les erreurs de manière silencieuse
   */
  function reloadEmailTypes() {
    return fetch("/get_types")
      .then(res => res.json())
      .then(data => {
        const form = document.getElementById("dynamic-form");
        if (form) {
          const select = form.querySelector('select[id="type"]');
          if (select) {
            // Sauvegarde la valeur actuelle
            const currentValue = select.value;
            // Vide et recrée les options
            select.innerHTML = "";
            data.types.forEach(type => {
              const opt = document.createElement("option");
              opt.value = type;
              opt.textContent = type;
              select.appendChild(opt);
            });
            // Restaure la valeur si elle existe toujours
            if (data.types.includes(currentValue)) {
              select.value = currentValue;
            }
          }
        }
      })
      .catch(console.error);
  }

  /**
   * Génère un formulaire dynamique basé sur les champs spécifiés
   * @param {Array} fields - Liste des champs à afficher
   * - Crée un formulaire avec les champs spécifiés
   * - Gère différents types de champs (text, select)
   * - Ajoute la gestion des événements de soumission
   */
  function renderForm(fields) {
    formContainer.innerHTML = "";
    const form = document.createElement("form");
    form.id = "dynamic-form";

    fields.forEach(f => {
      const label = document.createElement("label");
      label.htmlFor = f.id;
      label.textContent = f.label;
      form.appendChild(label);

      let input;
      if (f.type === "select") {
        input = document.createElement("select");
        input.required = true;
        // Pour le select de type, on recharge les types à jour
        if (f.id === "type") {
          reloadEmailTypes();
        }
        f.options.forEach(opt => {
          const o = document.createElement("option");
          o.value = opt;
          o.textContent = opt;
          input.appendChild(o);
        });
      } else {
        input = document.createElement("input");
        input.type = "text";
        input.required = true;
      }

      input.id = f.id;
      input.name = f.id;
      form.appendChild(input);
      form.appendChild(document.createElement("br"));
    });

    const submit = document.createElement("button");
    submit.type = "submit";
    submit.textContent = "Envoyer";
    form.appendChild(submit);

    formContainer.appendChild(form);

    // Gestion de la soumission du formulaire
    form.addEventListener("submit", e => {
      e.preventDefault();
      const data = {};
      fields.forEach(f => {
        data[f.id] = document.getElementById(f.id).value.trim();
      });

      // Si c'est un formulaire de détails (ni type, ni dest/obj)
      if (fields.length && !["type", "dest", "obj"].includes(fields[0].id)) {
        sendData({ details: data });
      } else {
        sendData(data);
      }
    });
  }

  /**
   * Ajoute les boutons d'action post-génération
   * (Recommencer et Régénérer)
   * - Crée les boutons avec leurs gestionnaires d'événements
   * - Gère les états de chargement
   * - Met à jour l'interface après chaque action
   */
  function renderPostGenerationOptions() {
    headerActions.innerHTML = "";

    const btnRestart = document.createElement("button");
    btnRestart.textContent = "Recommencer";
    btnRestart.onclick = () => {
      headerActions.innerHTML = "";
      UI.showLoading(true);

      fetch("/start")
        .then(res => res.json())
        .then(res => {
          UI.appendMessage("🟢 Nouvelle conversation démarrée.", "bot");
          if (res.fields) {
            Forms.renderForm(res.fields);
          }
        })
        .catch(err => {
          UI.appendMessage("❌ Erreur lors du redémarrage.", "bot");
        })
        .finally(() => {
          UI.showLoading(false);
        });
    };

    const btnRegenerate = document.createElement("button");
    btnRegenerate.textContent = "Régénérer";
    btnRegenerate.onclick = () => {
      headerActions.innerHTML = "";
      UI.showLoading(true);

      fetch("/regen")
        .then(res => res.json())
        .then(res => {
          UI.appendMessage("🔁 Nouvelle version générée :", "bot");
          UI.appendMessage(res.bot, "bot");
          renderPostGenerationOptions();
        })
        .catch(err => {
          UI.appendMessage("❌ Erreur de régénération.", "bot");
        })
        .finally(() => {
          UI.showLoading(false);
        });
    };

    headerActions.appendChild(btnRestart);
    headerActions.appendChild(btnRegenerate);
  }

  /**
   * Envoie les données au backend et gère la réponse
   * @param {Object} payload - Les données à envoyer
   * - Affiche le message de l'utilisateur
   * - Envoie les données au serveur
   * - Gère la réponse (nouveau formulaire ou fin de conversation)
   * - Gère les erreurs réseau
   */
  function sendData(payload) {
    UI.showLoading(true);
    UI.appendMessage(
      (payload.details ? Object.values(payload.details) : Object.values(payload)).join(" | "),
      "user"
    );
    Forms.clearForm();

    fetch("/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(res => {
      UI.showLoading(false);

      const questions = res.fields;
      UI.appendMessage(res.bot, "bot");
      if (questions) {
        Forms.renderForm(questions);
      } else if (res.end) {
        renderPostGenerationOptions();
      }
    })
    .catch(err => {
      console.error(err);
      UI.showLoading(false);
      UI.appendMessage("Erreur réseau, veuillez réessayer.", "bot");
    });
  }

  // Initialisation de la conversation au chargement de la page
  fetch("/start")
    .then(res => res.json())
    .then(res => {
      UI.appendMessage(res.bot, "bot");
      if (res.fields) {
        Forms.renderForm(res.fields);
      }
    })
    .catch(err => {
      console.error(err);
      UI.appendMessage("Impossible de démarrer la conversation.", "bot");
    });

  // Export des fonctions pour les autres modules
  window.Chat = {
    sendData
  };

  // Ajout du bouton repli/dépli
  const toggleBtn = document.getElementById("toggle-header");
  const headerContent = document.getElementById("header-content");
  if (toggleBtn && headerContent) {
    let isVisible = true;
    toggleBtn.addEventListener("click", () => {
      isVisible = !isVisible;
      headerContent.style.display = isVisible ? "flex" : "none";
      toggleBtn.textContent = isVisible ? "▲" : "▼";
    });
  }
});
