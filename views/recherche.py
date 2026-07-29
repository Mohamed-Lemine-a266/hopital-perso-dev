import tkinter as tk
from tkinter import ttk, messagebox
from config import C_FOND, C_PRIMAIRE, DELAI_RECHERCHE, FONT_H1, FONT_H2, FONT_H3, FONT_TEXTE, FONT_PETIT
from models import patient, consultation, rendez_vous, constantes_vitales, document
from utils.impression import imprimer_fiche_patient
from views.dossier_patient import VueDossierPatient


class VueRecherche:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Recherche de patients", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 6))

        zone_rech = tk.Frame(self.frame, bg=C_FOND)
        zone_rech.pack(pady=5)

        tk.Label(zone_rech, text="Rechercher (CNI, nom, prénom, tél) :", bg=C_FOND,
                 font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.rech_entry = tk.Entry(zone_rech, width=28, font=("Arial", 11))
        self.rech_entry.grid(row=0, column=1, padx=5)
        self._timer_id = None
        self.rech_entry.bind("<KeyRelease>", self._on_keyrelease)
        self.rech_entry.bind("<Return>", lambda e: self.rechercher())

        zone_res = tk.Frame(self.frame)
        zone_res.pack(pady=5, fill="x", padx=15)

        cols = ("cni", "nom", "prenom", "sexe", "telephone", "adresse", "inscription")
        self.tableau = ttk.Treeview(zone_res, columns=cols, show="headings", height=5)
        for c, t, w in [("cni","CNI",95),("nom","Nom",105),("prenom","Prénom",105),("sexe","Sexe",60),
                         ("telephone","Tél",95),("adresse","Adresse",125),("inscription","Inscrit",80)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        self.tableau.pack(fill="x")
        self.tableau.bind("<<TreeviewSelect>>", self.afficher_details)

        self.zone_details = tk.Frame(self.frame, bg=C_FOND)
        self.zone_details.pack(pady=8, fill="both", expand=True, padx=15)
        tk.Label(self.zone_details, text="Sélectionnez un patient pour voir son dossier complet.",
                 font=("Arial", 10, "italic"), bg=C_FOND, fg="#888").pack(pady=10)

    def _on_keyrelease(self, event):
        if self._timer_id:
            self.frame.after_cancel(self._timer_id)
        self._timer_id = self.frame.after(DELAI_RECHERCHE, self.rechercher)

    def rechercher(self):
        terme = self.rech_entry.get().strip()
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        if not terme:
            return
        resultats = patient.rechercher(terme)
        for p in resultats:
            self.tableau.insert("", "end", iid=p[0],
                values=(p[1], p[2], p[3], p[4] or "", p[6] or "", p[7] or "", p[8]))
        if not resultats:
            for w in self.zone_details.winfo_children():
                w.destroy()
            tk.Label(self.zone_details, text="Aucun patient trouvé.",
                     font=("Arial", 10), bg=C_FOND, fg="#888").pack(pady=10)

    def afficher_details(self, event):
        sel = self.tableau.selection()
        if not sel:
            return
        pid = int(sel[0])
        p = patient.obtenir_par_id(pid)
        if not p:
            return
        self._patient_courant = p

        for w in self.zone_details.winfo_children():
            w.destroy()

        zone_boutons_top = tk.Frame(self.zone_details, bg=C_FOND)
        zone_boutons_top.pack(anchor="e", pady=(0, 6))
        tk.Button(zone_boutons_top, text="📁 Dossier complet (onglets)", command=self.ouvrir_dossier_complet,
                  bg=C_PRIMAIRE, fg="white", font=FONT_PETIT, padx=8, pady=3).pack(side="left", padx=4)
        tk.Button(zone_boutons_top, text="🖶 Imprimer la fiche patient", command=self.imprimer_fiche,
                  bg="#555", fg="white", font=FONT_PETIT, padx=8, pady=3).pack(side="left", padx=4)

        tk.Label(self.zone_details, text=f"Dossier de {p[2]} {p[3]}",
                 font=FONT_H2, bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(5, 5))

        info = f"CNI: {p[1]}  |  Sexe: {p[4] or '—'}  |  Né(e): {p[5] or '—'}  |  Tél: {p[6] or '—'}  |  Adresse: {p[7] or '—'}"
        tk.Label(self.zone_details, text=info, bg=C_FOND, font=FONT_PETIT).pack(anchor="w")

        # Informations médicales (allergies, antécédents, groupe sanguin)
        infos_med = patient.obtenir_infos_medicales(pid)
        if infos_med and any(infos_med):
            tk.Label(self.zone_details, text="Informations médicales", font=FONT_H3,
                     bg=C_FOND, fg="#6C5CE7").pack(pady=(10, 3), anchor="w")
            allergies, atcd_med, atcd_chir, groupe = infos_med
            if groupe:
                tk.Label(self.zone_details, text=f"  Groupe sanguin : {groupe}",
                         bg=C_FOND, font=FONT_TEXTE, anchor="w").pack(fill="x")
            if allergies:
                tk.Label(self.zone_details, text=f"  Allergies : {allergies}",
                         bg=C_FOND, font=FONT_PETIT, anchor="w", fg="#C0392B").pack(fill="x")
            if atcd_med:
                tk.Label(self.zone_details, text=f"  Antécédents médicaux : {atcd_med}",
                         bg=C_FOND, font=FONT_PETIT, anchor="w").pack(fill="x")
            if atcd_chir:
                tk.Label(self.zone_details, text=f"  Antécédents chirurgicaux : {atcd_chir}",
                         bg=C_FOND, font=FONT_PETIT, anchor="w").pack(fill="x")

        # Dernières constantes vitales
        derniere_vitale = constantes_vitales.derniere_par_patient(pid)
        if derniere_vitale:
            tk.Label(self.zone_details, text="Dernières constantes vitales", font=FONT_H3,
                     bg=C_FOND, fg="#333").pack(pady=(10, 3), anchor="w")
            _, dv_date, taille, poids, temp, tension, freq, sat = derniere_vitale
            parts = [f"le {dv_date}"]
            if taille: parts.append(f"Taille: {taille} cm")
            if poids: parts.append(f"Poids: {poids} kg")
            if temp: parts.append(f"Temp: {temp}°C")
            if tension: parts.append(f"Tension: {tension}")
            if freq: parts.append(f"Fréq. card: {freq} bpm")
            if sat: parts.append(f"SpO2: {sat}%")
            tk.Label(self.zone_details, text="  " + "  |  ".join(parts),
                     bg=C_FOND, font=FONT_PETIT, anchor="w").pack(fill="x")

        # Rendez-vous
        tk.Label(self.zone_details, text="Rendez-vous", font=("Arial", 11, "bold"), bg=C_FOND).pack(pady=(10, 3), anchor="w")
        rdvs = rendez_vous.charger_par_patient(pid)
        if rdvs:
            for r in rdvs[:5]:
                tk.Label(self.zone_details, text=f"  {r[5]}  —  {r[3]} ({r[4]})  —  {r[7] or ''}  [{r[8]}]",
                         bg=C_FOND, font=("Arial", 9), anchor="w").pack(fill="x")
        else:
            tk.Label(self.zone_details, text="  Aucun.", bg=C_FOND, fg="#888", font=("Arial", 9)).pack(anchor="w")

        # Consultations
        tk.Label(self.zone_details, text="Historique médical", font=("Arial", 11, "bold"), bg=C_FOND).pack(pady=(10, 3), anchor="w")
        cons = consultation.charger_par_patient(pid)
        if cons:
            for c in cons[:5]:
                tk.Label(self.zone_details, text=f"  {c[1]}  —  {c[2]} ({c[3]})",
                         bg=C_FOND, font=("Arial", 9, "bold"), anchor="w").pack(fill="x")
                for lbl, val in [("Diagnostic", c[4]), ("Traitement", c[5]), ("Observations", c[6])]:
                    if val:
                        tk.Label(self.zone_details, text=f"    {lbl} : {val}",
                                 bg=C_FOND, font=("Arial", 9), anchor="w").pack(fill="x")
        else:
            tk.Label(self.zone_details, text="  Aucune.", bg=C_FOND, fg="#888", font=("Arial", 9)).pack(anchor="w")

        # Documents associés
        tk.Label(self.zone_details, text="Documents", font=FONT_H3, bg=C_FOND, fg="#333").pack(
            pady=(10, 3), anchor="w")
        docs = document.charger_par_patient(pid)
        if docs:
            for d in docs[:5]:
                tk.Label(self.zone_details, text=f"  {d[1]} — {d[2]} ({d[4]})",
                         bg=C_FOND, font=FONT_PETIT, anchor="w").pack(fill="x")
        else:
            tk.Label(self.zone_details, text="  Aucun document.", bg=C_FOND, fg="#888",
                     font=FONT_PETIT).pack(anchor="w")

    def imprimer_fiche(self):
        if not hasattr(self, "_patient_courant") or self._patient_courant is None:
            return
        p = self._patient_courant
        pid = p[0]
        infos_med = patient.obtenir_infos_medicales(pid)
        derniere_vitale = constantes_vitales.derniere_par_patient(pid)
        docs = document.charger_par_patient(pid)
        consultations_list = consultation.charger_par_patient(pid)
        rdv_list = rendez_vous.charger_par_patient(pid)
        imprimer_fiche_patient(p, consultations_list, rdv_list, infos_med, derniere_vitale, docs)

    def ouvrir_dossier_complet(self):
        if not hasattr(self, "_patient_courant") or self._patient_courant is None:
            return
        popup = tk.Toplevel(self.frame.winfo_toplevel())
        popup.title("Dossier patient")
        popup.geometry("900x600")
        vue = VueDossierPatient()
        vue.afficher(popup, patient_id=self._patient_courant[0])
