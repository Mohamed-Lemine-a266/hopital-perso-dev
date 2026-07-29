import tkinter as tk
from tkinter import messagebox
from config import C_FOND, C_PRIMAIRE, FONT_H1, FONT_TEXTE
from models import utilisateur, audit
import session


class VueMonProfil:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        u = session.utilisateur_courant()

        tk.Label(self.frame, text="Mon profil", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(25, 15))

        zone = tk.Frame(self.frame, bg=C_FOND)
        zone.pack(pady=10)

        tk.Label(zone, text="Identifiant :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=0, column=0, padx=10, pady=8, sticky="w")
        tk.Label(zone, text=u["nom_utilisateur"], bg=C_FOND, font=("Arial", 10, "bold")).grid(
            row=0, column=1, padx=10, pady=8, sticky="w")

        tk.Label(zone, text="Nom complet :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=1, column=0, padx=10, pady=8, sticky="w")
        tk.Label(zone, text=f"{u['prenom']} {u['nom']}", bg=C_FOND, font=("Arial", 10, "bold")).grid(
            row=1, column=1, padx=10, pady=8, sticky="w")

        tk.Label(zone, text="Rôle :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=2, column=0, padx=10, pady=8, sticky="w")
        tk.Label(zone, text=u["role_nom"], bg=C_FOND, font=("Arial", 10, "bold")).grid(
            row=2, column=1, padx=10, pady=8, sticky="w")

        tk.Frame(self.frame, bg="#CCC", height=1).pack(fill="x", padx=60, pady=15)

        tk.Label(self.frame, text="Changer mon mot de passe", font=("Arial", 12, "bold"),
                 bg=C_FOND, fg="#333").pack(pady=(0, 10))

        zone_mdp = tk.Frame(self.frame, bg=C_FOND)
        zone_mdp.pack(pady=5)

        tk.Label(zone_mdp, text="Mot de passe actuel :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=0, column=0, padx=10, pady=8, sticky="w")
        self.actuel_entry = tk.Entry(zone_mdp, width=25, show="•", font=FONT_TEXTE)
        self.actuel_entry.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(zone_mdp, text="Nouveau mot de passe :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=1, column=0, padx=10, pady=8, sticky="w")
        self.nouveau_entry = tk.Entry(zone_mdp, width=25, show="•", font=FONT_TEXTE)
        self.nouveau_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(zone_mdp, text="Confirmer le nouveau :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=2, column=0, padx=10, pady=8, sticky="w")
        self.confirmer_entry = tk.Entry(zone_mdp, width=25, show="•", font=FONT_TEXTE)
        self.confirmer_entry.grid(row=2, column=1, padx=10, pady=8)

        tk.Button(self.frame, text="Mettre à jour le mot de passe", command=self._changer_mdp,
                  bg=C_PRIMAIRE, fg="white", font=("Arial", 11), padx=15, pady=5).pack(pady=15)

        self.info = tk.Label(self.frame, text="", bg=C_FOND, fg="#27AE60", font=("Arial", 10, "italic"))
        self.info.pack()

    def _changer_mdp(self):
        u = session.utilisateur_courant()
        actuel = self.actuel_entry.get()
        nouveau = self.nouveau_entry.get()
        confirmer = self.confirmer_entry.get()

        if not actuel or not nouveau or not confirmer:
            messagebox.showwarning("Champs requis", "Remplissez tous les champs.")
            return

        verif = utilisateur.authentifier(u["nom_utilisateur"], actuel)
        if verif is None:
            messagebox.showerror("Erreur", "Le mot de passe actuel est incorrect.")
            return

        if nouveau != confirmer:
            messagebox.showwarning("Erreur", "Les deux nouveaux mots de passe ne correspondent pas.")
            return

        if len(nouveau) < 4:
            messagebox.showwarning("Mot de passe trop court", "Le mot de passe doit contenir au moins 4 caractères.")
            return

        utilisateur.changer_mot_de_passe(u["id"], nouveau)
        audit.enregistrer(u["id"], session.utilisateur_nom_complet(),
                           "modification", "utilisateurs", u["id"], "Mot de passe changé par l'utilisateur lui-même")
        self.actuel_entry.delete(0, tk.END)
        self.nouveau_entry.delete(0, tk.END)
        self.confirmer_entry.delete(0, tk.END)
        self.info.config(text="Mot de passe mis à jour avec succès.")
        messagebox.showinfo("Succès", "Votre mot de passe a été mis à jour.")
