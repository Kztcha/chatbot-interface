/**
 * ui.js - Gestion des effets visuels et de l'interface utilisateur
 * Ce module fournit les fonctionnalités de base pour l'interface utilisateur :
 * - Système de particules en arrière-plan
 * - Gestion des messages dans le chat
 * - Indicateur de chargement
 * - Initialisation de l'interface
 */

/**
 * Crée une particule flottante avec animation
 * La particule est une fleur qui monte depuis le bas de l'écran
 * et disparaît après 8 secondes
 */
function createParticle() {
  const particle = document.createElement('div');
  particle.classList.add('particle');
  particle.innerText = '❀';
  particle.style.left = Math.random() * window.innerWidth + 'px';
  particle.style.top = '-50px';
  particle.style.fontSize = (Math.random() * 10 + 15) + 'px';
  document.body.appendChild(particle);
  setTimeout(() => particle.remove(), 8000);
}

/**
 * Ajoute un nouveau message dans la zone de chat
 * @param {string} text - Le contenu du message
 * @param {string} sender - L'expéditeur ('user' ou 'bot')
 */
function appendMessage(text, sender) {
  const chatBox = document.getElementById("chat-box");
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.textContent = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Contrôle l'affichage de l'indicateur de chargement
 * @param {boolean} show - true pour afficher, false pour masquer
 */
function showLoading(show = true) {
  const loadingEl = document.getElementById("loading");
  loadingEl.style.display = show ? "block" : "none";
}

/**
 * Initialisation de l'interface utilisateur
 * Démarre le système de particules dès le chargement de la page
 */
document.addEventListener("DOMContentLoaded", () => {
  // Démarrage des particules
  setInterval(createParticle, 300);
});

// Export des fonctions pour utilisation dans d'autres modules
window.UI = {
  appendMessage,
  showLoading,
  createParticle
}; 