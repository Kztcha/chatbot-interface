/**
 * Fonctions utilitaires communes aux pages d'administration
 * Ce module fournit des fonctions réutilisables pour :
 * - L'affichage des messages de retour
 * - La gestion des formulaires
 * - La confirmation des actions de suppression
 * - La création et gestion des champs de formulaire
 * - La gestion des conteneurs de formulaire
 */

/**
 * Affiche un message temporaire dans le conteneur de messages
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de message ('success' ou 'error')
 * Le message disparaît automatiquement après 5 secondes
 */
function showMessage(message, type) {
    const container = document.getElementById('msg-container');
    const div = document.createElement('div');
    div.className = `msg ${type}`;
    div.textContent = message;
    container.appendChild(div);
    setTimeout(() => div.remove(), 5000);
}

/**
 * Gère la soumission d'un formulaire avec gestion des erreurs
 * @param {HTMLFormElement} form - Le formulaire à gérer
 * @param {string} url - L'URL de l'endpoint API
 * @param {Function} successCallback - Fonction appelée en cas de succès
 * - Empêche la soumission par défaut du formulaire
 * - Envoie les données en POST
 * - Affiche les messages de succès/erreur
 * - Exécute le callback de succès si fourni
 */
function handleFormSubmit(form, url, successCallback) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const data = new URLSearchParams(new FormData(form));
        
        fetch(url, { method: 'POST', body: data })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    if (successCallback) successCallback(data);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(err => showMessage(err, 'error'));
    });
}

/**
 * Demande confirmation avant une action de suppression
 * @param {string} message - Message de confirmation personnalisé
 * @returns {boolean} - true si l'utilisateur confirme, false sinon
 */
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

/**
 * Crée un élément DOM pour représenter un champ de formulaire
 * @param {Object} field - Les données du champ
 * @param {string} field.id - Identifiant unique du champ
 * @param {string} field.label - Libellé affiché à l'utilisateur
 * @param {string} field.type - Type de champ (text, select, etc.)
 * @returns {HTMLElement} - L'élément DOM créé
 */
function createFieldElement(field) {
    const div = document.createElement('div');
    div.className = 'field-item';
    div.setAttribute('data-field-id', field.id);
    div.innerHTML = `
        <div class="field-info">
            <strong>${field.label}</strong>
            <br>
            <small>ID: ${field.id} | Type: ${field.type}</small>
        </div>
        <div class="field-actions">
            <button onclick="deleteField('${field.id}')" class="delete">Supprimer</button>
        </div>
    `;
    return div;
}

/**
 * Cache tous les conteneurs de formulaire
 * Utilisé pour nettoyer l'interface avant d'afficher un nouveau formulaire
 */
function hideAllContainers() {
    const containers = document.querySelectorAll('.form-container');
    containers.forEach(container => {
        container.style.display = 'none';
    });
}

/**
 * Affiche un formulaire d'ajout spécifique
 * @param {string} formId - L'ID du formulaire à afficher
 */
function showAddForm(formId) {
    document.getElementById(formId).style.display = 'block';
}

/**
 * Cache un formulaire d'ajout et réinitialise ses champs
 * @param {string} formId - L'ID du formulaire à cacher
 */
function hideAddForm(formId) {
    const form = document.getElementById(formId);
    form.style.display = 'none';
    form.reset();
} 