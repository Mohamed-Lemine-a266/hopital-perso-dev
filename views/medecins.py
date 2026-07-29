import tkinter as tk
import csv
from tkinter import ttk, messagebox, filedialog
from config import C_FOND, C_PRIMAIRE, C_DANGER, JOURS_SEMAINE, STATUTS_MEDECIN
from models import medecin, specialite, file_attente, audit
from views.widgets import HeureEntry
import session


class VueMedecins:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Gestion des médecins", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=4)
        self.entries = {}
        for label, r, c in [("Nom :", 0, 0), ("Prénom :", 0, 2), ("Téléphone :", 0, 4)]:
            tk.Label(zone_form, text=label, bg=C_FOND).grid(row=r, column=c, padx=4, pady=3, sticky="w")
            e = tk.Entry(zone_form, width=16)
            e.grid(row=r, column=c+1, padx=4, pady=3)
            self.entries[label] = e

        tk.Label(zone_form, text="Spécialité :", bg=C_FOND).grid(row=1, column=0, padx=4, pady=3, sticky="w")
        self.specs_data = specialite.charger_toutes()
        self.spec_combo = ttk.Combobox(zone_form, values=[s[1] for s in self.specs_data], state="readonly", width=20)
        self.spec_combo.grid(row=1, column=1, padx=4, pady=3, sticky="w")

        tk.Label(zone_form, text="Statut :", bg=C_FOND).grid(row=1, column=2, padx=4, pady=3, sticky="w")
        self.statut_combo = ttk.Combobox(zone_form, values=STATUTS_MEDECIN, state="readonly", width=12)
        self.statut_combo.grid(row=1, column=3, padx=4, pady=3, sticky="w")
        self.statut_combo.set("présent")

        tk.Label(zone_form, text="Jours :", bg=C_FOND).grid(row=2, column=0, padx=4, pady=3, sticky="w")
        self.jours_vars = {}
        jf = tk.Frame(zone_form, bg=C_FOND)
        jf.grid(row=2, column=1, columnspan=3, padx=4, pady=3, sticky="w")
        for j in JOURS_SEMAINE:
            v = tk.BooleanVar(value=j not in ["Sam", "Dim"])
            tk.Checkbutton(jf, text=j, variable=v, bg=C_FOND).pack(side="left", padx=2)
            self.jours_vars[j] = v

        tk.Label(zone_form, text="Début :", bg=C_FOND).grid(row=2, column=4, padx=4, pady=3, sticky="w")
        self.debut_entry = HeureEntry(zone_form, heure_defaut="08:00")
        self.debut_entry.grid(row=2, column=5, padx=4, pady=3, sticky="w")

        tk.Label(zone_form, text="Fin :", bg=C_FOND).grid(row=3, column=4, padx=4, pady=3, sticky="w")
        self.fin_entry = HeureEntry(zone_form, heure_defaut="17:00")
        self.fin_entry.grid(row=3, column=5, padx=4, pady=3, sticky="w")

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=5)
        for txt, cmd, bg in [("Enregistrer", self._enregistrer, C_PRIMAIRE),
                               ("Modifier", self._modifier, "#468FAF"),
                               ("Supprimer", self._supprimer, C_DANGER),
                               ("Absences", self._ouvrir_absences, "#E67E22"),
                               ("Exporter CSV", self._exporter_csv, "#27AE60"),
                               ("Vider", self._vider, "#888")]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white", padx=10).pack(side="left", padx=4)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=4, fill="both", expand=True, padx=15)
        cols = ("nom", "prenom", "tel", "specialite", "jours", "horaires", "statut")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=10)
        for c, t, w in [("nom","Nom",110),("prenom","Prénom",110),("tel","Tél",90),
                         ("specialite","Spécialité",130),("jours","Jours",130),
                         ("horaires","Horaires",85),("statut","Statut",80)]:
            self.tableau.heading(c, text=t, command=lambda col=c: self._trier(col))
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tableau.bind("<<TreeviewSelect>>", self._remplir)
        self._tri_inverse = {}
        self._charger()

    def _charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        for m in medecin.charger_tous():
            self.tableau.insert("", "end", iid=m[0],
                values=(m[1], m[2], m[3] or "", m[4], m[5], f"{m[6]}-{m[7]}", m[8]))

    def _trier(self, col):
        inv = self._tri_inverse.get(col, False)
        data = [(self.tableau.set(k, col), k) for k in self.tableau.get_children("")]
        data.sort(reverse=inv)
        for i, (_, k) in enumerate(data):
            self.tableau.move(k, "", i)
        self._tri_inverse[col] = not inv

    def _jours_str(self):
        return ",".join(j for j, v in self.jours_vars.items() if v.get())

    def _spec_id(self):
        idx = self.spec_combo.current()
        return self.specs_data[idx][0] if idx >= 0 else None

    def _valider_horaires(self):
        deb = self.debut_entry.get().strip()
        fin = self.fin_entry.get().strip()
        if deb >= fin:
            messagebox.showwarning("Horaires", "L'heure de début doit être inférieure à l'heure de fin.")
            return False
        jours = self._jours_str()
        if jours == "":
            messagebox.showwarning("Jours", "Sélectionnez au moins un jour de travail.")
            return False
        return True

    def _enregistrer(self):
        nom = self.entries["Nom :"].get().strip()
        prenom = self.entries["Prénom :"].get().strip()
        tel = self.entries["Téléphone :"].get().strip()
        spec_id = self._spec_id()
        if nom == "" or prenom == "" or spec_id is None:
            messagebox.showwarning("Champs obligatoires", "Nom, prénom et spécialité obligatoires.")
            return
        if not self._valider_horaires():
            return
        if medecin.existe_deja(nom, prenom, spec_id):
            messagebox.showwarning("Doublon", "Ce médecin existe déjà dans cette spécialité.")
            return
        try:
            mid_new = medecin.ajouter(nom, prenom, tel, spec_id, self._jours_str(),
                            self.debut_entry.get().strip(), self.fin_entry.get().strip())
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "création", "medecins", mid_new, f"Dr. {nom} {prenom}")
            self._charger()
            messagebox.showinfo("Succès", f"Dr. {nom} {prenom} enregistré.")
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _modifier(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un médecin.")
            return
        nom = self.entries["Nom :"].get().strip()
        prenom = self.entries["Prénom :"].get().strip()
        tel = self.entries["Téléphone :"].get().strip()
        spec_id = self._spec_id()
        statut = self.statut_combo.get()
        if nom == "" or prenom == "" or spec_id is None:
            messagebox.showwarning("Champs obligatoires", "Nom, prénom et spécialité obligatoires.")
            return
        if not self._valider_horaires():
            return
        mid = sel[0]

        # Réorientation si passage à absent/congé
        ancien = medecin.obtenir_par_id(mid)
        if ancien and ancien[9] == "présent" and statut in ("absent", "en congé"):
            nb = file_attente.compter_en_attente_par_medecin(int(mid))
            if nb > 0:
                dispo = medecin.charger_disponibles_par_specialite(spec_id)
                dispo = [m for m in dispo if m[0] != int(mid)]
                if dispo and messagebox.askyesno("Réorientation",
                    f"Ce médecin a {nb} patient(s) en attente.\n"
                    f"Voulez-vous les réorienter automatiquement ?"):
                    # Trouver le moins chargé
                    min_nb, min_mid = float('inf'), dispo[0][0]
                    for m in dispo:
                        c = file_attente.compter_en_attente_par_medecin(m[0])
                        if c < min_nb:
                            min_nb, min_mid = c, m[0]
                    nb_r = medecin.reorienter_patients(int(mid), min_mid)
                    messagebox.showinfo("Réorientation", f"{nb_r} patient(s) réorienté(s).")

        try:
            medecin.modifier(mid, nom, prenom, tel, spec_id, self._jours_str(),
                             self.debut_entry.get().strip(), self.fin_entry.get().strip(), statut)
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "modification", "medecins", mid, f"Dr. {nom} {prenom} — statut: {statut}")
            self._charger()
            messagebox.showinfo("Succès", "Médecin modifié.")
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _supprimer(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un médecin.")
            return
        if medecin.a_des_enregistrements(sel[0]):
            messagebox.showwarning("Impossible", "Ce médecin a des enregistrements liés.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce médecin ?"):
            return
        vals = self.tableau.item(sel[0], "values")
        try:
            medecin.supprimer(sel[0])
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "suppression", "medecins", sel[0], f"Dr. {vals[0]} {vals[1]}")
            self._charger()
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _remplir(self, event):
        sel = self.tableau.selection()
        if not sel:
            return
        m = medecin.obtenir_par_id(sel[0])
        if not m:
            return
        self._vider()
        self.entries["Nom :"].insert(0, m[1])
        self.entries["Prénom :"].insert(0, m[2])
        self.entries["Téléphone :"].insert(0, m[3] or "")
        self.spec_combo.set(m[5])
        jours = m[6].split(",") if m[6] else []
        for j, v in self.jours_vars.items():
            v.set(j in jours)
        self.debut_entry.delete(0, tk.END)
        self.debut_entry.insert(0, m[7])
        self.fin_entry.delete(0, tk.END)
        self.fin_entry.insert(0, m[8])
        self.statut_combo.set(m[9])

    def _vider(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.spec_combo.set("")
        self.statut_combo.set("présent")
        for j, v in self.jours_vars.items():
            v.set(j not in ["Sam", "Dim"])
        self.debut_entry.delete(0, tk.END)
        self.debut_entry.insert(0, "08:00")
        self.fin_entry.delete(0, tk.END)
        self.fin_entry.insert(0, "17:00")

    def _exporter_csv(self):
        dest = filedialog.asksaveasfilename(title="Exporter les médecins", defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv"), ("Tous", "*.*")])
        if not dest:
            return
        try:
            with open(dest, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Nom", "Prénom", "Téléphone", "Spécialité", "Jours", "Horaires", "Statut"])
                for row_id in self.tableau.get_children():
                    writer.writerow(self.tableau.item(row_id, "values"))
            messagebox.showinfo("Succès", f"Médecins exportés vers :\n{dest}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _ouvrir_absences(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un médecin.")
            return
        from views.absences import PopupAbsences
        vals = self.tableau.item(sel[0], "values")
        PopupAbsences(self.frame.winfo_toplevel(), int(sel[0]), f"Dr. {vals[0]} {vals[1]}")
