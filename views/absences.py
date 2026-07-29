import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from config import C_FOND, C_PRIMAIRE, C_DANGER, FONT_H2, FONT_TEXTE
from views.widgets import DateEntry
from models import absence, audit
import session


class PopupAbsences:
    """Popup de gestion des absences planifiées d'un médecin (congés, formations, etc.)."""

    def __init__(self, parent_toplevel, medecin_id, nom_medecin):
        self.medecin_id = medecin_id
        self.popup = Toplevel(parent_toplevel)
        self.popup.title(f"Absences planifiées — {nom_medecin}")
        self.popup.geometry("560x420")
        self.popup.configure(bg=C_FOND)
        self.popup.grab_set()

        tk.Label(self.popup, text=f"Absences de {nom_medecin}", font=FONT_H2,
                 bg=C_FOND, fg=C_PRIMAIRE).pack(pady=(15, 10))

        zone_form = tk.Frame(self.popup, bg=C_FOND)
        zone_form.pack(pady=5)

        tk.Label(zone_form, text="Du :", bg=C_FOND, font=FONT_TEXTE).grid(row=0, column=0, padx=5, pady=5)
        self.debut_entry = DateEntry(zone_form, width=11)
        self.debut_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(zone_form, text="Au :", bg=C_FOND, font=FONT_TEXTE).grid(row=0, column=2, padx=5, pady=5)
        self.fin_entry = DateEntry(zone_form, width=11)
        self.fin_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(zone_form, text="Motif :", bg=C_FOND, font=FONT_TEXTE).grid(row=1, column=0, padx=5, pady=5)
        self.motif_entry = tk.Entry(zone_form, width=35)
        self.motif_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Button(self.popup, text="Ajouter cette absence", command=self._ajouter,
                  bg=C_PRIMAIRE, fg="white", padx=10, pady=4).pack(pady=8)

        zone_tab = tk.Frame(self.popup)
        zone_tab.pack(fill="both", expand=True, padx=15, pady=10)
        cols = ("debut", "fin", "motif")
        self.tableau = ttk.Treeview(zone_tab, columns=cols, show="headings", height=8)
        for c, t, w in [("debut", "Du", 110), ("fin", "Au", 110), ("motif", "Motif", 260)]:
            self.tableau.heading(c, text=t)
            self.tableau.column(c, width=w)
        self.tableau.pack(fill="both", expand=True)

        tk.Button(self.popup, text="Supprimer l'absence sélectionnée", command=self._supprimer,
                  bg=C_DANGER, fg="white", padx=10, pady=4).pack(pady=8)

        self._charger()

    def _charger(self):
        for r in self.tableau.get_children():
            self.tableau.delete(r)
        for a in absence.charger_par_medecin(self.medecin_id):
            self.tableau.insert("", "end", iid=a[0], values=(a[1], a[2], a[3] or ""))

    def _ajouter(self):
        debut = self.debut_entry.get().strip()
        fin = self.fin_entry.get().strip()
        if not debut or not fin:
            messagebox.showwarning("Champs requis", "Les deux dates sont obligatoires.", parent=self.popup)
            return
        if fin < debut:
            messagebox.showwarning("Dates invalides", "La date de fin doit être postérieure à la date de début.",
                                    parent=self.popup)
            return
        motif = self.motif_entry.get().strip()
        aid = absence.ajouter(self.medecin_id, debut, fin, motif)
        audit.enregistrer(session.utilisateur_id(), session.utilisateur_nom_complet(),
                           "création", "medecins", self.medecin_id, f"Absence planifiée {debut} → {fin}")
        self._charger()
        self.debut_entry.delete(0, tk.END)
        self.fin_entry.delete(0, tk.END)
        self.motif_entry.delete(0, tk.END)

    def _supprimer(self):
        sel = self.tableau.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette absence ?", parent=self.popup):
            return
        absence.supprimer(sel[0])
        self._charger()
