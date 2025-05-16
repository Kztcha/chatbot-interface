/**
 * Gestion spécifique de la page des utilisateurs
 * Ce module gère l'interface d'administration des utilisateurs :
 * - Ajout de nouveaux utilisateurs
 * - Suppression d'utilisateurs existants
 * - Modification des mots de passe
 * - Mise à jour en temps réel de la liste des utilisateurs
 */

/**
 * Gestion du formulaire d'ajout d'utilisateur
 * - Empêche la soumission par défaut
 * - Vide les champs après soumission
 * - Envoie les données au serveur
 * - Recharge la liste des utilisateurs en cas de succès
 * - Affiche un message de succès/erreur
 */
document.getElementById("add-user-form").onsubmit = function(e) {
    e.preventDefault();
    e.target.reset(); // Vide les champs après soumission
    const data = new URLSearchParams(new FormData(e.target));
    fetch("/admin/users/add", { method: "POST", body: data })
        .then(res => res.ok ? reloadUsers() : res.text().then(e => Promise.reject(e)))
        .then(msg => showMessage("users-msg", msg || "✔️ Utilisateur ajouté", "success"))
        .catch(err => showMessage("users-msg", err, "error"));
};

/**
 * Recharge la liste des utilisateurs depuis le serveur
 * - Récupère le HTML mis à jour de la table
 * - Met à jour l'affichage
 * - Réattache les gestionnaires d'événements aux nouveaux éléments
 */
function reloadUsers() {
    fetch("/admin/users/table")
        .then(res => res.text())
        .then(html => {
            document.getElementById("users-body").innerHTML = html;
            attachUserActions();
        });
}

/**
 * Attache les gestionnaires d'événements aux formulaires
 * Gère deux types d'actions :
 * 1. Suppression d'utilisateur
 * 2. Modification du mot de passe
 * 
 * Pour chaque action :
 * - Empêche la soumission par défaut
 * - Demande confirmation si nécessaire
 * - Envoie les données au serveur
 * - Recharge la liste en cas de succès
 * - Affiche un message de succès/erreur
 */
function attachUserActions() {
    // Gestion de la suppression
    document.querySelectorAll(".delete-user-form").forEach(form => {
        form.onsubmit = function(e) {
            e.preventDefault();
            if (confirmDelete("Êtes-vous sûr de vouloir supprimer cet utilisateur ?")) {
                const data = new URLSearchParams(new FormData(form));
                fetch("/admin/users/delete", { method: "POST", body: data })
                    .then(res => res.ok ? reloadUsers() : res.text().then(e => Promise.reject(e)))
                    .then(msg => showMessage("users-msg", msg || "✔️ Utilisateur supprimé", "success"))
                    .catch(err => showMessage("users-msg", err, "error"));
            }
        };
    });

    // Gestion de la modification
    document.querySelectorAll(".update-user-form").forEach(form => {
        form.onsubmit = function(e) {
            e.preventDefault();
            const data = new URLSearchParams(new FormData(form));
            fetch("/admin/users/update", { method: "POST", body: data })
                .then(res => res.ok ? reloadUsers() : res.text().then(e => Promise.reject(e)))
                .then(msg => showMessage("users-msg", msg || "✔️ Mot de passe modifié", "success"))
                .catch(err => showMessage("users-msg", err, "error"));
        };
    });
}

// Initialisation : attache les gestionnaires d'événements au chargement de la page
attachUserActions(); 