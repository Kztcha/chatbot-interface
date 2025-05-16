/**
 * Gestion spécifique de la page des prompts
 * Ce module gère l'interface d'administration des prompts et des types d'emails :
 * - Création et suppression des types d'emails
 * - Gestion des champs de formulaire pour chaque type
 * - Édition des prompts associés à chaque type
 * - Mise à jour en temps réel de l'interface
 */

// Données initiales stockées en mémoire
// Ces données sont injectées par le template et mises à jour dynamiquement
let currentType = null;

/**
 * Gestion du sélecteur de type d'email
 * - Met à jour le type courant
 * - Affiche/masque les données associées
 * - Gère l'affichage du bouton de suppression
 */
document.getElementById('type-select').addEventListener('change', function(e) {
    currentType = e.target.value;
    if (currentType) {
        showTypeData(currentType);
        document.getElementById('delete-type-btn').style.display = 'inline-block';
    } else {
        hideAllContainers();
        document.getElementById('delete-type-btn').style.display = 'none';
    }
});

/**
 * Affiche les données d'un type d'email sélectionné
 * @param {string} type - Le nom du type à afficher
 * - Affiche la liste des champs du formulaire
 * - Affiche le prompt associé
 * - Met à jour l'interface utilisateur
 */
function showTypeData(type) {
    // Affiche les champs
    const fieldList = document.getElementById('field-list');
    fieldList.innerHTML = '';
    promptsData.form_fields[type].forEach(function(field) {
        fieldList.appendChild(createFieldElement(field));
    });
    document.getElementById('fields-container').style.display = 'block';

    // Affiche le prompt
    document.getElementById('prompt-text').value = promptsData.prompts[type];
    document.getElementById('prompt-container').style.display = 'block';
}

/**
 * Gestion des types d'emails
 * Fonctions pour l'ajout et la suppression des types
 */

/**
 * Affiche le formulaire d'ajout de type
 */
function showAddTypeForm() {
    showAddForm('add-type-form');
}

/**
 * Cache le formulaire d'ajout de type
 */
function hideAddTypeForm() {
    hideAddForm('add-type-form');
}

/**
 * Ajoute un nouveau type d'email
 * - Vérifie les données saisies
 * - Envoie la requête au serveur
 * - Met à jour l'interface et les données en mémoire
 * - Sélectionne automatiquement le nouveau type
 */
function addType() {
    const typeName = document.getElementById('new-type-name').value.trim();
    if (!typeName) {
        showMessage('Le nom du type est requis', 'error');
        return;
    }

    const data = new URLSearchParams({ type_name: typeName });
    fetch('/admin/type/add', { method: 'POST', body: data })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                hideAddTypeForm();
                
                // Ajoute le nouveau type au menu déroulant
                const select = document.getElementById('type-select');
                const option = document.createElement('option');
                option.value = typeName;
                option.textContent = typeName;
                select.appendChild(option);
                
                // Met à jour les données en mémoire
                promptsData.types.push(typeName);
                promptsData.form_fields[typeName] = [];
                promptsData.prompts[typeName] = "";
                
                // Sélectionne le nouveau type
                select.value = typeName;
                showTypeData(typeName);
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(err => showMessage(err, 'error'));
}

/**
 * Gestion des champs de formulaire
 * Fonctions pour l'ajout et la suppression des champs
 */

/**
 * Affiche le formulaire d'ajout de champ
 */
function showAddFieldForm() {
    showAddForm('add-field-form');
}

/**
 * Cache le formulaire d'ajout de champ
 */
function hideAddFieldForm() {
    hideAddForm('add-field-form');
}

/**
 * Ajoute un nouveau champ au type courant
 * - Vérifie les données saisies
 * - Envoie la requête au serveur
 * - Met à jour l'interface et les données en mémoire
 */
function addField() {
    const fieldId = document.getElementById('field-id').value.trim();
    const fieldLabel = document.getElementById('field-label').value.trim();
    
    if (!fieldId || !fieldLabel) {
        showMessage('Tous les champs sont requis', 'error');
        return;
    }

    const data = new URLSearchParams({
        type_name: currentType,
        field_id: fieldId,
        field_label: fieldLabel,
        field_type: 'text'
    });

    fetch('/admin/field/add', { method: 'POST', body: data })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                hideAddFieldForm();
                
                // Ajoute le nouveau champ à la liste
                const newField = {
                    id: fieldId,
                    label: fieldLabel,
                    type: 'text'
                };
                promptsData.form_fields[currentType].push(newField);
                
                // Met à jour l'affichage
                const fieldList = document.getElementById('field-list');
                fieldList.appendChild(createFieldElement(newField));
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(err => showMessage(err, 'error'));
}

/**
 * Supprime un champ du type courant
 * @param {string} fieldId - L'identifiant du champ à supprimer
 * - Demande confirmation
 * - Envoie la requête au serveur
 * - Met à jour l'interface et les données en mémoire
 */
function deleteField(fieldId) {
    if (!confirmDelete('Êtes-vous sûr de vouloir supprimer ce champ ?')) {
        return;
    }

    const data = new URLSearchParams({
        type_name: currentType,
        field_id: fieldId
    });

    fetch('/admin/field/delete', { method: 'POST', body: data })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                
                // Supprime le champ des données en mémoire
                promptsData.form_fields[currentType] = promptsData.form_fields[currentType].filter(
                    f => f.id !== fieldId
                );
                
                // Met à jour l'affichage
                const fieldList = document.getElementById('field-list');
                const fieldElement = fieldList.querySelector(`[data-field-id="${fieldId}"]`);
                if (fieldElement) {
                    fieldElement.remove();
                }
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(err => showMessage(err, 'error'));
}

/**
 * Gestion des prompts
 * Fonctions pour la mise à jour des prompts
 */

/**
 * Met à jour le prompt du type courant
 * - Vérifie que le prompt n'est pas vide
 * - Envoie la requête au serveur
 * - Met à jour les données en mémoire
 */
function updatePrompt() {
    const promptText = document.getElementById('prompt-text').value.trim();
    if (!promptText) {
        showMessage('Le prompt ne peut pas être vide', 'error');
        return;
    }

    const data = new URLSearchParams({
        type_name: currentType,
        prompt_text: promptText
    });

    fetch('/admin/prompt/update', { method: 'POST', body: data })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(err => showMessage(err, 'error'));
}

/**
 * Supprime le type d'email courant
 * - Vérifie qu'un type est sélectionné
 * - Demande confirmation
 * - Envoie la requête au serveur
 * - Met à jour l'interface et les données en mémoire
 * - Réinitialise l'interface
 */
function deleteCurrentType() {
    if (!currentType) return;
    
    if (!confirmDelete(`Êtes-vous sûr de vouloir supprimer le type "${currentType}" ? Cette action est irréversible.`)) {
        return;
    }

    const data = new URLSearchParams({ type_name: currentType });
    fetch('/admin/type/delete', { method: 'POST', body: data })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                
                // Supprime le type des données en mémoire
                promptsData.types = promptsData.types.filter(t => t !== currentType);
                delete promptsData.form_fields[currentType];
                delete promptsData.prompts[currentType];
                
                // Met à jour l'interface
                const select = document.getElementById('type-select');
                const option = select.querySelector(`option[value="${currentType}"]`);
                if (option) {
                    option.remove();
                }
                
                // Réinitialise l'interface
                currentType = null;
                select.value = '';
                hideAllContainers();
                document.getElementById('delete-type-btn').style.display = 'none';
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(err => showMessage(err, 'error'));
} 