import tkinter as tk
from tkinter import messagebox
from config import C_FOND, C_PRIMAIRE, C_SURFACE, C_BORDURE, C_TEXTE_SECONDAIRE, C_HOVER_PRIMAIRE
from config import FONT_H1, FONT_H2, FONT_TEXTE, FONT_PETIT, ICONS
from models import utilisateur, parametres


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        self.frame = tk.Frame(root, bg=C_FOND)
        self.frame.pack(fill="both", expand=True)

        # Carte centrale avec ombre simulée (double frame)
        ombre = tk.Frame(self.frame, bg="#D5DAE0")
        ombre.place(relx=0.5, rely=0.46, anchor="center", width=442, height=442)
        carte = tk.Frame(self.frame, bg=C_SURFACE, highlightbackground=C_BORDURE,
                          highlightthickness=1)
        carte.place(relx=0.5, rely=0.45, anchor="center", width=440, height=440)

        contenu = tk.Frame(carte, bg=C_SURFACE)
        contenu.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(contenu, text=ICONS.get("logo_defaut", "🏥"), font=("Arial", 40),
                 bg=C_SURFACE).pack(pady=(0, 6))

        nom_h = parametres.nom_hopital()
        tk.Label(contenu, text=nom_h, font=FONT_H1, bg=C_SURFACE, fg=C_PRIMAIRE).pack()
        tk.Label(contenu, text="Système de Gestion Hospitalière", font=FONT_PETIT,
                 bg=C_SURFACE, fg=C_TEXTE_SECONDAIRE).pack(pady=(2, 22))

        tk.Label(contenu, text="Nom d'utilisateur", font=FONT_PETIT, bg=C_SURFACE,
                 fg=C_TEXTE_SECONDAIRE, anchor="w").pack(fill="x")
        self.user_entry = tk.Entry(contenu, width=30, font=FONT_TEXTE, relief="solid",
                                    bd=1, highlightthickness=1,
                                    highlightbackground=C_BORDURE, highlightcolor=C_PRIMAIRE)
        self.user_entry.pack(pady=(2, 14), ipady=5)
        self.user_entry.focus_set()

        tk.Label(contenu, text="Mot de passe", font=FONT_PETIT, bg=C_SURFACE,
                 fg=C_TEXTE_SECONDAIRE, anchor="w").pack(fill="x")
        self.pwd_entry = tk.Entry(contenu, width=30, font=FONT_TEXTE, show="•", relief="solid",
                                   bd=1, highlightthickness=1,
                                   highlightbackground=C_BORDURE, highlightcolor=C_PRIMAIRE)
        self.pwd_entry.pack(pady=(2, 22), ipady=5)
        self.pwd_entry.bind("<Return>", lambda e: self.connexion())

        btn = tk.Button(contenu, text="Se connecter", command=self.connexion,
                         bg=C_PRIMAIRE, fg="white", font=FONT_H2, relief="flat",
                         activebackground=C_HOVER_PRIMAIRE, activeforeground="white",
                         cursor="hand2", bd=0, padx=30, pady=8)
        btn.pack(pady=(0, 14))

        tk.Label(contenu, text="Compte par défaut : admin / admin",
                 bg=C_SURFACE, fg="#B0B8C0", font=FONT_PETIT).pack()

    def connexion(self):
        nom_u = self.user_entry.get().strip()
        mdp = self.pwd_entry.get()
        if not nom_u or not mdp:
            messagebox.showwarning("Connexion", "Remplissez les deux champs.")
            return
        u = utilisateur.authentifier(nom_u, mdp)
        if u is None:
            messagebox.showerror("Connexion échouée", "Identifiants incorrects ou compte désactivé.")
            self.pwd_entry.delete(0, tk.END)
            return
        perms = utilisateur.obtenir_permissions(u["id"], u["role_id"])
        import session
        session.definir_utilisateur(u, perms)
        self.frame.destroy()
        self.on_success(u, perms)
