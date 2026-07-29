import tkinter as tk
from config import (C_SIDEBAR, C_SIDEBAR_BTN, C_SIDEBAR_ACTIVE, C_FOND, C_PRIMAIRE,
                     C_SIDEBAR_TEXTE_ATTENUE, FONT_H3, FONT_TEXTE, FONT_PETIT, ICONS)


MENU_PERMISSIONS = {
    "accueil": "accueil",
    "accueil_patient": "accueil_patient",
    "patients": "patients_voir",
    "medecins": "medecins_voir",
    "specialites": "specialites_gerer",
    "file_attente": "file_attente_voir",
    "rendez_vous": "rdv_voir",
    "consultations": "consultations_voir",
    "documents": "documents_voir",
    "recherche": "recherche",
    "statistiques": "statistiques",
    "parametres": "parametres",
    "utilisateurs": "utilisateurs_gerer",
    "journal": "audit_voir",
    "dossier_patient": "recherche",
}

LIBELLES = {
    "accueil": "Accueil", "accueil_patient": "Accueil Patient", "patients": "Patients",
    "medecins": "Médecins", "specialites": "Spécialités",
    "file_attente": "File d'attente", "rendez_vous": "Rendez-vous",
    "consultations": "Consultations", "recherche": "Recherche", "statistiques": "Statistiques",
    "parametres": "Paramètres", "utilisateurs": "Utilisateurs", "journal": "Journal d'audit",
    "documents": "Documents", "mon_profil": "Mon profil",
    "dossier_patient": "Dossier patient",
}

RAFRAICHISSEMENT_BADGES_MS = 8000
LARGEUR_SIDEBAR = 245


