import tkinter as tk
import os
import shutil
from tkinter import ttk, messagebox, filedialog
from config import C_FOND, C_PRIMAIRE, C_DANGER, FONT_H1, FONT_TEXTE, FONT_PETIT
from models import patient, document
import session

DOSSIER_DOCUMENTS = "documents_patients"


class VueDocuments:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Documents des patients", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 4))
        tk.Label(self.frame, text="Ordonnances, analyses, radios, scanners, IRM et autres documents.",
                 font=FONT_PETIT, bg=C_FOND, fg="#888").pack(pady=(0, 8))

        zone_rech = tk.Frame(self.frame, bg=C_FOND)
        zone_rech.pack(pady=5)
        tk.Label(zone_rech, text="CNI patient :", bg=C_FOND, font=FONT_TEXTE).grid(row=0, column=0, padx=5)
        self.cni_entry = tk.Entry(zone_rech, width=18, font=FONT_TEXTE)
        self.cni_entry.grid(row=0, column=1, padx=5)
        self.cni_entry.bind("<Return>", lambda e: self.chercher())
        tk.Button(zone_rech, text="Chercher", command=self.chercher,
                  bg="#468FAF", fg="white").grid(row=0, column=2, padx=5)
        self.pat_label = tk.Label(zone_rech, text="", bg=C_FOND, fg=C_PRIMAIRE, font=FONT_PETIT)
        self.pat_label.grid(row=0, column=3, padx=8)

        zone_ajout = tk.Frame(self.frame, bg=C_FOND)
        zone_ajout.pack(pady=6)
        tk.Label(zone_ajout, text="Type :", bg=C_FOND, font=FONT_TEXTE).grid(row=0, column=0, padx=5)
        self.type_combo = ttk.Combobox(zone_ajout, values=document.TYPES_DOCUMENT, state="readonly", width=15)
        self.type_combo.grid(row=0, column=1, padx=5)
        self.type_combo.set(document.TYPES_DOCUMENT[0])
        tk.Button(zone_ajout, text="Ajouter un fichier...", command=self.ajouter_fichier,
                  bg=C_PRIMAIRE, fg="white", padx=10).grid(row=0, column=2, padx=10)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=8, fill="both", expand=True, padx=20)
        cols = ("type", "nom_fichier", "date_ajout", "ajoute_par")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=12)
        for c, t, w in [("type", "Type", 110), ("nom_fichier", "Fichier", 260),
                        ("date_ajout", "Ajouté le", 130), ("ajoute_par", "Ajouté par", 140)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        zone_btn = tk.Frame(self.frame, bg=C_FOND)
        zone_btn.pack(pady=8)
        tk.Button(zone_btn, text="Ouvrir", command=self.ouvrir_document,
                  bg="#468FAF", fg="white", padx=10).pack(side="left", padx=5)
        tk.Button(zone_btn, text="Supprimer", command=self.supprimer_document,
                  bg=C_DANGER, fg="white", padx=10).pack(side="left", padx=5)

        self.patient_id = None

    def chercher(self):
        cni = self.cni_entry.get().strip()
        if not cni:
            return
        p = patient.rechercher_par_cni(cni)
        if p:
            self.patient_id = p[0]
            self.pat_label.config(text=f"{p[2]} {p[3]} (CNI: {p[1]})")
            self.charger()
        else:
            self.patient_id = None
            self.pat_label.config(text="Patient introuvable.")
            for r in self.tableau.get_children():
                self.tableau.delete(r)

    def charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        if self.patient_id is None:
            return
        for d in document.charger_par_patient(self.patient_id):
            self.tableau.insert("", "end", iid=d[0], values=(d[1], d[2], d[4], d[5] or ""))

    def ajouter_fichier(self):
        if self.patient_id is None:
            messagebox.showwarning("Patient requis", "Cherchez un patient par CNI d'abord.")
            return
        chemin_source = filedialog.askopenfilename(title="Sélectionner un document")
        if not chemin_source:
            return
        try:
            os.makedirs(DOSSIER_DOCUMENTS, exist_ok=True)
            nom_fichier = os.path.basename(chemin_source)
            destination = os.path.join(DOSSIER_DOCUMENTS, f"p{self.patient_id}_{nom_fichier}")
            shutil.copy2(chemin_source, destination)
            type_doc = self.type_combo.get()
            document.ajouter(self.patient_id, type_doc, nom_fichier, destination,
                              session.utilisateur_nom_complet())
            self.charger()
            messagebox.showinfo("Succès", f"Document '{nom_fichier}' ajouté.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def ouvrir_document(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un document.")
            return
        doc = document.obtenir_par_id(sel[0])
        if not doc:
            return
        chemin = doc[4]
        try:
            import webbrowser
            webbrowser.open('file://' + os.path.abspath(chemin))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

    def supprimer_document(self):
        sel = self.tableau.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Sélectionnez un document.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce document ?"):
            return
        doc = document.obtenir_par_id(sel[0])
        document.supprimer(sel[0])
        if doc:
            try:
                os.remove(doc[4])
            except OSError:
                pass
        self.charger()
