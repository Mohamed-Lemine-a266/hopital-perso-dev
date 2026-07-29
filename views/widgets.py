"""
Widgets réutilisables pour toute l'application :
  - DateEntry : champ date avec bouton calendrier (popup)
  - HeureEntry : champ heure avec sélecteurs Heure/Minute (Spinbox)

Ces widgets remplacent les Entry texte libres pour les dates et heures.
Ils utilisent uniquement tkinter — aucune bibliothèque externe.
"""
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date, datetime
from config import C_PRIMAIRE, C_FOND


class DateEntry(tk.Frame):
    """Champ de saisie de date avec bouton calendrier. Valeur au format AAAA-MM-JJ."""

    def __init__(self, parent, width=11, date_defaut=None, **kwargs):
        super().__init__(parent, bg=parent["bg"] if "bg" in parent.keys() else C_FOND)
        self.entry = tk.Entry(self, width=width, **kwargs)
        self.entry.pack(side="left")
        if date_defaut:
            self.entry.insert(0, date_defaut)
        self.btn = tk.Button(self, text="📅", command=self._ouvrir_calendrier,
                              width=2, relief="flat", bg="#E8F0F6", cursor="hand2")
        self.btn.pack(side="left", padx=(2, 0))
        self._popup = None

    def get(self):
        return self.entry.get().strip()

    def set(self, valeur):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, valeur)

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, texte):
        self.entry.insert(index, texte)

    def bind(self, *args, **kwargs):
        self.entry.bind(*args, **kwargs)

    def _ouvrir_calendrier(self):
        if self._popup is not None:
            self._popup.destroy()
        try:
            base = datetime.strptime(self.get(), "%Y-%m-%d").date()
        except ValueError:
            base = date.today()
        self._annee, self._mois = base.year, base.month

        self._popup = tk.Toplevel(self)
        self._popup.title("Choisir une date")
        self._popup.resizable(False, False)
        self._popup.transient(self.winfo_toplevel())
        self._popup.grab_set()

        # Positionner sous le bouton
        x = self.btn.winfo_rootx()
        y = self.btn.winfo_rooty() + self.btn.winfo_height()
        self._popup.geometry(f"+{x}+{y}")

        self._construire_calendrier()

    def _construire_calendrier(self):
        for w in self._popup.winfo_children():
            w.destroy()

        nav = tk.Frame(self._popup, bg=C_PRIMAIRE)
        nav.pack(fill="x")
        tk.Button(nav, text="◀", command=self._mois_precedent, relief="flat",
                  bg=C_PRIMAIRE, fg="white", cursor="hand2").pack(side="left", padx=5, pady=5)
        mois_noms = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet",
                     "Août","Septembre","Octobre","Novembre","Décembre"]
        tk.Label(nav, text=f"{mois_noms[self._mois-1]} {self._annee}",
                 bg=C_PRIMAIRE, fg="white", font=("Arial", 10, "bold"), width=16).pack(side="left")
        tk.Button(nav, text="▶", command=self._mois_suivant, relief="flat",
                  bg=C_PRIMAIRE, fg="white", cursor="hand2").pack(side="left", padx=5, pady=5)

        grille = tk.Frame(self._popup, bg="white")
        grille.pack()

        for i, j in enumerate(["Lu","Ma","Me","Je","Ve","Sa","Di"]):
            tk.Label(grille, text=j, width=4, bg="white", fg="#888",
                     font=("Arial", 8, "bold")).grid(row=0, column=i, padx=1, pady=1)

        cal = calendar.Calendar(firstweekday=0)
        semaine_idx = 1
        for semaine in cal.monthdayscalendar(self._annee, self._mois):
            for i, jour in enumerate(semaine):
                if jour == 0:
                    tk.Label(grille, text="", width=4, bg="white").grid(row=semaine_idx, column=i)
                else:
                    est_aujourdhui = date(self._annee, self._mois, jour) == date.today()
                    btn = tk.Button(grille, text=str(jour), width=4, relief="flat",
                                    bg="#E8F0F6" if est_aujourdhui else "white",
                                    cursor="hand2",
                                    command=lambda j=jour: self._selectionner(j))
                    btn.grid(row=semaine_idx, column=i, padx=1, pady=1)
            semaine_idx += 1

    def _mois_precedent(self):
        self._mois -= 1
        if self._mois == 0:
            self._mois = 12
            self._annee -= 1
        self._construire_calendrier()

    def _mois_suivant(self):
        self._mois += 1
        if self._mois == 13:
            self._mois = 1
            self._annee += 1
        self._construire_calendrier()

    def _selectionner(self, jour):
        d = date(self._annee, self._mois, jour)
        self.set(d.isoformat())
        self._popup.destroy()
        self._popup = None
        self.entry.event_generate("<<DateSelected>>")


class HeureEntry(tk.Frame):
    """Sélecteur d'heure avec deux Spinbox (heures/minutes). Valeur au format HH:MM."""

    def __init__(self, parent, heure_defaut=None, pas_minutes=5, **kwargs):
        bg = parent["bg"] if "bg" in parent.keys() else C_FOND
        super().__init__(parent, bg=bg)

        self.var_h = tk.StringVar(value="08")
        self.var_m = tk.StringVar(value="00")

        if heure_defaut:
            try:
                h, m = heure_defaut.split(":")
                self.var_h.set(h)
                self.var_m.set(m)
            except ValueError:
                pass

        self.spin_h = tk.Spinbox(self, from_=0, to=23, width=3, format="%02.0f",
                                  textvariable=self.var_h, wrap=True, justify="center")
        self.spin_h.pack(side="left")
        tk.Label(self, text=":", bg=bg).pack(side="left")
        minutes_valides = [f"{m:02d}" for m in range(0, 60, pas_minutes)]
        self.spin_m = tk.Spinbox(self, values=minutes_valides, width=3,
                                  textvariable=self.var_m, wrap=True, justify="center")
        self.spin_m.pack(side="left")

    def get(self):
        h = self.var_h.get().strip().zfill(2)
        m = self.var_m.get().strip().zfill(2)
        return f"{h}:{m}"

    def set(self, valeur):
        try:
            h, m = valeur.split(":")
            self.var_h.set(h)
            self.var_m.set(m)
        except (ValueError, AttributeError):
            pass

    def delete(self, *args):
        self.var_h.set("08")
        self.var_m.set("00")

    def insert(self, index, texte):
        self.set(texte)
