import tkinter as tk
from tkinter import Toplevel
from datetime import date
from config import C_PRIMAIRE, C_SIDEBAR
from models import file_attente, parametres

RAFRAICHISSEMENT_MS = 4000


class EcranPublic:
    """Fenêtre plein écran affichant les derniers tickets appelés — à projeter
    dans la salle d'attente. Se ferme avec la touche Échap."""

    def __init__(self, parent):
        self.popup = Toplevel(parent)
        self.popup.title("File d'attente — Écran public")
        self.popup.configure(bg=C_SIDEBAR)
        try:
            self.popup.attributes("-fullscreen", True)
        except tk.TclError:
            self.popup.geometry("1000x700")
        self.popup.bind("<Escape>", lambda e: self.popup.destroy())

        tk.Label(self.popup, text=parametres.nom_hopital(), font=("Segoe UI", 26, "bold"),
                 bg=C_SIDEBAR, fg="white").pack(pady=(30, 5))
        tk.Label(self.popup, text="Derniers tickets appelés", font=("Segoe UI", 16),
                 bg=C_SIDEBAR, fg="#89C2D9").pack(pady=(0, 20))

        self.zone_liste = tk.Frame(self.popup, bg=C_SIDEBAR)
        self.zone_liste.pack(fill="both", expand=True, padx=60)

        self.horloge_label = tk.Label(self.popup, font=("Segoe UI", 12), bg=C_SIDEBAR, fg="#89C2D9")
        self.horloge_label.pack(pady=15)

        self._actualiser()
        self._tick_horloge()

    def _actualiser(self):
        for w in self.zone_liste.winfo_children():
            w.destroy()

        appeles = file_attente.derniers_appeles(limite=8)
        if not appeles:
            tk.Label(self.zone_liste, text="Aucun ticket appelé pour le moment.",
                     font=("Segoe UI", 16, "italic"), bg=C_SIDEBAR, fg="#89C2D9").pack(pady=40)
        else:
            for i, (ticket, medecin, specialite, statut, heure_appel) in enumerate(appeles):
                couleur_fond = C_PRIMAIRE if i == 0 else "#274C5B"
                taille = 34 if i == 0 else 20
                ligne = tk.Frame(self.zone_liste, bg=couleur_fond)
                ligne.pack(fill="x", pady=4)
                tk.Label(ligne, text=ticket, font=("Segoe UI", taille, "bold"),
                         bg=couleur_fond, fg="white", width=8).pack(side="left", padx=15, pady=8)
                tk.Label(ligne, text=f"Dr. {medecin}  —  {specialite}",
                         font=("Segoe UI", taille - 8 if taille > 20 else 12),
                         bg=couleur_fond, fg="white").pack(side="left", padx=10)
                heure = heure_appel.split(" ")[-1] if heure_appel else ""
                tk.Label(ligne, text=heure, font=("Segoe UI", 12),
                         bg=couleur_fond, fg="#B8C4CE").pack(side="right", padx=15)

        self.popup.after(RAFRAICHISSEMENT_MS, self._actualiser)

    def _tick_horloge(self):
        import datetime
        self.horloge_label.config(text=datetime.datetime.now().strftime("%A %d %B %Y — %H:%M:%S"))
        self.popup.after(1000, self._tick_horloge)
