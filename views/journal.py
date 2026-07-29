import tkinter as tk
from tkinter import ttk
from config import C_FOND, C_PRIMAIRE
from models import audit


class VueJournal:
    def afficher(self, parent):
        self.frame = tk.Frame(parent, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Journal des actions", font=("Arial", 16, "bold"),
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 8))
        tk.Label(self.frame, text="Historique des créations, modifications et suppressions.",
                 font=("Arial", 9, "italic"), bg=C_FOND, fg="#888").pack(pady=(0, 8))

        zone_filtre = tk.Frame(self.frame, bg=C_FOND)
        zone_filtre.pack(pady=5)
        tk.Label(zone_filtre, text="Module :", bg=C_FOND).pack(side="left", padx=5)
        self.filtre_module = ttk.Combobox(zone_filtre,
            values=["Tous", "patients", "medecins", "file_attente", "rendez_vous", "consultations", "utilisateurs"],
            state="readonly", width=16)
        self.filtre_module.set("Tous")
        self.filtre_module.pack(side="left", padx=5)
        tk.Button(zone_filtre, text="Actualiser", command=self.charger,
                  bg=C_PRIMAIRE, fg="white", padx=8).pack(side="left", padx=10)

        zone_tab = tk.Frame(self.frame)
        zone_tab.pack(pady=5, fill="both", expand=True, padx=15)

        cols = ("date_heure", "utilisateur", "action", "module", "cible", "details", "ancien", "nouveau")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=18)
        for c, t, w in [("date_heure","Date/Heure",140),("utilisateur","Utilisateur",115),
                         ("action","Action",95),("module","Module",100),
                         ("cible","Cible",50),("details","Détails",200),
                         ("ancien","Ancienne valeur",140),("nouveau","Nouvelle valeur",140)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        sb = ttk.Scrollbar(zone_tab, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=sb.set)
        self.tableau.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.charger()

    def charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        module = self.filtre_module.get()
        if module == "Tous" or module == "":
            data = audit.charger_tout()
        else:
            data = audit.charger_par_module(module)
        for a in data:
            self.tableau.insert("", "end", values=(a[0], a[1] or "—", a[2], a[3], a[4] or "",
                                                     a[5] or "", a[6] or "", a[7] or ""))