class Navigation:
    def __init__(self, parent, vues, permissions, utilisateur_info):
        self.parent = parent
        self.vues = vues
        self.permissions = permissions

        self.sidebar = tk.Frame(parent, bg=C_SIDEBAR, width=LARGEUR_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ── Bloc identité utilisateur (fixe, en haut — cliquable → Mon profil) ──
        bloc_user = tk.Frame(self.sidebar, bg=C_SIDEBAR, cursor="hand2")
        bloc_user.pack(side="top", fill="x", pady=(18, 14), padx=14)
        bloc_user.bind("<Button-1>", lambda e: self.afficher_vue("mon_profil"))

        avatar = tk.Label(bloc_user, text="●", font=("Arial", 22), bg=C_SIDEBAR,
                           fg=C_PRIMAIRE, cursor="hand2")
        avatar.pack(side="left", padx=(0, 8))
        avatar.bind("<Button-1>", lambda e: self.afficher_vue("mon_profil"))

        infos = tk.Frame(bloc_user, bg=C_SIDEBAR, cursor="hand2")
        infos.pack(side="left", fill="x", expand=True)
        lbl_nom = tk.Label(infos, text=f"{utilisateur_info['prenom']} {utilisateur_info['nom']}",
                           font=FONT_H3, bg=C_SIDEBAR, fg="white", anchor="w", cursor="hand2",
                           wraplength=155, justify="left")
        lbl_nom.pack(fill="x")
        lbl_nom.bind("<Button-1>", lambda e: self.afficher_vue("mon_profil"))
        lbl_role = tk.Label(infos, text=utilisateur_info['role_nom'], font=FONT_PETIT,
                            bg=C_SIDEBAR, fg=C_SIDEBAR_TEXTE_ATTENUE, anchor="w", cursor="hand2")
        lbl_role.pack(fill="x")
        lbl_role.bind("<Button-1>", lambda e: self.afficher_vue("mon_profil"))

        sep = tk.Frame(self.sidebar, bg="#3A7CA5", height=1)
        sep.pack(side="top", fill="x", padx=14, pady=(0, 6))

        # ── Déconnexion (fixe, en bas) — empaqueté AVANT le menu pour réserver sa place ──
        sep2 = tk.Frame(self.sidebar, bg="#3A7CA5", height=1)
        sep2.pack(side="bottom", fill="x", padx=14, pady=(6, 8))
        icone_deco = ICONS.get("deconnexion", "⏻")
        btn_deco = tk.Button(self.sidebar, text=f"  {icone_deco}   Déconnexion", font=FONT_TEXTE,
                             bg="#8B2E24", fg="white", relief="flat", cursor="hand2",
                             anchor="w", padx=8, pady=8, bd=0, highlightthickness=0,
                             command=self._deconnexion)
        btn_deco.pack(side="bottom", fill="x", padx=10, pady=(0, 16))

        # ── Menu : véritablement scrollable (Canvas + Scrollbar + molette) ──
        menu_container = tk.Frame(self.sidebar, bg=C_SIDEBAR)
        menu_container.pack(side="top", fill="both", expand=True)

        menu_canvas = tk.Canvas(menu_container, bg=C_SIDEBAR, highlightthickness=0,
                                 width=LARGEUR_SIDEBAR - 16)
        menu_scrollbar = tk.Scrollbar(menu_container, orient="vertical", command=menu_canvas.yview,
                                      width=10)
        menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        menu_canvas.pack(side="left", fill="both", expand=True)
        menu_scrollbar.pack(side="right", fill="y")

        menu_scroll = tk.Frame(menu_canvas, bg=C_SIDEBAR)
        fenetre_id = menu_canvas.create_window((0, 0), window=menu_scroll, anchor="nw")

        def _maj_scrollregion(event=None):
            menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))

        def _maj_largeur_contenu(event):
            menu_canvas.itemconfig(fenetre_id, width=event.width)

        menu_scroll.bind("<Configure>", _maj_scrollregion)
        menu_canvas.bind("<Configure>", _maj_largeur_contenu)

        def _molette(event):
            menu_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        menu_canvas.bind("<Enter>", lambda e: menu_canvas.bind_all("<MouseWheel>", _molette))
        menu_canvas.bind("<Leave>", lambda e: menu_canvas.unbind_all("<MouseWheel>"))

        boutons_ordre = ["accueil", "accueil_patient", "patients", "medecins", "specialites",
                          "file_attente", "rendez_vous", "consultations", "documents",
                          "recherche", "dossier_patient", "statistiques", "parametres",
                          "utilisateurs", "journal"]

        self.boutons = {}
        self.badges = {}
        for cle in boutons_ordre:
            perm_requise = MENU_PERMISSIONS.get(cle, cle)
            if perm_requise not in self.permissions:
                continue
            icone = ICONS.get(cle, "•")
            ligne_btn = tk.Frame(menu_scroll, bg=C_SIDEBAR_BTN)
            ligne_btn.pack(fill="x", padx=10, pady=2)

            btn = tk.Button(ligne_btn, text=f"  {icone}   {LIBELLES.get(cle, cle)}", font=FONT_TEXTE,
                            bg=C_SIDEBAR_BTN, fg="white", relief="flat",
                            activebackground=C_SIDEBAR_ACTIVE, activeforeground="white",
                            cursor="hand2", anchor="w", padx=8, pady=8, bd=0,
                            highlightthickness=0,
                            command=lambda c=cle: self.afficher_vue(c))
            btn.pack(side="left", fill="x", expand=True)

            badge = tk.Label(ligne_btn, text="", font=("Arial", 8, "bold"), bg=C_SIDEBAR_BTN,
                             fg="white")
            if cle in ("file_attente", "rendez_vous"):
                badge.pack(side="right", padx=(0, 8))
            self.badges[cle] = badge
            self.boutons[cle] = (ligne_btn, btn)

        self.contenu = tk.Frame(parent, bg=C_FOND)
        self.contenu.pack(side="right", fill="both", expand=True)

        self._actualiser_badges()

    def afficher_vue(self, nom_vue):
        for widget in self.contenu.winfo_children():
            widget.destroy()
        if nom_vue in self.vues and self.vues[nom_vue] is not None:
            self.vues[nom_vue].afficher(self.contenu)
        for cle, (ligne, btn) in self.boutons.items():
            couleur = C_SIDEBAR_ACTIVE if cle == nom_vue else C_SIDEBAR_BTN
            ligne.configure(bg=couleur)
            btn.configure(bg=couleur)
            self.badges[cle].configure(bg=couleur)

    def _actualiser_badges(self):
        try:
            if "file_attente" in self.badges:
                from models import file_attente
                nb = sum(n for _, n in file_attente.compter_en_attente_par_specialite())
                self._maj_badge("file_attente", nb)
            if "rendez_vous" in self.badges:
                from models import rendez_vous
                nb = len(rendez_vous.charger_aujourd_hui())
                self._maj_badge("rendez_vous", nb)
        except Exception:
            pass
        self.parent.after(RAFRAICHISSEMENT_BADGES_MS, self._actualiser_badges)

    def _maj_badge(self, cle, nb):
        badge = self.badges.get(cle)
        if badge is None:
            return
        if nb > 0:
            badge.configure(text=str(nb), fg="#FFD166" if nb < 5 else "#FF6B6B")
        else:
            badge.configure(text="")

    def _deconnexion(self):
        from tkinter import messagebox
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            import session
            session.deconnecter()
            self.parent.destroy()
