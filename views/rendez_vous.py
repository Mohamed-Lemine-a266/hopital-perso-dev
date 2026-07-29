import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import C_FOND, C_PRIMAIRE, C_DANGER, C_SUCCES, C_AVERTISSEMENT, JOURS_EN_FR
from models import rendez_vous, medecin, specialite, patient, file_attente, parametres, audit, absence
from views.widgets import DateEntry, HeureEntry
import session


class VueRendezVous:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        self.medecin_verrouille = session.medecin_id_courant()

        tk.Label(self.frame, text="Gestion des rendez-vous", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=5)

        tk.Label(zone_form, text="CNI patient :", bg=C_FOND).grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.cni_entry = tk.Entry(zone_form, width=18)
        self.cni_entry.grid(row=0, column=1, padx=5, pady=4)
        self.cni_entry.bind("<Return>", lambda e: self.chercher())
        tk.Button(zone_form, text="Chercher", command=self.chercher, bg="#468FAF", fg="white").grid(
            row=0, column=2, padx=5)
        self.pat_label = tk.Label(zone_form, text="", bg=C_FOND, fg=C_PRIMAIRE, font=("Arial", 9, "italic"))
        self.pat_label.grid(row=0, column=3, columnspan=3, padx=5)

        if self.medecin_verrouille:
            m = medecin.obtenir_par_id(self.medecin_verrouille)
            self.meds_data = [m] if m else []
            tk.Label(zone_form, text="Médecin :", bg=C_FOND).grid(row=1, column=0, padx=5, pady=4, sticky="w")
            tk.Label(zone_form, text=f"Dr. {m[1]} {m[2]} — {m[5]}" if m else "—",
                     bg=C_FOND, font=("Arial", 10, "bold"), fg=C_PRIMAIRE).grid(
                row=1, column=1, columnspan=3, padx=5, pady=4, sticky="w")
        else:
            tk.Label(zone_form, text="Spécialité :", bg=C_FOND).grid(row=1, column=0, padx=5, pady=4, sticky="w")
            self.specs_data = specialite.charger_toutes()
            self.spec_combo = ttk.Combobox(zone_form, values=[s[1] for s in self.specs_data],
                                            state="readonly", width=18)
            self.spec_combo.grid(row=1, column=1, padx=5, pady=4)
            self.spec_combo.bind("<<ComboboxSelected>>", self.charger_meds)

            tk.Label(zone_form, text="Médecin :", bg=C_FOND).grid(row=1, column=2, padx=5, pady=4)
            self.meds_data = []
            self.med_combo = ttk.Combobox(zone_form, state="readonly", width=22)
            self.med_combo.grid(row=1, column=3, padx=5, pady=4)

        tk.Label(zone_form, text="Date (AAAA-MM-JJ) :", bg=C_FOND).grid(row=2, column=0, padx=5, pady=4, sticky="w")
        self.date_entry = DateEntry(zone_form, width=11)
        self.date_entry.grid(row=2, column=1, padx=5, pady=4, sticky="w")

        tk.Label(zone_form, text="Heure (HH:MM) :", bg=C_FOND).grid(row=2, column=2, padx=5, pady=4)
        self.heure_entry = HeureEntry(zone_form, heure_defaut="09:00")
        self.heure_entry.grid(row=2, column=3, padx=5, pady=4, sticky="w")

        tk.Label(zone_form, text="Durée (min) :", bg=C_FOND).grid(row=2, column=4, padx=5, pady=4)
        self.duree_entry = tk.Entry(zone_form, width=5)
        self.duree_entry.grid(row=2, column=5, padx=5, pady=4, sticky="w")
        self.duree_entry.insert(0, str(parametres.duree_rdv()))

        tk.Label(zone_form, text="Motif :", bg=C_FOND).grid(row=3, column=0, padx=5, pady=4, sticky="w")
        self.motif_entry = tk.Entry(zone_form, width=50)
        self.motif_entry.grid(row=3, column=1, columnspan=5, padx=5, pady=4, sticky="w")

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=6)
        for txt, cmd, bg in [("Planifier", self.planifier, C_PRIMAIRE),
                               ("Patient arrivé", self.patient_arrive, C_SUCCES),
                               ("Annuler", self.annuler, C_AVERTISSEMENT),
                               ("Terminé", self.terminer, "#27AE60"),
                               ("Supprimer", self.supprimer_rdv, C_DANGER)]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white", padx=8).pack(side="left", padx=4)

        zone_flt = tk.Frame(self.frame, bg=C_FOND)
        zone_flt.pack(pady=3)
        self.filtre_var = tk.StringVar(value="aujourd_hui")
        for txt, val in [("Aujourd'hui", "aujourd_hui"), ("Tous", "tous")]:
            tk.Radiobutton(zone_flt, text=txt, variable=self.filtre_var, value=val,
                           bg=C_FOND, command=self.charger_tableau).pack(side="left", padx=8)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=5, fill="both", expand=True, padx=15)

        cols = ("cni", "patient", "medecin", "specialite", "date_heure", "duree", "motif", "statut")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=10)
        for c, t, w in [("cni","CNI",80),("patient","Patient",120),("medecin","Médecin",120),
                         ("specialite","Spécialité",100),("date_heure","Date/Heure",120),
                         ("duree","Durée",50),("motif","Motif",130),("statut","Statut",75)]:
            self.tableau.heading(c, text=t, command=lambda col=c: self._trier(col))
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.patient_id = None
        self.charger_tableau()

    def chercher(self):
        cni = self.cni_entry.get().strip()
        if not cni:
            return
        p = patient.rechercher_par_cni(cni)
        if p:
            self.patient_id = p[0]
            self.pat_label.config(text=f"{p[2]} {p[3]} (CNI: {p[1]})")
        else:
            self.patient_id = None
            self.pat_label.config(text="Patient introuvable.")

    def charger_meds(self, event=None):
        idx = self.spec_combo.current()
        if idx < 0:
            return
        self.meds_data = medecin.charger_disponibles_par_specialite(self.specs_data[idx][0])
        if not self.meds_data:
            self.med_combo["values"] = []
            self.med_combo.set("")
            messagebox.showinfo("Information", "Aucun médecin disponible dans cette spécialité.")
            return
        labels = []
        for m in self.meds_data:
            nb = file_attente.compter_en_attente_par_medecin(m[0])
            labels.append(f"Dr. {m[1]} {m[2]} ({nb} en attente)")
        self.med_combo["values"] = labels
        self.med_combo.set("")

    def _medecin_selectionne(self):
        """Renvoie le tuple médecin sélectionné, ou le médecin verrouillé si applicable."""
        if self.medecin_verrouille:
            return self.meds_data[0] if self.meds_data else None
        idx = self.med_combo.current()
        return self.meds_data[idx] if idx >= 0 else None

    def planifier(self):
        if self.patient_id is None:
            messagebox.showwarning("Patient requis", "Cherchez un patient par CNI d'abord.")
            return
        m = self._medecin_selectionne()
        if m is None:
            messagebox.showwarning("Médecin requis", "Sélectionnez une spécialité puis un médecin.")
            return
        date_str = self.date_entry.get().strip()
        heure_str = self.heure_entry.get().strip()
        if not date_str or not heure_str:
            messagebox.showwarning("Date requise", "La date et l'heure sont obligatoires.")
            return
        date_heure = f"{date_str} {heure_str}"
        try:
            dt = datetime.strptime(date_heure, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showwarning("Format invalide", "Format attendu : AAAA-MM-JJ et HH:MM")
            return
        if dt < datetime.now():
            messagebox.showwarning("Date passée", "Impossible de planifier dans le passé.")
            return

        mid = m[0]

        jour_fr = JOURS_EN_FR.get(dt.strftime("%a"), "")
        jours_ok = m[5].split(",") if m[5] else []
        if jour_fr and jour_fr not in jours_ok:
            messagebox.showwarning("Jour non travaillé", f"Dr. {m[1]} {m[2]} ne travaille pas le {jour_fr}.")
            return

        heure_rdv = dt.strftime("%H:%M")
        if heure_rdv < m[6] or heure_rdv >= m[7]:
            messagebox.showwarning("Hors horaires", f"Horaires : {m[6]} — {m[7]}.")
            return

        date_rdv_str = dt.strftime("%Y-%m-%d")
        if absence.est_absent_a_la_date(mid, date_rdv_str):
            messagebox.showwarning("Médecin absent",
                f"Dr. {m[1]} {m[2]} a une absence planifiée à cette date.")
            return

        try:
            duree = int(self.duree_entry.get().strip())
        except ValueError:
            duree = parametres.duree_rdv()

        if rendez_vous.conflit_horaire(mid, date_heure, duree):
            messagebox.showwarning("Conflit horaire", "Ce médecin a déjà un RDV qui chevauche ce créneau.")
            return

        if rendez_vous.existe_deja(self.patient_id, mid, date_heure):
            messagebox.showwarning("Doublon", "Ce rendez-vous existe déjà.")
            return

        motif = self.motif_entry.get().strip()
        try:
            rid = rendez_vous.ajouter(self.patient_id, mid, date_heure, duree, motif)
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "création", "rendez_vous", rid, f"Dr. {m[1]} {m[2]} — {date_heure}")
            messagebox.showinfo("Succès", "Rendez-vous planifié.")
            self.charger_tableau()
            self.motif_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.heure_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def patient_arrive(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un rendez-vous.")
            return
        vals = self.tableau.item(sel[0], "values")
        if vals[7] not in ("planifié", "confirmé"):
            messagebox.showwarning("Action impossible", "Ce RDV n'est plus actif.")
            return

        rdv_data = rendez_vous.obtenir_par_id(sel[0])
        if not rdv_data:
            return
        pid, mid = rdv_data[1], rdv_data[2]

        m = medecin.obtenir_par_id(mid)
        if not m:
            return
        spec_id = m[4]

        if file_attente.patient_deja_en_attente(pid, spec_id):
            messagebox.showwarning("Déjà en file", "Ce patient est déjà dans la file de cette spécialité.")
            return

        dh = datetime.now().strftime("%Y-%m-%d %H:%M")
        file_attente.ajouter(pid, mid, dh, vals[6] or "RDV")
        rendez_vous.changer_statut(sel[0], "confirmé")
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "patient arrivé", "rendez_vous", sel[0], f"{vals[1]} — {vals[4]}")
        self.charger_tableau()
        messagebox.showinfo("Succès", f"Patient placé dans la file — {vals[4]}")

    def annuler(self):
        sel = self.tableau.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmation", "Annuler ce rendez-vous ?"):
            return
        vals = self.tableau.item(sel[0], "values")
        rendez_vous.changer_statut(sel[0], "annulé")
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "annulation", "rendez_vous", sel[0], f"{vals[1]} — {vals[4]}")
        self.charger_tableau()

    def terminer(self):
        sel = self.tableau.selection()
        if not sel:
            return
        vals = self.tableau.item(sel[0], "values")
        rendez_vous.changer_statut(sel[0], "terminé")
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "terminé", "rendez_vous", sel[0], f"{vals[1]} — {vals[4]}")
        self.charger_tableau()

    def supprimer_rdv(self):
        sel = self.tableau.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce rendez-vous ?"):
            return
        vals = self.tableau.item(sel[0], "values")
        rendez_vous.supprimer(sel[0])
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "suppression", "rendez_vous", sel[0], f"{vals[1]} — {vals[4]}")
        self.charger_tableau()

    def charger_tableau(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        if self.filtre_var.get() == "aujourd_hui":
            data = rendez_vous.charger_aujourd_hui()
        else:
            data = rendez_vous.charger_tous()
        for r in data:
            self.tableau.insert("", "end", iid=r[0],
                values=(r[1], r[2], r[3], r[4], r[5], r[6], r[7] or "", r[8]))

    def _trier(self, col):
        data = [(self.tableau.set(k, col), k) for k in self.tableau.get_children()]
        data.sort()
        for i, (_, k) in enumerate(data):
            self.tableau.move(k, "", i)