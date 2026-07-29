import tkinter as tk
from tkinter import ttk, messagebox
from config import C_FOND, C_PRIMAIRE, C_DANGER, FONT_H1, FONT_TEXTE
from models import specialite, audit
import session


class VueSpecialites:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Gestion des spécialités", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 8))
        tk.Label(self.frame, text="Ajoutez, renommez ou supprimez les spécialités de l'établissement.",
                 font=("Arial", 9, "italic"), bg=C_FOND, fg="#888").pack(pady=(0, 10))

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=5)
        tk.Label(zone_form, text="Nom de la spécialité :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=0, column=0, padx=5)
        self.nom_entry = tk.Entry(zone_form, width=30, font=FONT_TEXTE)
        self.nom_entry.grid(row=0, column=1, padx=5)

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=8)
        for txt, cmd, bg in [("Ajouter", self._ajouter, C_PRIMAIRE),
                              ("Modifier", self._modifier, "#468FAF"),
                              ("Supprimer", self._supprimer, C_DANGER),
                              ("Vider", self._vider, "#888")]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white", padx=10).pack(side="left", padx=4)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=8, fill="both", expand=True, padx=20)
        self.tableau = ttk.Treeview(zone_tab, columns=("nom",), show="headings", height=14)
        self.tableau.heading("nom", text="Spécialité")
        self.tableau.column("nom", width=300)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self._remplir)

        self._charger()

    def _charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        for s in specialite.charger_toutes():
            self.tableau.insert("", "end", iid=s[0], values=(s[1],))

    def _ajouter(self):
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showwarning("Champ requis", "Le nom est obligatoire.")
            return
        if specialite.nom_existe(nom):
            messagebox.showwarning("Doublon", "Cette spécialité existe déjà.")
            return
        sid = specialite.ajouter(nom)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "création", "specialites", sid, nom)
        self._charger()
        self._vider()
        messagebox.showinfo("Succès", f"Spécialité '{nom}' ajoutée.")

    def _modifier(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une spécialité.")
            return
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showwarning("Champ requis", "Le nom est obligatoire.")
            return
        sid = sel[0]
        if specialite.nom_existe(nom, exclure_id=sid):
            messagebox.showwarning("Doublon", "Une autre spécialité porte déjà ce nom.")
            return
        ancien = self.tableau.item(sid, "values")[0]
        specialite.modifier(sid, nom)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "modification", "specialites", sid, nom,
                           ancien_valeur=ancien, nouvelle_valeur=nom)
        self._charger()
        self._vider()
        messagebox.showinfo("Succès", "Spécialité modifiée.")

    def _supprimer(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une spécialité.")
            return
        if specialite.a_des_medecins(sel[0]):
            messagebox.showwarning("Impossible", "Des médecins sont rattachés à cette spécialité.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette spécialité ?"):
            return
        nom = self.tableau.item(sel[0], "values")[0]
        specialite.supprimer(sel[0])
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "suppression", "specialites", sel[0], nom)
        self._charger()
        self._vider()

    def _remplir(self, event):
        sel = self.tableau.selection()
        if not sel:
            return
        self._vider()
        self.nom_entry.insert(0, self.tableau.item(sel[0], "values")[0])

    def _vider(self):
        self.nom_entry.delete(0, tk.END)
