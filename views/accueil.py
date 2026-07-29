import tkinter as tk
import os
from config import (C_FOND, C_PRIMAIRE, C_SURFACE, C_BORDURE, C_TEXTE_SECONDAIRE,
                     FONT_H1, FONT_H2, FONT_H3, FONT_TEXTE, FONT_PETIT, FONT_CHIFFRE)
from models import patient, medecin, file_attente, rendez_vous, consultation, parametres, statistiques


class VueAccueil:
    def afficher(self, parent):
        # Canvas + scrollbar pour un tableau de bord qui peut s'étendre sans contrainte
        canvas = tk.Canvas(parent, bg=C_FOND, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.frame = tk.Frame(canvas, bg=C_FOND)

        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _molette(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _molette)

        # ── En-tête : logo + nom hôpital ──
        entete = tk.Frame(self.frame, bg=C_FOND)
        entete.pack(fill="x", pady=(20, 10), padx=30)

        logo_path = parametres.logo()
        logo_affiche = False
        if logo_path and os.path.exists(logo_path):
            try:
                self.logo_img = tk.PhotoImage(file=logo_path)
                w, h = self.logo_img.width(), self.logo_img.height()
                if w > 70 or h > 70:
                    self.logo_img = self.logo_img.subsample(max(w // 70, h // 70, 1))
                tk.Label(entete, image=self.logo_img, bg=C_FOND).pack(side="left", padx=(0, 15))
                logo_affiche = True
            except Exception:
                pass
        if not logo_affiche:
            tk.Label(entete, text="🏥", font=("Arial", 36), bg=C_FOND).pack(side="left", padx=(0, 15))

        bloc_titre = tk.Frame(entete, bg=C_FOND)
        bloc_titre.pack(side="left")
        tk.Label(bloc_titre, text=parametres.nom_hopital(), font=FONT_H1,
                 bg=C_FOND, fg=C_PRIMAIRE, anchor="w").pack(fill="x")
        em = parametres.email()
        sous_texte = "Tableau de bord — Vue d'ensemble en temps réel"
        tk.Label(bloc_titre, text=sous_texte, font=FONT_PETIT,
                 bg=C_FOND, fg=C_TEXTE_SECONDAIRE, anchor="w").pack(fill="x")

        # ── Récupération des données (défensif : ne bloque jamais l'affichage) ──
        try:
            nb_patients_total = len(patient.charger_tous())
            nb_medecins_total = len(medecin.charger_tous())
            statuts_medecins = medecin.compter_par_statut()
            nb_medecins_presents = statuts_medecins.get("présent", 0)
            statuts_file = file_attente.compter_par_statut_jour()
            nb_en_attente = statuts_file.get("en attente", 0)
            nb_en_consultation = statuts_file.get("en consultation", 0)
            nb_appeles = statuts_file.get("appelé", 0)
            nb_rdv_jour = len(rendez_vous.charger_aujourd_hui())
            nb_patients_aujourdhui = statistiques.patients_par_periode(0)
            temps_attente_data = statistiques.temps_moyen_attente(0)
            temps_moyen_global = (
                round(sum(t for _, t in temps_attente_data) / len(temps_attente_data), 1)
                if temps_attente_data else 0
            )
            par_specialite = file_attente.compter_en_attente_par_specialite()
        except Exception:
            nb_patients_total = nb_medecins_total = nb_medecins_presents = 0
            nb_en_attente = nb_en_consultation = nb_appeles = nb_rdv_jour = 0
            nb_patients_aujourdhui = temps_moyen_global = 0
            par_specialite = []

        # ── Cartes indicateurs (ligne 1 : activité du jour) ──
        tk.Label(self.frame, text="Activité du jour", font=FONT_H2, bg=C_FOND, fg="#333",
                 anchor="w").pack(fill="x", padx=30, pady=(15, 8))

        ligne1 = tk.Frame(self.frame, bg=C_FOND)
        ligne1.pack(padx=25, pady=2)
        cartes_jour = [
            ("Patients reçus", nb_patients_aujourdhui, "#1B4965", "🧍"),
            ("En attente", nb_en_attente, "#E67E22", "⏳"),
            ("Appelés", nb_appeles, "#2980B9", "📢"),
            ("En consultation", nb_en_consultation, "#8E44AD", "🩺"),
            ("RDV aujourd'hui", nb_rdv_jour, "#27AE60", "📅"),
        ]
        for i, (label, val, col, icone) in enumerate(cartes_jour):
            self._carte(ligne1, label, val, col, icone).grid(row=0, column=i, padx=6, pady=6)

        # ── Cartes indicateurs (ligne 2 : ressources & qualité de service) ──
        tk.Label(self.frame, text="Ressources & qualité de service", font=FONT_H2,
                 bg=C_FOND, fg="#333", anchor="w").pack(fill="x", padx=30, pady=(18, 8))

        ligne2 = tk.Frame(self.frame, bg=C_FOND)
        ligne2.pack(padx=25, pady=2)
        cartes_ressources = [
            ("Patients (total)", nb_patients_total, "#34495E", "📁"),
            ("Médecins (total)", nb_medecins_total, "#34495E", "👥"),
            ("Médecins présents", nb_medecins_presents, "#27AE60", "✔"),
            ("Temps attente moy.", f"{temps_moyen_global} min", "#C0392B", "⏱"),
        ]
        for i, (label, val, col, icone) in enumerate(cartes_ressources):
            self._carte(ligne2, label, val, col, icone).grid(row=0, column=i, padx=6, pady=6)

        # ── File d'attente en temps réel par spécialité (barres proportionnelles) ──
        tk.Label(self.frame, text="File d'attente par spécialité", font=FONT_H2,
                 bg=C_FOND, fg="#333", anchor="w").pack(fill="x", padx=30, pady=(20, 8))

        carte_file = tk.Frame(self.frame, bg=C_SURFACE, highlightbackground=C_BORDURE,
                               highlightthickness=1)
        carte_file.pack(fill="x", padx=30, pady=(0, 10))

        if par_specialite:
            nb_max = max(nb for _, nb in par_specialite) or 1
            for spec, nb in par_specialite:
                ligne = tk.Frame(carte_file, bg=C_SURFACE)
                ligne.pack(fill="x", padx=18, pady=6)
                tk.Label(ligne, text=spec, font=FONT_TEXTE, bg=C_SURFACE, width=20,
                         anchor="w").pack(side="left")

                barre_fond = tk.Frame(ligne, bg="#EDEFF2", height=14, width=260)
                barre_fond.pack(side="left", padx=10)
                barre_fond.pack_propagate(False)
                couleur = "#C0392B" if nb >= 5 else "#E67E22" if nb >= 3 else "#27AE60"
                largeur_relative = max(int(260 * nb / nb_max), 6)
                barre_remplie = tk.Frame(barre_fond, bg=couleur, width=largeur_relative)
                barre_remplie.pack(side="left", fill="y")

                tk.Label(ligne, text=f"{nb} en attente", font=FONT_TEXTE,
                         bg=C_SURFACE, fg=couleur).pack(side="left", padx=8)
        else:
            tk.Label(carte_file, text="Aucun patient en attente actuellement.", font=FONT_PETIT,
                     bg=C_SURFACE, fg=C_TEXTE_SECONDAIRE).pack(pady=18)

        tk.Frame(self.frame, bg=C_FOND, height=20).pack()

    def _carte(self, parent, label, valeur, couleur, icone):
        carte = tk.Frame(parent, bg=couleur, padx=18, pady=12)
        tk.Label(carte, text=icone, font=("Arial", 16), bg=couleur, fg="white").pack()
        tk.Label(carte, text=str(valeur), font=FONT_CHIFFRE, bg=couleur, fg="white").pack()
        tk.Label(carte, text=label, font=FONT_PETIT, bg=couleur, fg="white",
                 wraplength=110, justify="center").pack()
        return carte
