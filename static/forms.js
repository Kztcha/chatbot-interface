/**
 * forms.js - Gestion des formulaires dynamiques
 * Ce module gère la création et la manipulation des formulaires :
 * - Génération dynamique des formulaires basée sur les champs reçus
 * - Gestion des différents types de champs (texte, select)
 * - Soumission et validation des données
 * - Nettoyage des formulaires
 */

/**
 * Génère un formulaire dynamique basé sur les champs spécifiés
 * @param {Array} fields - Liste des champs à afficher
 *                        Chaque champ doit avoir : id, label, et type
 *                        Pour les selects : options[]
 */
function renderForm(fields) {
  const formContainer = document.getElementById("form-container");
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

  form.addEventListener("submit", e => {
    e.preventDefault();
    const data = {};
    fields.forEach(f => {
      data[f.id] = document.getElementById(f.id).value.trim();
    });

    // Si c'est un formulaire de détails (ni type, ni dest/obj)
    if (fields.length && !["type", "dest", "obj"].includes(fields[0].id)) {
      Chat.sendData({ details: data });
    } else {
      Chat.sendData(data);
    }
  });
}

/**
 * Nettoie le contenu du conteneur de formulaire
 * Utilisé avant de charger un nouveau formulaire ou
 * après la soumission des données
 */
function clearForm() {
  const formContainer = document.getElementById("form-container");
  formContainer.innerHTML = "";
}

// Export des fonctions pour utilisation dans d'autres modules
window.Forms = {
  renderForm,
  clearForm
}; 