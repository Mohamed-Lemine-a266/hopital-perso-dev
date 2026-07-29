import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from datetime import datetime
from config import C_FOND, C_PRIMAIRE, C_DANGER, C_SUCCES, C_AVERTISSEMENT, JOURS_EN_FR
from models import file_attente, medecin, specialite, consultation, audit, rendez_vous, absence, parametres
from views.ecran_public import EcranPublic
from views.widgets import DateEntry, HeureEntry
import session


class VueFileAttente:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="File d'attente", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        # ── Filtres : spécialité + médecin ──
        zone_filtre = tk.Frame(self.frame, bg=C_FOND)
        zone_filtre.pack(pady=5)

        tk.Label(zone_filtre, text="Spécialité :", bg=C_FOND).grid(row=0, column=0, padx=5)
        self.specs_data = specialite.charger_toutes()
        self.filtre_spec = ttk.Combobox(zone_filtre, values=["Toutes"] + [s[1] for s in self.specs_data],
                                         state="readonly", width=20)
        self.filtre_spec.grid(row=0, column=1, padx=5)
        self.filtre_spec.set("Toutes")
        self.filtre_spec.bind("<<ComboboxSelected>>", self._on_filtre_spec)

        tk.Label(zone_filtre, text="Médecin :", bg=C_FOND).grid(row=0, column=2, padx=5)
        self.meds_filtre_data = []
        self.filtre_med = ttk.Combobox(zone_filtre, values=["Tous"], state="readonly", width=22)
        self.filtre_med.grid(row=0, column=3, padx=5)
        self.filtre_med.set("Tous")
        self.filtre_med.bind("<<ComboboxSelected>>", lambda e: self.charger())

        tk.Button(zone_filtre, text="Actualiser", command=self.charger,
                  bg=C_PRIMAIRE, fg="white", padx=8).grid(row=0, column=4, padx=10)

        # ── Tableau ──
        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=5, fill="both", expand=True, padx=15)

        cols = ("ticket", "cni", "nom", "prenom", "medecin", "specialite", "arrivee", "priorite", "statut", "motif")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=12)
        for c, t, w in [("ticket","Ticket",55),("cni","CNI",85),("nom","Nom",90),("prenom","Prénom",90),
                         ("medecin","Médecin",120),("specialite","Spécialité",100),
                         ("arrivee","Arrivée",115),("priorite","Priorité",75),
                         ("statut","Statut",90),("motif","Motif",100)]:
            self.tableau.heading(c, text=t, command=lambda col=c: self._trier(col))
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Boutons d'action ──
        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=8)

        for txt, cmd, bg in [
            ("Appeler suivant", self.appeler_suivant, C_PRIMAIRE),
            ("Patient absent", self.patient_absent, C_AVERTISSEMENT),
            ("Début consultation", self.debut_consultation, C_SUCCES),
            ("Terminer", self.terminer, "#8E44AD"),
            ("Créer RDV", self.creer_rdv, "#2980B9"),
            ("Retirer", self.retirer, C_DANGER),
            ("Imprimer ticket", self.imprimer_ticket, "#555"),
            ("Écran public", self.ouvrir_ecran_public, "#1B3A4B"),
        ]:
            tk.Button(zone_btn, text=txt, command=cmd, bg=bg, fg="white",
                      padx=8, font=("Arial", 9)).pack(side="left", padx=4)

        self.charger()

    def _on_filtre_spec(self, event=None):
        idx = self.filtre_spec.current()
        if idx <= 0:
            self.meds_filtre_data = []
            self.filtre_med["values"] = ["Tous"]
            self.filtre_med.set("Tous")
        else:
            spec_id = self.specs_data[idx - 1][0]
            self.meds_filtre_data = medecin.charger_par_specialite(spec_id)
            self.filtre_med["values"] = ["Tous"] + [f"Dr. {m[1]} {m[2]}" for m in self.meds_filtre_data]
            self.filtre_med.set("Tous")
        self.charger()

    def charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)

        spec_idx = self.filtre_spec.current()
        med_idx = self.filtre_med.current()

        if med_idx > 0 and self.meds_filtre_data:
            data = file_attente.charger_par_medecin(self.meds_filtre_data[med_idx - 1][0])
        elif spec_idx > 0:
            data = file_attente.charger_par_specialite(self.specs_data[spec_idx - 1][0])
        else:
            data = file_attente.charger_toute()

        for f in data:
            tags = ()
            if f[8] == "très urgente":
                tags = ("urgent",)
            elif f[8] == "urgente":
                tags = ("avertissement",)
            self.tableau.insert("", "end", iid=f[0],
                values=(f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10] or ""),
                tags=tags)

        self.tableau.tag_configure("urgent", background="#FADBD8")
        self.tableau.tag_configure("avertissement", background="#FDEBD0")

    def _sel(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez une entrée dans la file.")
            return None
        return sel[0]

    def _med_id_de_selection(self):
        sel = self._sel()
        if not sel:
            return None, None
        vals = self.tableau.item(sel, "values")
        med_nom = vals[4]
        for m in medecin.charger_tous():
            if f"{m[1]} {m[2]}" == med_nom:
                return m[0], sel
        return None, sel

    def appeler_suivant(self):
        if not session.exiger_permission("file_attente_gerer"):
            return
        mid, sel = self._med_id_de_selection()
        if mid is None:
            return
        fid = file_attente.appeler_suivant(mid)
        if fid is None:
            messagebox.showinfo("File vide", "Aucun patient en attente pour ce médecin.")
            return
        self.charger()
        info = file_attente.obtenir_info(fid)
        if info:
            messagebox.showinfo("Patient appelé",
                f"Ticket: Le prochain patient a été appelé.\n{info[3]} {info[4]} — {info[7]}")

    def patient_absent(self):
        if not session.exiger_permission("file_attente_gerer"):
            return
        sel = self._sel()
        if not sel:
            return
        vals = self.tableau.item(sel, "values")
        if vals[8] != "appelé":
            messagebox.showwarning("Action impossible", "Ce bouton s'applique uniquement aux patients 'appelé'.")
            return
        file_attente.changer_statut(sel, "en attente")
        self.charger()
        messagebox.showinfo("Remis en file", f"{vals[2]} {vals[3]} a été remis(e) en file d'attente.")

    def debut_consultation(self):
        if not session.exiger_permission("file_attente_gerer"):
            return
        sel = self._sel()
        if not sel:
            return
        vals = self.tableau.item(sel, "values")
        if vals[8] != "appelé":
            messagebox.showwarning("Action impossible", "Le patient doit d'abord être 'appelé'.")
            return
        file_attente.changer_statut(sel, "en consultation")
        self.charger()

    def terminer(self):
        if not session.exiger_permission("file_attente_gerer"):
            return
        sel = self._sel()
        if not sel:
            return
        vals = self.tableau.item(sel, "values")
        if vals[8] not in ("en consultation", "appelé"):
            messagebox.showwarning("Action impossible", "Le patient doit être 'appelé' ou 'en consultation'.")
            return
        info = file_attente.obtenir_info(sel)
        if not info:
            return
        file_attente.changer_statut(sel, "terminé")
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "fin consultation", "file_attente", sel, f"{info[3]} {info[4]}")
        self._ouvrir_popup_consultation(info)
        self.charger()

    def _ouvrir_popup_consultation(self, info):
        """Popup Toplevel pré-remplie pour saisir la consultation."""
        popup = Toplevel()
        popup.title("Enregistrer la consultation")
        popup.geometry("500x350")
        popup.configure(bg=C_FOND)
        popup.grab_set()

        patient_id, medecin_id = info[1], info[2]
        tk.Label(popup, text=f"Patient : {info[3]} {info[4]}", font=("Arial", 12, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(15, 3))
        tk.Label(popup, text=f"Médecin : Dr. {info[5]} {info[6]} — {info[7]}",
                 font=("Arial", 10), bg=C_FOND).pack(pady=(0, 10))

        zone = tk.Frame(popup, bg=C_FOND)
        zone.pack(pady=5, padx=20, fill="x")

        entries = {}
        for i, (lbl, h) in enumerate([("Diagnostic :", 1), ("Traitement :", 1), ("Observations :", 1)]):
            tk.Label(zone, text=lbl, bg=C_FOND, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            e = tk.Entry(zone, width=45)
            e.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            entries[lbl] = e

        def sauvegarder():
            diag = entries["Diagnostic :"].get().strip()
            if diag == "":
                messagebox.showwarning("Obligatoire", "Le diagnostic est obligatoire.", parent=popup)
                return
            try:
                consultation.ajouter(patient_id, medecin_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    diag, entries["Traitement :"].get().strip(),
                    entries["Observations :"].get().strip())
                messagebox.showinfo("Succès", "Consultation enregistrée.", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=popup)

        tk.Button(popup, text="Enregistrer la consultation", command=sauvegarder,
                  bg=C_SUCCES, fg="white", font=("Arial", 11), padx=15, pady=5).pack(pady=15)

    def creer_rdv(self):
        """Ouvre une popup pour planifier un rendez-vous à partir du patient
        sélectionné dans la file d'attente — CNI et médecin déjà connus,
        aucune ressaisie nécessaire."""
        if not session.exiger_permission("rdv_gerer"):
            return
        sel = self._sel()
        if not sel:
            return
        info = file_attente.obtenir_info(sel)
        if not info:
            return

        patient_id, medecin_id = info[1], info[2]
        m = medecin.obtenir_par_id(medecin_id)
        if not m:
            messagebox.showerror("Erreur", "Médecin introuvable.")
            return

        popup = Toplevel()
        popup.title("Créer un rendez-vous")
        popup.geometry("480x380")
        popup.configure(bg=C_FOND)
        popup.grab_set()

        tk.Label(popup, text=f"Patient : {info[3]} {info[4]}", font=("Arial", 12, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(15, 3))
        tk.Label(popup, text=f"Médecin : Dr. {info[5]} {info[6]} — {info[7]}",
                 font=("Arial", 10), bg=C_FOND).pack(pady=(0, 12))

        zone = tk.Frame(popup, bg=C_FOND)
        zone.pack(pady=5, padx=20, fill="x")

        tk.Label(zone, text="Date :", bg=C_FOND).grid(row=0, column=0, padx=5, pady=6, sticky="w")
        date_entry = DateEntry(zone, width=11)
        date_entry.grid(row=0, column=1, padx=5, pady=6, sticky="w")

        tk.Label(zone, text="Heure :", bg=C_FOND).grid(row=0, column=2, padx=5, pady=6, sticky="w")
        heure_entry = HeureEntry(zone, heure_defaut="09:00")
        heure_entry.grid(row=0, column=3, padx=5, pady=6, sticky="w")

        tk.Label(zone, text="Durée (min) :", bg=C_FOND).grid(row=1, column=0, padx=5, pady=6, sticky="w")
        duree_entry = tk.Entry(zone, width=6)
        duree_entry.insert(0, str(parametres.duree_rdv()))
        duree_entry.grid(row=1, column=1, padx=5, pady=6, sticky="w")

        tk.Label(zone, text="Motif :", bg=C_FOND).grid(row=2, column=0, padx=5, pady=6, sticky="w")
        motif_entry = tk.Entry(zone, width=35)
        motif_entry.insert(0, info[8] if len(info) > 8 and info[8] else "")
        motif_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=6, sticky="w")

        def valider():
            date_str = date_entry.get().strip()
            heure_str = heure_entry.get().strip()
            if not date_str or not heure_str:
                messagebox.showwarning("Champs requis", "La date et l'heure sont obligatoires.", parent=popup)
                return
            date_heure = f"{date_str} {heure_str}"
            try:
                dt = datetime.strptime(date_heure, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showwarning("Format invalide", "Format attendu : AAAA-MM-JJ et HH:MM", parent=popup)
                return
            if dt < datetime.now():
                messagebox.showwarning("Date passée", "Impossible de planifier dans le passé.", parent=popup)
                return

            jour_fr = JOURS_EN_FR.get(dt.strftime("%a"), "")
            jours_ok = m[6].split(",") if m[6] else []
            if jour_fr and jour_fr not in jours_ok:
                messagebox.showwarning("Jour non travaillé",
                    f"Dr. {m[1]} {m[2]} ne travaille pas le {jour_fr}.", parent=popup)
                return

            heure_rdv = dt.strftime("%H:%M")
            if heure_rdv < m[7] or heure_rdv >= m[8]:
                messagebox.showwarning("Hors horaires", f"Horaires : {m[7]} — {m[8]}.", parent=popup)
                return

            if absence.est_absent_a_la_date(medecin_id, dt.strftime("%Y-%m-%d")):
                messagebox.showwarning("Médecin absent",
                    f"Dr. {m[1]} {m[2]} a une absence planifiée à cette date.", parent=popup)
                return

            try:
                duree = int(duree_entry.get().strip())
            except ValueError:
                duree = parametres.duree_rdv()

            if rendez_vous.conflit_horaire(medecin_id, date_heure, duree):
                messagebox.showwarning("Conflit horaire",
                    "Ce médecin a déjà un RDV qui chevauche ce créneau.", parent=popup)
                return

            if rendez_vous.existe_deja(patient_id, medecin_id, date_heure):
                messagebox.showwarning("Doublon", "Ce rendez-vous existe déjà.", parent=popup)
                return

            try:
                rid = rendez_vous.ajouter(patient_id, medecin_id, date_heure, duree,
                                          motif_entry.get().strip())
                audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                                   "création", "rendez_vous", rid,
                                   f"{info[3]} {info[4]} — Dr. {m[1]} {m[2]} — {date_heure}")
                messagebox.showinfo("Succès", "Rendez-vous créé.", parent=popup)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=popup)

        tk.Button(popup, text="Créer le rendez-vous", command=valider,
                  bg=C_SUCCES, fg="white", font=("Arial", 11), padx=15, pady=5).pack(pady=15)

    def retirer(self):
        if not session.exiger_permission("file_attente_gerer"):
            return
        sel = self._sel()
        if not sel:
            return
        vals = self.tableau.item(sel, "values")
        if not messagebox.askyesno("Confirmation", "Retirer ce patient de la file ?"):
            return
        file_attente.retirer(sel)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "retrait file", "file_attente", sel, f"{vals[2]} {vals[3]}")
        self.charger()

    def imprimer_ticket(self):
        sel = self._sel()
        if not sel:
            return
        info = file_attente.obtenir_info(sel)
        vals = self.tableau.item(sel, "values")
        if info and vals:
            from utils.impression import imprimer_ticket
            imprimer_ticket(vals[0], info[3], info[4], info[7],
                            f"Dr. {info[5]} {info[6]}", vals[6], vals[7])

    def _trier(self, col):
        data = [(self.tableau.set(k, col), k) for k in self.tableau.get_children()]
        data.sort()
        for i, (_, k) in enumerate(data):
            self.tableau.move(k, "", i)

    def ouvrir_ecran_public(self):
        EcranPublic(self.frame.winfo_toplevel())