import tkinter as tk
import re
from tkinter import messagebox, filedialog
from config import C_FOND, C_PRIMAIRE
from models import parametres, audit
from utils.sauvegarde import sauvegarder_base, restaurer_base
import session


class VueParametres:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Paramètres", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(20, 12))

        zone = tk.Frame(self.frame, bg=C_FOND)
        zone.pack(pady=10)

        self.entries = {}
        champs = [("Nom de l'hôpital", "nom_hopital"),
                  ("Email", "email_hopital"),
                  ("Préfixe patient (ex: HOP)", "prefixe_patient"),
                  ("Durée RDV par défaut (min)", "duree_rdv_defaut")]

        for i, (label, cle) in enumerate(champs):
            tk.Label(zone, text=f"{label} :", bg=C_FOND, font=("Arial", 10)).grid(
                row=i, column=0, padx=10, pady=8, sticky="w")
            e = tk.Entry(zone, width=35, font=("Arial", 10))
            e.grid(row=i, column=1, padx=10, pady=8)
            e.insert(0, parametres.obtenir(cle))
            self.entries[cle] = e

        # Logo
        r = len(champs)
        tk.Label(zone, text="Logo (PNG/GIF) :", bg=C_FOND, font=("Arial", 10)).grid(
            row=r, column=0, padx=10, pady=8, sticky="w")
        self.logo_entry = tk.Entry(zone, width=25, font=("Arial", 10))
        self.logo_entry.grid(row=r, column=1, padx=10, pady=8, sticky="w")
        self.logo_entry.insert(0, parametres.logo())
        tk.Button(zone, text="Parcourir...", command=self.choisir_logo,
                  bg="#468FAF", fg="white").grid(row=r, column=2, padx=5)

        # Boutons
        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=15)
        tk.Button(zone_btn, text="Sauvegarder les paramètres", command=self.sauvegarder,
                  bg=C_PRIMAIRE, fg="white", font=("Arial", 11), padx=15, pady=4).pack(side="left", padx=10)
        tk.Button(zone_btn, text="Sauvegarder la base de données", command=self.sauvegarder_bdd,
                  bg="#27AE60", fg="white", font=("Arial", 11), padx=15, pady=4).pack(side="left", padx=10)
        tk.Button(zone_btn, text="Restaurer une sauvegarde", command=self.restaurer_bdd,
                  bg="#E67E22", fg="white", font=("Arial", 11), padx=15, pady=4).pack(side="left", padx=10)

        self.info = tk.Label(self.frame, text="", bg=C_FOND, fg="#27AE60", font=("Arial", 10, "italic"))
        self.info.pack(pady=5)

    def choisir_logo(self):
        chemin = filedialog.askopenfilename(title="Choisir le logo",
            filetypes=[("Images", "*.png *.gif"), ("Tous", "*.*")])
        if chemin:
            self.logo_entry.delete(0, tk.END)
            self.logo_entry.insert(0, chemin)

    def _valider_email(self, email):
        if email == "":
            return True
        return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None

    def sauvegarder(self):
        nom = self.entries["nom_hopital"].get().strip()
        email = self.entries["email_hopital"].get().strip()
        if not nom:
            messagebox.showwarning("Requis", "Le nom de l'hôpital est obligatoire.")
            return
        if not self._valider_email(email):
            messagebox.showwarning("Email invalide", "L'adresse email n'est pas valide.")
            return
        for cle, entry in self.entries.items():
            parametres.modifier(cle, entry.get().strip())
        parametres.modifier("logo_path", self.logo_entry.get().strip())
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "modification", "parametres", None, f"Hôpital: {nom}")
        self.info.config(text="Paramètres sauvegardés.")

    def sauvegarder_bdd(self):
        dest = filedialog.asksaveasfilename(title="Sauvegarder la base",
            defaultextension=".db", filetypes=[("SQLite", "*.db"), ("Tous", "*.*")])
        if dest:
            try:
                sauvegarder_base(dest)
                audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                                   "sauvegarde", "parametres", None, f"Base sauvegardée : {dest}")
                messagebox.showinfo("Succès", f"Base sauvegardée dans :\n{dest}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def restaurer_bdd(self):
        avertissement = (
            "Cette action va remplacer TOUTES les données actuelles par celles "
            "de la sauvegarde choisie.\n\n"
            "Une copie de sécurité de la base actuelle sera créée automatiquement.\n"
            "L'application devra être redémarrée après la restauration.\n\n"
            "Voulez-vous continuer ?"
        )
        if not messagebox.askyesno("Restauration — Confirmation", avertissement, icon="warning"):
            return
        source = filedialog.askopenfilename(title="Choisir la sauvegarde à restaurer",
            filetypes=[("SQLite", "*.db"), ("Tous", "*.*")])
        if not source:
            return
        try:
            restaurer_base(source)
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "restauration", "parametres", None, f"Restauré depuis : {source}")
            messagebox.showinfo("Succès",
                "Base restaurée avec succès.\n\nVeuillez fermer et relancer l'application "
                "pour que les changements soient pris en compte.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
