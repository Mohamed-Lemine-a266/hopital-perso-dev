import tkinter as tk
import csv
from tkinter import ttk, filedialog, messagebox
from config import C_FOND, C_PRIMAIRE, C_SURFACE, C_BORDURE, FONT_H1, FONT_H3, FONT_PETIT
from models import statistiques


class VueStatistiques:
    def afficher(self, parent):
        canvas = tk.Canvas(parent, bg=C_FOND, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.frame = tk.Frame(canvas, bg=C_FOND)
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        tk.Label(self.frame, text="Statistiques", font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(10, 8))

        zone_per = tk.Frame(self.frame, bg=C_FOND)
        zone_per.pack(pady=5)
        tk.Label(zone_per, text="Période :", bg=C_FOND).pack(side="left", padx=5)
        self.periode = ttk.Combobox(zone_per, values=["Aujourd'hui", "7 derniers jours", "30 derniers jours", "Tout"],
                                     state="readonly", width=18)
        self.periode.pack(side="left", padx=5)
        self.periode.set("30 derniers jours")
        tk.Button(zone_per, text="Actualiser", command=self.charger, bg=C_PRIMAIRE, fg="white",
                  padx=8).pack(side="left", padx=10)
        tk.Button(zone_per, text="Exporter en CSV", command=self.exporter_csv, bg="#27AE60", fg="white",
                  padx=8).pack(side="left", padx=6)

        self.zone_stats = tk.Frame(self.frame, bg=C_FOND)
        self.zone_stats.pack(pady=5, fill="both", expand=True, padx=20)

        self._dernieres_donnees = {}
        self.charger()

    def _jours(self):
        p = self.periode.get()
        if p == "Aujourd'hui":
            return 0
        elif p == "7 derniers jours":
            return 7
        elif p == "30 derniers jours":
            return 30
        return None

    def charger(self):
        for w in self.zone_stats.winfo_children():
            w.destroy()
        jours = self._jours()

        nb = statistiques.patients_par_periode(jours)
        self._carte(f"Patients reçus ({self.periode.get()})", str(nb)).pack(anchor="w", pady=(0, 15))

        repartition = statistiques.repartition_par_specialite(jours)
        self._section_graphique("Répartition par spécialité", repartition, "#2A6F97")

        charge = statistiques.charge_par_medecin(jours)
        self._section_graphique("Charge par médecin (consultations)", charge, "#8E44AD")

        temps = statistiques.temps_moyen_attente(jours)
        self._section_tableau("Temps moyen d'attente (minutes)", ["Spécialité", "Minutes"], temps)

        taux = statistiques.taux_rdv(jours)
        self._section_tableau("Rendez-vous par statut", ["Statut", "Nombre"], taux)

        jour = statistiques.jour_plus_charge(jours)
        self._section_tableau("Jour le plus chargé", ["Jour", "Patients"], jour)

        self._dernieres_donnees = {
            "repartition_specialite": repartition, "charge_medecin": charge,
            "temps_attente": temps, "taux_rdv": taux, "jour_charge": jour,
        }

    def _carte(self, titre, valeur):
        f = tk.Frame(self.zone_stats, bg=C_PRIMAIRE, padx=20, pady=10)
        tk.Label(f, text=valeur, font=("Arial", 24, "bold"), bg=C_PRIMAIRE, fg="white").pack()
        tk.Label(f, text=titre, font=FONT_PETIT, bg=C_PRIMAIRE, fg="white").pack()
        return f

    def _section_graphique(self, titre, data, couleur):
        tk.Label(self.zone_stats, text=titre, font=FONT_H3, bg=C_FOND, fg="#333").pack(
            anchor="w", pady=(10, 4))
        carte = tk.Frame(self.zone_stats, bg=C_SURFACE, highlightbackground=C_BORDURE, highlightthickness=1)
        carte.pack(fill="x", pady=(0, 6))

        if not data:
            tk.Label(carte, text="Aucune donnée pour cette période.", bg=C_SURFACE,
                     fg="#888", font=FONT_PETIT).pack(pady=15)
            return

        largeur_canvas = 640
        hauteur_barre = 26
        marge_gauche = 180
        hauteur_totale = len(data) * (hauteur_barre + 8) + 20
        cv = tk.Canvas(carte, width=largeur_canvas, height=hauteur_totale, bg=C_SURFACE, highlightthickness=0)
        cv.pack(padx=15, pady=10)

        val_max = max(v for _, v in data) or 1
        y = 12
        for label, valeur in data:
            cv.create_text(marge_gauche - 10, y + hauteur_barre / 2, text=str(label),
                            anchor="e", font=("Segoe UI", 9))
            largeur_barre = int((largeur_canvas - marge_gauche - 60) * valeur / val_max)
            largeur_barre = max(largeur_barre, 3)
            cv.create_rectangle(marge_gauche, y, marge_gauche + largeur_barre, y + hauteur_barre,
                                 fill=couleur, outline="")
            cv.create_text(marge_gauche + largeur_barre + 8, y + hauteur_barre / 2,
                            text=str(valeur), anchor="w", font=("Segoe UI", 9, "bold"))
            y += hauteur_barre + 8

    def _section_tableau(self, titre, colonnes, data):
        tk.Label(self.zone_stats, text=titre, font=FONT_H3, bg=C_FOND, fg="#333").pack(
            anchor="w", pady=(10, 4))
        if not data:
            tk.Label(self.zone_stats, text="  Aucune donnée.", bg=C_FOND, fg="#888",
                     font=FONT_PETIT).pack(anchor="w", pady=(0, 6))
            return
        tv = ttk.Treeview(self.zone_stats, columns=colonnes, show="headings", height=min(len(data), 6))
        for c in colonnes:
            tv.heading(c, text=c)
            tv.column(c, width=200)
        for d in data:
            tv.insert("", "end", values=d)
        tv.pack(fill="x", pady=(0, 6))

    def exporter_csv(self):
        dest = filedialog.asksaveasfilename(title="Exporter les statistiques", defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv"), ("Tous", "*.*")])
        if not dest:
            return
        try:
            with open(dest, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                for titre, cle, colonnes in [
                    ("Répartition par spécialité", "repartition_specialite", ["Spécialité", "Nombre"]),
                    ("Charge par médecin", "charge_medecin", ["Médecin", "Consultations"]),
                    ("Temps moyen d'attente", "temps_attente", ["Spécialité", "Minutes"]),
                    ("Rendez-vous par statut", "taux_rdv", ["Statut", "Nombre"]),
                    ("Jour le plus chargé", "jour_charge", ["Jour", "Patients"]),
                ]:
                    writer.writerow([titre])
                    writer.writerow(colonnes)
                    for ligne in self._dernieres_donnees.get(cle, []):
                        writer.writerow(ligne)
                    writer.writerow([])
            messagebox.showinfo("Succès", f"Statistiques exportées vers :\n{dest}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
