import tkinter as tk
from tkinter import ttk, messagebox
from config import C_FOND, C_PRIMAIRE, C_DANGER
from models import utilisateur, audit, medecin
import session


class VueUtilisateurs:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Gestion des utilisateurs et rôles", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 8))

        tk.Label(self.frame, text="Utilisateurs", font=("Arial", 13, "bold"),
                 bg=C_FOND, fg="#333").pack(pady=(8, 4), anchor="w", padx=15)

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=3, padx=15, anchor="w")

        self.entries = {}
        for i, (lbl, w) in enumerate([("Identifiant :", 15), ("Nom :", 15), ("Prénom :", 15), ("Mot de passe :", 15)]):
            tk.Label(zone_form, text=lbl, bg=C_FOND).grid(row=0, column=i*2, padx=4, pady=4, sticky="w")
            e = tk.Entry(zone_form, width=w, show="*" if "passe" in lbl else "")
            e.grid(row=0, column=i*2+1, padx=4, pady=4)
            self.entries[lbl] = e

        tk.Label(zone_form, text="Rôle :", bg=C_FOND).grid(row=1, column=0, padx=4, pady=4, sticky="w")
        self.roles_data = utilisateur.charger_roles()
        self.role_combo = ttk.Combobox(zone_form, values=[r[1] for r in self.roles_data], state="readonly", width=18)
        self.role_combo.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        self.actif_var = tk.BooleanVar(value=True)
        tk.Checkbutton(zone_form, text="Actif", variable=self.actif_var, bg=C_FOND).grid(
            row=1, column=2, padx=4, pady=4, sticky="w")

        tk.Label(zone_form, text="Médecin lié :", bg=C_FOND).grid(row=2, column=0, padx=4, pady=4, sticky="w")
        self.medecins_data = medecin.charger_tous()
        self.medecin_combo = ttk.Combobox(
            zone_form, values=["(Aucun)"] + [f"Dr. {m[1]} {m[2]}" for m in self.medecins_data],
            state="readonly", width=25)
        self.medecin_combo.grid(row=2, column=1, columnspan=3, padx=4, pady=4, sticky="w")
        self.medecin_combo.set("(Aucun)")

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=4, padx=15, anchor="w")
        for txt, cmd, bg in [("Ajouter", self.ajouter_user, C_PRIMAIRE),
                               ("Modifier", self.modifier_user, "#468FAF"),
                               ("Supprimer", self.supprimer_user, C_DANGER),
                               ("Vider", self.vider, "#888")]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white", padx=8).pack(side="left", padx=3)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=5, fill="x", padx=15)

        cols = ("id", "identifiant", "nom", "prenom", "role", "actif", "medecin")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=6)
        for c, t, w in [("id","ID",35),("identifiant","Identifiant",110),("nom","Nom",100),
                         ("prenom","Prénom",100),("role","Rôle",110),("actif","Actif",45),
                         ("medecin","Médecin lié",140)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        self.tableau.pack(fill="x")
        self.tableau.bind("<<TreeviewSelect>>", self.remplir)

        tk.Label(self.frame, text="Gestion des rôles et permissions", font=("Arial", 13, "bold"),
                 bg=C_FOND, fg="#333").pack(pady=(12, 4), anchor="w", padx=15)

        zone_role = tk.Frame(self.frame, bg=C_FOND)
        zone_role.pack(pady=3, padx=15, anchor="w")

        tk.Label(zone_role, text="Rôle :", bg=C_FOND).grid(row=0, column=0, padx=5, pady=4)
        self.role_select = ttk.Combobox(zone_role, values=[r[1] for r in self.roles_data],
                                         state="readonly", width=18)
        self.role_select.grid(row=0, column=1, padx=5, pady=4)
        self.role_select.bind("<<ComboboxSelected>>", self.charger_perms_role)
        tk.Label(zone_role, text="Nouveau rôle :", bg=C_FOND).grid(row=0, column=2, padx=5, pady=4)
        self.new_role_entry = tk.Entry(zone_role, width=15)
        self.new_role_entry.grid(row=0, column=3, padx=5, pady=4)
        tk.Button(zone_role, text="Créer", command=self.creer_role, bg=C_PRIMAIRE,
                  fg="white", padx=6).grid(row=0, column=4, padx=5)

        self.perms_data = utilisateur.charger_permissions()
        self.perms_vars = {}
        zone_perms = tk.Frame(self.frame, bg=C_FOND)
        zone_perms.pack(pady=5, padx=20, anchor="w")

        for i, p in enumerate(self.perms_data):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(zone_perms, text=f"{p[1]} — {p[2]}", variable=var, bg=C_FOND, font=("Arial", 9))
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=1)
            self.perms_vars[p[0]] = var

        tk.Button(self.frame, text="Sauvegarder les permissions du rôle", command=self.sauver_perms,
                  bg=C_PRIMAIRE, fg="white", padx=10).pack(pady=8)

        self.charger_users()

    def charger_users(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        for u in utilisateur.charger_tous():
            mid = utilisateur.obtenir_medecin_id(u[0])
            nom_med = "—"
            if mid:
                m = medecin.obtenir_par_id(mid)
                if m:
                    nom_med = f"Dr. {m[1]} {m[2]}"
            self.tableau.insert("", "end", iid=u[0],
                values=(u[0], u[1], u[2], u[3], u[4], "Oui" if u[5] else "Non", nom_med))

    def remplir(self, event):
        sel = self.tableau.selection()
        if not sel:
            return
        vals = self.tableau.item(sel[0], "values")
        self.vider()
        self.entries["Identifiant :"].insert(0, vals[1])
        self.entries["Nom :"].insert(0, vals[2])
        self.entries["Prénom :"].insert(0, vals[3])
        self.role_combo.set(vals[4])
        self.actif_var.set(vals[5] == "Oui")
        self.medecin_combo.set(vals[6] if vals[6] != "—" else "(Aucun)")

    def vider(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.role_combo.set("")
        self.actif_var.set(True)
        self.medecin_combo.set("(Aucun)")

    def _role_id(self):
        idx = self.role_combo.current()
        return self.roles_data[idx][0] if idx >= 0 else None

    def _medecin_id_selectionne(self):
        idx = self.medecin_combo.current()
        if idx <= 0:
            return None
        return self.medecins_data[idx - 1][0]

    def ajouter_user(self):
        ident = self.entries["Identifiant :"].get().strip()
        nom = self.entries["Nom :"].get().strip()
        prenom = self.entries["Prénom :"].get().strip()
        mdp = self.entries["Mot de passe :"].get()
        rid = self._role_id()
        if not ident or not nom or not prenom or not mdp or rid is None:
            messagebox.showwarning("Champs requis", "Tous les champs sont obligatoires.")
            return
        if utilisateur.nom_utilisateur_existe(ident):
            messagebox.showwarning("Doublon", "Cet identifiant existe déjà.")
            return
        new_uid = utilisateur.ajouter(ident, mdp, nom, prenom, rid)
        mid = self._medecin_id_selectionne()
        if mid:
            utilisateur.lier_medecin(new_uid, mid)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "création", "utilisateurs", new_uid, f"{ident} ({nom} {prenom})")
        self.charger_users()
        self.vider()
        messagebox.showinfo("Succès", "Utilisateur créé.")

    def modifier_user(self):
        sel = self.tableau.selection()
        if not sel:
            return
        ident = self.entries["Identifiant :"].get().strip()
        nom = self.entries["Nom :"].get().strip()
        prenom = self.entries["Prénom :"].get().strip()
        rid = self._role_id()
        if not ident or not nom or not prenom or rid is None:
            messagebox.showwarning("Champs requis", "Remplissez tous les champs.")
            return
        uid = sel[0]
        if utilisateur.nom_utilisateur_existe(ident, exclure_id=uid):
            messagebox.showwarning("Doublon", "Cet identifiant est déjà pris.")
            return
        utilisateur.modifier(uid, ident, nom, prenom, rid, 1 if self.actif_var.get() else 0)
        mdp = self.entries["Mot de passe :"].get()
        if mdp:
            utilisateur.changer_mot_de_passe(uid, mdp)
        mid = self._medecin_id_selectionne()
        utilisateur.lier_medecin(uid, mid)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "modification", "utilisateurs", uid, f"{ident} ({nom} {prenom})")
        self.charger_users()
        self.vider()
        messagebox.showinfo("Succès", "Utilisateur modifié.")

    def supprimer_user(self):
        sel = self.tableau.selection()
        if not sel:
            return
        if int(sel[0]) == session.utilisateur_id():
            messagebox.showwarning("Action impossible", "Vous ne pouvez pas supprimer votre propre compte.")
            return
        vals = self.tableau.item(sel[0], "values")
        if not messagebox.askyesno("Confirmation", "Supprimer cet utilisateur ?"):
            return
        utilisateur.supprimer(sel[0])
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "suppression", "utilisateurs", sel[0], f"{vals[1]} ({vals[2]} {vals[3]})")
        self.charger_users()
        self.vider()

    def creer_role(self):
        nom = self.new_role_entry.get().strip()
        if not nom:
            return
        try:
            utilisateur.ajouter_role(nom)
            self.roles_data = utilisateur.charger_roles()
            self.role_combo["values"] = [r[1] for r in self.roles_data]
            self.role_select["values"] = [r[1] for r in self.roles_data]
            self.new_role_entry.delete(0, tk.END)
            messagebox.showinfo("Succès", f"Rôle '{nom}' créé.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def charger_perms_role(self, event=None):
        idx = self.role_select.current()
        if idx < 0:
            return
        rid = self.roles_data[idx][0]
        perms_role = utilisateur.permissions_du_role(rid)
        pids = set(p[0] for p in perms_role)
        for pid, var in self.perms_vars.items():
            var.set(pid in pids)

    def sauver_perms(self):
        idx = self.role_select.current()
        if idx < 0:
            messagebox.showwarning("Sélection", "Sélectionnez un rôle.")
            return
        rid = self.roles_data[idx][0]
        pids = [pid for pid, var in self.perms_vars.items() if var.get()]
        utilisateur.definir_permissions_role(rid, pids)
        messagebox.showinfo("Succès", "Permissions mises à jour.")