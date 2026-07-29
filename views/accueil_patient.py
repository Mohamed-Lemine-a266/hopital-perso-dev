import tkinter as tk
import re
from tkinter import ttk, messagebox
from datetime import datetime
from config import C_FOND, C_PRIMAIRE, C_SUCCES, C_AVERTISSEMENT, SEXES, PRIORITES, DELAI_RECHERCHE
from models import patient, medecin, specialite, file_attente, parametres, audit
from views.widgets import DateEntry
import session


class VueAccueilPatient:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)
        self.patient_id = None
        self.mode = "nouveau"
        self._timer = None

        tk.Label(self.frame, text="Accueil Patient", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 4))
        tk.Label(self.frame, text="Recherchez un patient par CNI ou enregistrez un nouveau patient.",
                 font=("Arial", 9, "italic"), bg=C_FOND, fg="#888").pack(pady=(0, 6))

        # ── Recherche CNI ──
        zone_rech = tk.Frame(self.frame, bg=C_FOND)
        zone_rech.pack(pady=4)

        tk.Label(zone_rech, text="N° CNI :", bg=C_FOND, font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)
        self.cni_rech = tk.Entry(zone_rech, width=22, font=("Arial", 11))
        self.cni_rech.grid(row=0, column=1, padx=5)
        self.cni_rech.bind("<Return>", lambda e: self._rechercher_cni())
        self.cni_rech.bind("<KeyRelease>", self._recherche_instantanee)

        tk.Button(zone_rech, text="Rechercher", command=self._rechercher_cni,
                  bg=C_PRIMAIRE, fg="white", font=("Arial", 10), padx=10).grid(row=0, column=2, padx=5)
        tk.Button(zone_rech, text="Nouveau patient", command=self._mode_nouveau,
                  bg=C_SUCCES, fg="white", font=("Arial", 10), padx=8).grid(row=0, column=3, padx=5)

        # Case sans CNI
        self.sans_cni_var = tk.BooleanVar(value=False)
        self.sans_cni_cb = tk.Checkbutton(zone_rech, text="Sans CNI (enfant/étranger)",
                                           variable=self.sans_cni_var, bg=C_FOND,
                                           command=self._toggle_sans_cni)
        self.sans_cni_cb.grid(row=0, column=4, padx=8)

        self.status_label = tk.Label(self.frame, text="", bg=C_FOND, font=("Arial", 10, "italic"))
        self.status_label.pack(pady=2)

        # ── Formulaire patient ──
        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=4)

        self.entries = {}
        champs = [
            ("N° CNI :", 0, 0), ("Nom :", 0, 2), ("Prénom :", 0, 4),
            ("Sexe :", 1, 0), ("Date naissance :", 1, 2), ("Téléphone :", 1, 4),
            ("Adresse :", 2, 0),
        ]
        for label, row, col in champs:
            tk.Label(zone_form, text=label, bg=C_FOND, font=("Arial", 10)).grid(
                row=row, column=col, padx=4, pady=3, sticky="w")
            if label == "Sexe :":
                w = ttk.Combobox(zone_form, values=SEXES, state="readonly", width=14)
            elif label == "Adresse :":
                w = tk.Entry(zone_form, width=48)
                w.grid(row=row, column=col + 1, columnspan=5, padx=4, pady=3, sticky="w")
                self.entries[label] = w
                continue
            elif label == "Date naissance :":
                w = DateEntry(zone_form, width=11)
                w.grid(row=row, column=col + 1, padx=4, pady=3, sticky="w")
                self.entries[label] = w
                continue
            else:
                w = tk.Entry(zone_form, width=17)
            w.grid(row=row, column=col + 1, padx=4, pady=3)
            self.entries[label] = w

        # ── Orientation vers la file ──
        tk.Frame(self.frame, bg="#CCC", height=1).pack(fill="x", padx=30, pady=8)
        tk.Label(self.frame, text="Orientation vers la file d'attente",
                 font=("Arial", 12, "bold"), bg=C_FOND, fg="#333").pack(pady=(3, 4))

        zone_orient = tk.Frame(self.frame, bg=C_FOND)
        zone_orient.pack(pady=4)

        tk.Label(zone_orient, text="Spécialité :", bg=C_FOND, font=("Arial", 10)).grid(
            row=0, column=0, padx=5, pady=4, sticky="w")
        self.specs_data = specialite.charger_toutes()
        self.spec_combo = ttk.Combobox(zone_orient, values=[s[1] for s in self.specs_data],
                                        state="readonly", width=20)
        self.spec_combo.grid(row=0, column=1, padx=5, pady=4)
        self.spec_combo.bind("<<ComboboxSelected>>", self._charger_medecins)

        tk.Label(zone_orient, text="Médecin :", bg=C_FOND, font=("Arial", 10)).grid(
            row=0, column=2, padx=5, pady=4)
        self.meds_data = []
        self.med_combo = ttk.Combobox(zone_orient, state="readonly", width=26)
        self.med_combo.grid(row=0, column=3, padx=5, pady=4)

        tk.Label(zone_orient, text="Priorité :", bg=C_FOND, font=("Arial", 10)).grid(
            row=1, column=0, padx=5, pady=4, sticky="w")
        self.priorite_combo = ttk.Combobox(zone_orient, values=PRIORITES, state="readonly", width=14)
        self.priorite_combo.grid(row=1, column=1, padx=5, pady=4, sticky="w")
        self.priorite_combo.set("normale")

        tk.Label(zone_orient, text="Motif :", bg=C_FOND, font=("Arial", 10)).grid(
            row=1, column=2, padx=5, pady=4)
        self.motif_entry = tk.Entry(zone_orient, width=30)
        self.motif_entry.grid(row=1, column=3, padx=5, pady=4, sticky="w")

        # ── Bouton principal ──
        self.btn_action = tk.Button(self.frame, text="Enregistrer et placer en file d'attente",
                                     command=self._action_principale, bg=C_PRIMAIRE,
                                     fg="white", font=("Arial", 11, "bold"), padx=20, pady=5)
        self.btn_action.pack(pady=10)

        # Raccourci Échap pour vider
        self.frame.winfo_toplevel().bind("<Escape>", lambda e: self._vider_tout())

    def _recherche_instantanee(self, event):
        if self._timer:
            self.frame.after_cancel(self._timer)
        self._timer = self.frame.after(DELAI_RECHERCHE, self._rechercher_cni)

    def _rechercher_cni(self):
        cni = self.cni_rech.get().strip()
        if cni == "":
            return
        p = patient.rechercher_par_cni(cni)
        if p:
            self.patient_id = p[0]
            self.mode = "existant"
            self._vider_formulaire()
            self.entries["N° CNI :"].insert(0, p[1])
            self.entries["N° CNI :"].config(state="readonly")
            self.entries["Nom :"].insert(0, p[2])
            self.entries["Prénom :"].insert(0, p[3])
            if p[4]: self.entries["Sexe :"].set(p[4])
            if p[5]: self.entries["Date naissance :"].insert(0, p[5])
            if p[6]: self.entries["Téléphone :"].insert(0, p[6])
            if p[7]: self.entries["Adresse :"].insert(0, p[7])
            self.status_label.config(text=f"Patient trouvé : {p[2]} {p[3]} (CNI: {p[1]})", fg=C_SUCCES)
            self.btn_action.config(text="Placer en file d'attente")
        else:
            self.status_label.config(text="Patient non trouvé. Remplissez le formulaire.", fg=C_AVERTISSEMENT)
            self._mode_nouveau()
            self.entries["N° CNI :"].delete(0, tk.END)
            self.entries["N° CNI :"].insert(0, cni)

    def _mode_nouveau(self):
        self.patient_id = None
        self.mode = "nouveau"
        self._vider_formulaire()
        self.entries["N° CNI :"].config(state="normal")
        self.sans_cni_var.set(False)
        self.status_label.config(text="Mode : Nouveau patient", fg=C_PRIMAIRE)
        self.btn_action.config(text="Enregistrer et placer en file d'attente")

    def _toggle_sans_cni(self):
        if self.sans_cni_var.get():
            pref = parametres.prefixe()
            numero = patient.prochain_numero_auto(pref)
            self.entries["N° CNI :"].config(state="normal")
            self.entries["N° CNI :"].delete(0, tk.END)
            self.entries["N° CNI :"].insert(0, numero)
            self.entries["N° CNI :"].config(state="readonly")
        else:
            self.entries["N° CNI :"].config(state="normal")
            self.entries["N° CNI :"].delete(0, tk.END)

    def _charger_medecins(self, event=None):
        idx = self.spec_combo.current()
        if idx < 0:
            return
        spec_id = self.specs_data[idx][0]
        self.meds_data = medecin.charger_disponibles_par_specialite(spec_id)
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
        # Auto-sélectionner le médecin avec le moins de patients
        min_nb = float('inf')
        min_idx = 0
        for i, m in enumerate(self.meds_data):
            nb = file_attente.compter_en_attente_par_medecin(m[0])
            if nb < min_nb:
                min_nb = nb
                min_idx = i
        self.med_combo.current(min_idx)

    def _valider_telephone(self, tel):
        if tel == "":
            return True
        return re.fullmatch(r"[0-9+\s\-]{7,15}", tel) is not None

    def _action_principale(self):
        cni = self.entries["N° CNI :"].get().strip()
        nom = self.entries["Nom :"].get().strip()
        prenom = self.entries["Prénom :"].get().strip()
        sexe = self.entries["Sexe :"].get()
        dn = self.entries["Date naissance :"].get().strip()
        tel = self.entries["Téléphone :"].get().strip()
        adresse = self.entries["Adresse :"].get().strip()
        motif = self.motif_entry.get().strip()
        priorite = self.priorite_combo.get() or "normale"

        if cni == "" or nom == "" or prenom == "":
            messagebox.showwarning("Champs obligatoires", "Le N° CNI, le nom et le prénom sont obligatoires.")
            return

        if not patient.format_cni_valide(cni, parametres.prefixe()):
            messagebox.showwarning("CNI invalide",
                "Le format du CNI est invalide.\nIl doit contenir au moins 5 caractères alphanumériques.")
            return

        if not self._valider_telephone(tel):
            messagebox.showwarning("Téléphone invalide", "Le numéro de téléphone n'est pas valide.")
            return

        # Vérifier spécialité et médecin
        spec_idx = self.spec_combo.current()
        if spec_idx < 0:
            messagebox.showwarning("Orientation requise", "Sélectionnez une spécialité.")
            return
        spec_id = self.specs_data[spec_idx][0]

        med_idx = self.med_combo.current()
        if med_idx < 0 or med_idx >= len(self.meds_data):
            messagebox.showwarning("Orientation requise", "Sélectionnez un médecin.")
            return
        med_id = self.meds_data[med_idx][0]

        try:
            if self.mode == "nouveau":
                if patient.cni_existe(cni):
                    messagebox.showwarning("Doublon", f"Le CNI {cni} est déjà enregistré.")
                    return
                date_insc = datetime.now().strftime("%Y-%m-%d")
                pid = patient.ajouter(cni, nom, prenom, sexe, dn, tel, adresse, date_insc)
                self.patient_id = pid
            else:
                pid = self.patient_id
                # Mettre à jour les coordonnées si modifiées
                patient.modifier(pid, cni, nom, prenom, sexe, dn, tel, adresse)

            # Vérifier doublon en file (par spécialité)
            if file_attente.patient_deja_en_attente(pid, spec_id):
                messagebox.showwarning("Doublon", f"{nom} {prenom} est déjà en attente dans cette spécialité.")
                return

            date_h = datetime.now().strftime("%Y-%m-%d %H:%M")
            fid, ticket = file_attente.ajouter(pid, med_id, date_h, motif, priorite)

            if self.mode == "nouveau":
                audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                                   "création", "patients", pid, f"{nom} {prenom} (CNI: {cni})")
            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "placement file", "file_attente", fid, f"{nom} {prenom} — ticket {ticket}")

            med = self.meds_data[med_idx]
            msg = f"{'Enregistré et placé' if self.mode == 'nouveau' else 'Placé'} en file d'attente\n\n"
            msg += f"Ticket : {ticket}\n"
            msg += f"Patient : {nom} {prenom}\nCNI : {cni}\n"
            msg += f"Médecin : Dr. {med[1]} {med[2]}\n"
            msg += f"Spécialité : {self.spec_combo.get()}\n"
            msg += f"Priorité : {priorite}"
            messagebox.showinfo("Succès", msg)
            self._vider_tout()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

    def _vider_formulaire(self):
        for key, w in self.entries.items():
            if isinstance(w, ttk.Combobox):
                w.set("")
            else:
                try:
                    w.config(state="normal")
                except Exception:
                    pass
                w.delete(0, tk.END)

    def _vider_tout(self):
        self._vider_formulaire()
        self.cni_rech.delete(0, tk.END)
        self.spec_combo.set("")
        self.med_combo.set("")
        self.med_combo["values"] = []
        self.motif_entry.delete(0, tk.END)
        self.priorite_combo.set("normale")
        self.sans_cni_var.set(False)
        self.patient_id = None
        self.mode = "nouveau"
        self.status_label.config(text="")
        self.btn_action.config(text="Enregistrer et placer en file d'attente")
