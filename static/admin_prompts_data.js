/**
 * Initialisation des données des prompts
 * Les données sont injectées par le template Jinja2
 * 
 * Structure des données attendues :
 * {
 *   types: [
 *     {
 *       name: string,        // Nom du type d'email
 *       fields: [            // Liste des champs du formulaire
 *         {
 *           id: string,      // Identifiant unique du champ
 *           label: string,   // Libellé affiché à l'utilisateur
 *           type: string,    // Type de champ (text, select, etc.)
 *           options: string[] // Options pour les champs de type select
 *         }
 *       ],
 *       prompt: string       // Template du prompt pour ce type
 *     }
 *   ]
 * }
 */

/**
 * Initialise les données des prompts dans l'objet window
 * Cette fonction est appelée par le template Jinja2 avec les données
 * @param {Object} data - Les données des prompts structurées comme décrit ci-dessus
 */
function initPromptsData(data) {
    window.promptsData = data;
}

// Les données seront injectées par le template
// initPromptsData({{ prompts_data|tojson|safe }}); 