import tkinter as tk
import re
import csv
from tkinter import ttk, messagebox, Toplevel, filedialog
from datetime import datetime
from config import C_FOND, C_PRIMAIRE, C_DANGER, SEXES, GROUPES_SANGUINS, FONT_H2, FONT_TEXTE
from models import patient, audit
from views.widgets import DateEntry
import session


class VuePatients:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Gestion des patients", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=4)
        self.entries = {}
        champs = [("N° CNI :", 0, 0), ("Nom :", 0, 2), ("Prénom :", 0, 4),
                  ("Sexe :", 1, 0), ("Date naissance :", 1, 2), ("Téléphone :", 1, 4),
                  ("Adresse :", 2, 0)]
        for label, row, col in champs:
            tk.Label(zone_form, text=label, bg=C_FOND).grid(row=row, column=col, padx=4, pady=3, sticky="w")
            if label == "Sexe :":
                w = ttk.Combobox(zone_form, values=SEXES, state="readonly", width=14)
            elif label == "Adresse :":
                w = tk.Entry(zone_form, width=46)
                w.grid(row=row, column=col+1, columnspan=5, padx=4, pady=3, sticky="w")
                self.entries[label] = w
                continue
            elif label == "Date naissance :":
                w = DateEntry(zone_form, width=11)
                w.grid(row=row, column=col+1, padx=4, pady=3, sticky="w")
                self.entries[label] = w
                continue
            else:
                w = tk.Entry(zone_form, width=17)
            w.grid(row=row, column=col+1, padx=4, pady=3)
            self.entries[label] = w

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=5)
        for txt, cmd, bg in [("Enregistrer", self._enregistrer, C_PRIMAIRE),
                               ("Modifier", self._modifier, "#468FAF"),
                               ("Supprimer", self._supprimer, C_DANGER),
                               ("Infos médicales", self._ouvrir_infos_medicales, "#6C5CE7"),
                               ("Exporter CSV", self._exporter_csv, "#27AE60"),
                               ("Vider", self._vider, "#888")]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white", padx=10).pack(side="left", padx=4)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=4, fill="both", expand=True, padx=15)
        cols = ("cni", "nom", "prenom", "sexe", "naissance", "telephone", "adresse", "inscription")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=12)
        for c, t, w in [("cni","CNI",100),("nom","Nom",100),("prenom","Prénom",100),("sexe","Sexe",65),
                         ("naissance","Naissance",85),("telephone","Tél",90),("adresse","Adresse",120),
                         ("inscription","Inscrit",80)]:
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
        for p in patient.charger_tous():
            self.tableau.insert("", "end", iid=p[0],
                values=(p[1], p[2], p[3], p[4] or "", p[5] or "", p[6] or "", p[7] or "", p[8]))

    def _trier(self, col):
        inverse = self._tri_inverse.get(col, False)
        donnees = [(self.tableau.set(k, col), k) for k in self.tableau.get_children("")]
        donnees.sort(reverse=inverse)
        for i, (_, k) in enumerate(donnees):
            self.tableau.move(k, "", i)
        self._tri_inverse[col] = not inverse

    def _get(self):
        return tuple(
            self.entries[k].get().strip() if not isinstance(self.entries[k], ttk.Combobox) else self.entries[k].get()
            for k in ["N° CNI :", "Nom :", "Prénom :", "Sexe :", "Date naissance :", "Téléphone :", "Adresse :"])

    def _valider_telephone(self, tel):
        if tel == "":
            return True
        return re.fullmatch(r"[0-9+\s\-]{7,15}", tel) is not None

    def _enregistrer(self):
        cni, nom, prenom, sexe, dn, tel, adr = self._get()
        if cni == "" or nom == "" or prenom == "":
            messagebox.showwarning("Champs obligatoires", "CNI, nom et prénom sont obligatoires.")
            return
        if not patient.format_cni_valide(cni):
            messagebox.showwarning("CNI invalide",
                "Le format du CNI est invalide.\nIl doit contenir au moins 5 caractères alphanumériques.")
            return
        if not self._valider_telephone(tel):
            messagebox.showwarning("Téléphone invalide", "Le numéro de téléphone n'est pas valide.")
            return
        if patient.cni_existe(cni):
            messagebox.showwarning("Doublon", f"Le CNI {cni} est déjà enregistré.")
            return
        try:
            di = datetime.now().strftime("%Y-%m-%d")
            pid = patient.ajouter(cni, nom, prenom, sexe, dn, tel, adr, di)
            self.tableau.insert("", "end", iid=pid, values=(cni, nom, prenom, sexe, dn, tel, adr, di))
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "création", "patients", pid, f"{nom} {prenom} (CNI: {cni})")
            messagebox.showinfo("Succès", f"Patient enregistré (CNI: {cni}).")
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _modifier(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un patient.")
            return
        cni, nom, prenom, sexe, dn, tel, adr = self._get()
        if cni == "" or nom == "" or prenom == "":
            messagebox.showwarning("Champs obligatoires", "CNI, nom et prénom sont obligatoires.")
            return
        if not patient.format_cni_valide(cni):
            messagebox.showwarning("CNI invalide",
                "Le format du CNI est invalide.\nIl doit contenir au moins 5 caractères alphanumériques.")
            return
        pid = sel[0]
        if patient.cni_existe(cni, exclure_id=pid):
            messagebox.showwarning("Doublon", f"Le CNI {cni} est déjà utilisé.")
            return
        if not self._valider_telephone(tel):
            messagebox.showwarning("Téléphone invalide", "Le numéro de téléphone n'est pas valide.")
            return
        try:
            patient.modifier(pid, cni, nom, prenom, sexe, dn, tel, adr)
            anc = self.tableau.item(pid, "values")
            self.tableau.item(pid, values=(cni, nom, prenom, sexe, dn, tel, adr, anc[7]))
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "modification", "patients", pid, f"{nom} {prenom} (CNI: {cni})")
            messagebox.showinfo("Succès", "Patient modifié.")
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _supprimer(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un patient.")
            return
        if patient.a_des_enregistrements(sel[0]):
            messagebox.showwarning("Impossible", "Ce patient a des RDV, consultations ou entrées en file.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce patient définitivement ?"):
            return
        vals = self.tableau.item(sel[0], "values")
        try:
            patient.supprimer(sel[0])
            self.tableau.delete(sel[0])
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "suppression", "patients", sel[0], f"{vals[1]} {vals[2]} (CNI: {vals[0]})")
            self._vider()
        except Exception as e:
            messagebox.showerror("Erreur", f"{e}")

    def _remplir(self, event):
        sel = self.tableau.selection()
        if not sel:
            return
        v = self.tableau.item(sel[0], "values")
        self._vider()
        keys = ["N° CNI :", "Nom :", "Prénom :", "Sexe :", "Date naissance :", "Téléphone :", "Adresse :"]
        for i, k in enumerate(keys):
            if isinstance(self.entries[k], ttk.Combobox):
                self.entries[k].set(v[i] if v[i] else "")
            else:
                self.entries[k].insert(0, v[i] if v[i] else "")

    def _ouvrir_infos_medicales(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un patient.")
            return
        pid = sel[0]
        vals = self.tableau.item(pid, "values")
        infos = patient.obtenir_infos_medicales(pid) or ("", "", "", "")

        popup = Toplevel()
        popup.title(f"Informations médicales — {vals[1]} {vals[2]}")
        popup.geometry("480x420")
        popup.configure(bg=C_FOND)
        popup.grab_set()

        tk.Label(popup, text=f"{vals[1]} {vals[2]} (CNI: {vals[0]})", font=FONT_H2,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(15, 10))

        zone = tk.Frame(popup, bg=C_FOND)
        zone.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Label(zone, text="Groupe sanguin :", bg=C_FOND, font=FONT_TEXTE).grid(
            row=0, column=0, padx=5, pady=6, sticky="w")
        groupe_combo = ttk.Combobox(zone, values=GROUPES_SANGUINS, state="readonly", width=8)
        groupe_combo.grid(row=0, column=1, padx=5, pady=6, sticky="w")
        groupe_combo.set(infos[3] or "")

        champs_texte = {}
        for i, (label, key) in enumerate([("Allergies :", "allergies"),
                                            ("Antécédents médicaux :", "atcd_med"),
                                            ("Antécédents chirurgicaux :", "atcd_chir")]):
            tk.Label(zone, text=label, bg=C_FOND, font=FONT_TEXTE).grid(
                row=i+1, column=0, padx=5, pady=6, sticky="nw")
            txt = tk.Text(zone, width=38, height=3, font=FONT_TEXTE, relief="solid", bd=1)
            txt.grid(row=i+1, column=1, padx=5, pady=6, sticky="w")
            champs_texte[key] = txt

        champs_texte["allergies"].insert("1.0", infos[0] or "")
        champs_texte["atcd_med"].insert("1.0", infos[1] or "")
        champs_texte["atcd_chir"].insert("1.0", infos[2] or "")

        def sauvegarder():
            allergies = champs_texte["allergies"].get("1.0", "end").strip()
            atcd_med = champs_texte["atcd_med"].get("1.0", "end").strip()
            atcd_chir = champs_texte["atcd_chir"].get("1.0", "end").strip()
            groupe = groupe_combo.get()
            patient.modifier_infos_medicales(pid, allergies, atcd_med, atcd_chir, groupe)
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "modification", "patients", pid,
                               f"Infos médicales de {vals[1]} {vals[2]}")
            messagebox.showinfo("Succès", "Informations médicales enregistrées.", parent=popup)
            popup.destroy()

        tk.Button(popup, text="Enregistrer", command=sauvegarder, bg=C_PRIMAIRE, fg="white",
                  font=FONT_TEXTE, padx=15, pady=5).pack(pady=12)

    def _vider(self):
        for w in self.entries.values():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                w.delete(0, tk.END)

    def _exporter_csv(self):
        dest = filedialog.asksaveasfilename(title="Exporter les patients", defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv"), ("Tous", "*.*")])
        if not dest:
            return
        try:
            with open(dest, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["CNI", "Nom", "Prénom", "Sexe", "Date naissance",
                                  "Téléphone", "Adresse", "Date inscription"])
                for row_id in self.tableau.get_children():
                    writer.writerow(self.tableau.item(row_id, "values"))
            messagebox.showinfo("Succès", f"Patients exportés vers :\n{dest}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
