import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import C_FOND, C_PRIMAIRE, C_SUCCES, DELAI_RECHERCHE, FONT_H1, FONT_H3
from models import consultation, medecin, specialite, patient, constantes_vitales, audit
import session


class VueConsultations:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        self.medecin_verrouille = session.medecin_id_courant()

        tk.Label(self.frame, text="Consultations & Historique médical", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        zone_form = tk.Frame(self.frame, bg=C_FOND)
        zone_form.pack(pady=5, fill="x", padx=20)

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
                                            state="readonly", width=16)
            self.spec_combo.grid(row=1, column=1, padx=5, pady=4, sticky="w")
            self.spec_combo.bind("<<ComboboxSelected>>", self.charger_meds)

            tk.Label(zone_form, text="Médecin :", bg=C_FOND).grid(row=1, column=2, padx=5, pady=4)
            self.meds_data = []
            self.med_combo = ttk.Combobox(zone_form, state="readonly", width=20)
            self.med_combo.grid(row=1, column=3, padx=5, pady=4)

        for i, lbl in enumerate(["Diagnostic :", "Traitement :", "Observations :"]):
            tk.Label(zone_form, text=lbl, bg=C_FOND).grid(row=2+i, column=0, padx=5, pady=4, sticky="w")
        self.diag_entry = tk.Entry(zone_form, width=55)
        self.diag_entry.grid(row=2, column=1, columnspan=5, padx=5, pady=4, sticky="w")
        self.trait_entry = tk.Entry(zone_form, width=55)
        self.trait_entry.grid(row=3, column=1, columnspan=5, padx=5, pady=4, sticky="w")
        self.obs_entry = tk.Entry(zone_form, width=55)
        self.obs_entry.grid(row=4, column=1, columnspan=5, padx=5, pady=4, sticky="w")

        tk.Label(zone_form, text="Constantes vitales", font=FONT_H3, bg=C_FOND, fg="#333").grid(
            row=5, column=0, columnspan=6, sticky="w", padx=5, pady=(10, 3))

        self.vitaux = {}
        vitaux_champs = [
            ("Taille (cm) :", "taille", 6, 0), ("Poids (kg) :", "poids", 6, 2),
            ("Température (°C) :", "temperature", 6, 4),
            ("Tension (ex: 12/8) :", "tension", 7, 0), ("Fréq. cardiaque (bpm) :", "freq_card", 7, 2),
            ("Saturation O2 (%) :", "saturation", 7, 4),
        ]
        for label, key, row, col in vitaux_champs:
            tk.Label(zone_form, text=label, bg=C_FOND, font=("Arial", 9)).grid(
                row=row, column=col, padx=5, pady=3, sticky="w")
            e = tk.Entry(zone_form, width=10)
            e.grid(row=row, column=col+1, padx=5, pady=3, sticky="w")
            self.vitaux[key] = e

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=6)
        tk.Button(zone_btn, text="Enregistrer la consultation", command=self.enregistrer,
                  bg=C_PRIMAIRE, fg="white", padx=12).pack(side="left", padx=5)
        tk.Button(zone_btn, text="Voir historique", command=self.voir_historique,
                  bg="#468FAF", fg="white", padx=8).pack(side="left", padx=5)

        self.label_hist = tk.Label(self.frame, text="Historique des consultations",
                                    font=("Arial", 12, "bold"), bg=C_FOND)
        self.label_hist.pack(pady=(8, 4))

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=3, fill="both", expand=True, padx=15)

        cols = ("date", "medecin", "specialite", "diagnostic", "traitement", "observations")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=7)
        for c, t, w in [("date","Date",115),("medecin","Médecin",125),("specialite","Spécialité",100),
                         ("diagnostic","Diagnostic",155),("traitement","Traitement",145),("observations","Obs.",125)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.patient_id = None

    def chercher(self):
        cni = self.cni_entry.get().strip()
        if not cni:
            return
        p = patient.rechercher_par_cni(cni)
        if p:
            self.patient_id = p[0]
            self.pat_label.config(text=f"{p[2]} {p[3]} (CNI: {p[1]})")
            self.voir_historique()
        else:
            self.patient_id = None
            self.pat_label.config(text="Patient introuvable.")

    def charger_meds(self, event=None):
        idx = self.spec_combo.current()
        if idx < 0:
            return
        self.meds_data = medecin.charger_par_specialite(self.specs_data[idx][0])
        self.med_combo["values"] = [f"Dr. {m[1]} {m[2]}" for m in self.meds_data]
        self.med_combo.set("")

    def _medecin_id_selectionne(self):
        if self.medecin_verrouille:
            return self.medecin_verrouille if self.meds_data else None
        idx = self.med_combo.current()
        return self.meds_data[idx][0] if idx >= 0 else None

    def _lire_vitaux(self):
        """Lit et valide les champs de constantes vitales. Renvoie None si un champ est invalide."""
        valeurs = {}
        specs = {
            "taille": float, "poids": float, "temperature": float,
            "freq_card": int, "saturation": int,
        }
        for key, caster in specs.items():
            texte = self.vitaux[key].get().strip()
            if texte == "":
                valeurs[key] = None
                continue
            try:
                valeurs[key] = caster(texte.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Valeur invalide", "La valeur saisie pour ce champ n'est pas un nombre valide.")
                return None
        valeurs["tension"] = self.vitaux["tension"].get().strip() or None
        return valeurs

    def enregistrer(self):
        if self.patient_id is None:
            messagebox.showwarning("Patient requis", "Cherchez un patient par CNI d'abord.")
            return
        medecin_id = self._medecin_id_selectionne()
        if medecin_id is None:
            messagebox.showwarning("Médecin requis", "Sélectionnez un médecin.")
            return
        diag = self.diag_entry.get().strip()
        if not diag:
            messagebox.showwarning("Obligatoire", "Le diagnostic est obligatoire.")
            return

        vitaux = self._lire_vitaux()
        if vitaux is None:
            return

        try:
            date_h = datetime.now().strftime("%Y-%m-%d %H:%M")
            cid = consultation.ajouter(self.patient_id, medecin_id, date_h,
                diag, self.trait_entry.get().strip(), self.obs_entry.get().strip())

            if any(v is not None for v in vitaux.values()):
                constantes_vitales.ajouter(self.patient_id, cid, date_h,
                    vitaux["taille"], vitaux["poids"], vitaux["temperature"],
                    vitaux["tension"], vitaux["freq_card"], vitaux["saturation"])

            audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                               "création", "consultations", cid, f"Diagnostic : {diag}")

            messagebox.showinfo("Succès", "Consultation enregistrée.")
            self.diag_entry.delete(0, tk.END)
            self.trait_entry.delete(0, tk.END)
            self.obs_entry.delete(0, tk.END)
            for e in self.vitaux.values():
                e.delete(0, tk.END)
            self.voir_historique()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def voir_historique(self):
        if self.patient_id is None:
            return
        p = patient.obtenir_par_id(self.patient_id)
        if p:
            self.label_hist.config(text=f"Historique de {p[2]} {p[3]}")
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        for c in consultation.charger_par_patient(self.patient_id):
            self.tableau.insert("", "end", iid=c[0],
                values=(c[1], c[2], c[3], c[4] or "", c[5] or "", c[6] or ""))