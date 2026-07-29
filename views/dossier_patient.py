import tkinter as tk
from tkinter import ttk, messagebox
from config import C_FOND, C_PRIMAIRE, C_SURFACE, FONT_H1, FONT_H2, FONT_H3, FONT_TEXTE, FONT_PETIT, GROUPES_SANGUINS
from models import patient, consultation, rendez_vous, constantes_vitales, document
from utils.impression import imprimer_fiche_patient


class VueDossierPatient:
    """Dossier patient unifié : une seule fenêtre avec des onglets internes
    (Infos / Constantes / Consultations / RDV / Documents). Consulté en
    lecture seule — les modifications se font toujours dans les modules
    métier dédiés (Patients, Consultations, Rendez-vous, Documents)."""

    def afficher(self, parent, patient_id=None):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)
        self.patient_id = patient_id

        tk.Label(self.frame, text="Dossier patient", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 4))

        zone_rech = tk.Frame(self.frame, bg=C_FOND)
        zone_rech.pack(pady=4)
        tk.Label(zone_rech, text="CNI :", bg=C_FOND, font=FONT_TEXTE).pack(side="left", padx=5)
        self.cni_entry = tk.Entry(zone_rech, width=20, font=FONT_TEXTE)
        self.cni_entry.pack(side="left", padx=5)
        self.cni_entry.bind("<Return>", lambda e: self._chercher())
        tk.Button(zone_rech, text="Ouvrir le dossier", command=self._chercher,
                  bg=C_PRIMAIRE, fg="white", padx=10).pack(side="left", padx=5)

        self.zone_contenu = tk.Frame(self.frame, bg=C_FOND)
        self.zone_contenu.pack(fill="both", expand=True, padx=15, pady=8)

        if self.patient_id:
            self._charger_patient(self.patient_id)
        else:
            tk.Label(self.zone_contenu, text="Saisissez un CNI pour ouvrir un dossier.",
                     font=FONT_PETIT, bg=C_FOND, fg="#888").pack(pady=30)

    def _chercher(self):
        cni = self.cni_entry.get().strip()
        if not cni:
            return
        p = patient.rechercher_par_cni(cni)
        if not p:
            messagebox.showinfo("Introuvable", "Aucun patient avec ce CNI.")
            return
        self._charger_patient(p[0])

    def _charger_patient(self, pid):
        self.patient_id = pid
        for w in self.zone_contenu.winfo_children():
            w.destroy()

        p = patient.obtenir_par_id(pid)
        if not p:
            return

        tk.Label(self.zone_contenu, text=f"{p[2]} {p[3]}  —  CNI: {p[1]}", font=FONT_H2,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(self.zone_contenu)
        notebook.pack(fill="both", expand=True)

        onglet_infos = tk.Frame(notebook, bg=C_SURFACE)
        onglet_vitales = tk.Frame(notebook, bg=C_SURFACE)
        onglet_consultations = tk.Frame(notebook, bg=C_SURFACE)
        onglet_rdv = tk.Frame(notebook, bg=C_SURFACE)
        onglet_documents = tk.Frame(notebook, bg=C_SURFACE)

        notebook.add(onglet_infos, text="  Informations  ")
        notebook.add(onglet_vitales, text="  Constantes vitales  ")
        notebook.add(onglet_consultations, text="  Consultations  ")
        notebook.add(onglet_rdv, text="  Rendez-vous  ")
        notebook.add(onglet_documents, text="  Documents  ")

        self._remplir_infos(onglet_infos, p)
        self._remplir_vitales(onglet_vitales, pid)
        self._remplir_consultations(onglet_consultations, pid)
        self._remplir_rdv(onglet_rdv, pid)
        self._remplir_documents(onglet_documents, pid)

        tk.Button(self.zone_contenu, text="🖶 Imprimer la fiche complète",
                  command=lambda: self._imprimer(p), bg="#555", fg="white",
                  font=FONT_PETIT, padx=10, pady=4).pack(anchor="e", pady=(8, 0))

    def _remplir_infos(self, parent, p):
        zone = tk.Frame(parent, bg=C_SURFACE)
        zone.pack(fill="both", expand=True, padx=20, pady=15)

        champs = [("CNI", p[1]), ("Nom", p[2]), ("Prénom", p[3]), ("Sexe", p[4] or "—"),
                  ("Date de naissance", p[5] or "—"), ("Téléphone", p[6] or "—"),
                  ("Adresse", p[7] or "—"), ("Date d'inscription", p[8])]
        for i, (label, val) in enumerate(champs):
            tk.Label(zone, text=f"{label} :", font=FONT_TEXTE, bg=C_SURFACE, fg="#666").grid(
                row=i, column=0, sticky="w", padx=5, pady=4)
            tk.Label(zone, text=val, font=("Arial", 10, "bold"), bg=C_SURFACE).grid(
                row=i, column=1, sticky="w", padx=15, pady=4)

        infos_med = patient.obtenir_infos_medicales(p[0])
        if infos_med and any(infos_med):
            allergies, atcd_med, atcd_chir, groupe = infos_med
            tk.Label(zone, text="Informations médicales", font=FONT_H3, bg=C_SURFACE,
                     fg="#6C5CE7").grid(row=len(champs), column=0, columnspan=2, sticky="w", pady=(15, 5))
            extra = [("Groupe sanguin", groupe or "—"), ("Allergies", allergies or "—"),
                     ("Antécédents médicaux", atcd_med or "—"), ("Antécédents chirurgicaux", atcd_chir or "—")]
            for j, (label, val) in enumerate(extra):
                tk.Label(zone, text=f"{label} :", font=FONT_TEXTE, bg=C_SURFACE, fg="#666").grid(
                    row=len(champs)+1+j, column=0, sticky="w", padx=5, pady=4)
                tk.Label(zone, text=val, font=FONT_TEXTE, bg=C_SURFACE, wraplength=350,
                         justify="left").grid(row=len(champs)+1+j, column=1, sticky="w", padx=15, pady=4)

    def _remplir_vitales(self, parent, pid):
        cols = ("date", "taille", "poids", "temp", "tension", "freq", "sat")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        for c, t, w in [("date","Date",130),("taille","Taille (cm)",90),("poids","Poids (kg)",90),
                        ("temp","Temp (°C)",80),("tension","Tension",80),
                        ("freq","Fréq. card.",90),("sat","SpO2 (%)",70)]:
            tv.heading(c, text=t)
            tv.column(c, width=w)
        tv.pack(fill="both", expand=True, padx=15, pady=15)
        for v in constantes_vitales.charger_par_patient(pid):
            tv.insert("", "end", values=(v[1], v[2] or "", v[3] or "", v[4] or "",
                                          v[5] or "", v[6] or "", v[7] or ""))

    def _remplir_consultations(self, parent, pid):
        cols = ("date", "medecin", "specialite", "diagnostic", "traitement", "observations")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        for c, t, w in [("date","Date",120),("medecin","Médecin",120),("specialite","Spécialité",100),
                        ("diagnostic","Diagnostic",150),("traitement","Traitement",140),("observations","Obs.",120)]:
            tv.heading(c, text=t)
            tv.column(c, width=w)
        tv.pack(fill="both", expand=True, padx=15, pady=15)
        for c in consultation.charger_par_patient(pid):
            tv.insert("", "end", values=(c[1], c[2], c[3], c[4] or "", c[5] or "", c[6] or ""))

    def _remplir_rdv(self, parent, pid):
        cols = ("date_heure", "medecin", "specialite", "motif", "statut")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        for c, t, w in [("date_heure","Date/Heure",130),("medecin","Médecin",130),
                        ("specialite","Spécialité",110),("motif","Motif",180),("statut","Statut",90)]:
            tv.heading(c, text=t)
            tv.column(c, width=w)
        tv.pack(fill="both", expand=True, padx=15, pady=15)
        for r in rendez_vous.charger_par_patient(pid):
            tv.insert("", "end", values=(r[5], r[3], r[4], r[7] or "", r[8]))

    def _remplir_documents(self, parent, pid):
        cols = ("type", "nom_fichier", "date_ajout", "ajoute_par")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=12)
        for c, t, w in [("type","Type",100),("nom_fichier","Fichier",250),
                        ("date_ajout","Ajouté le",130),("ajoute_par","Ajouté par",140)]:
            tv.heading(c, text=t)
            tv.column(c, width=w)
        tv.pack(fill="both", expand=True, padx=15, pady=15)
        for d in document.charger_par_patient(pid):
            tv.insert("", "end", values=(d[1], d[2], d[4], d[5] or ""))
        tk.Label(parent, text="Pour ajouter ou ouvrir un document, utilisez le module Documents.",
                 font=FONT_PETIT, bg=C_SURFACE, fg="#888").pack(pady=(0, 10))

    def _imprimer(self, p):
        pid = p[0]
        infos_med = patient.obtenir_infos_medicales(pid)
        derniere_vitale = constantes_vitales.derniere_par_patient(pid)
        docs = document.charger_par_patient(pid)
        consultations_list = consultation.charger_par_patient(pid)
        rdv_list = rendez_vous.charger_par_patient(pid)
        imprimer_fiche_patient(p, consultations_list, rdv_list, infos_med, derniere_vitale, docs)
