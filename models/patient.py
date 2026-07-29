from database import curseur, connection


def ajouter(numero_cni, nom, prenom, sexe, date_naissance, telephone, adresse, date_inscription):
    curseur.execute(
        """INSERT INTO patients (numero_cni,nom,prenom,sexe,date_naissance,telephone,adresse,date_inscription)
           VALUES (?,?,?,?,?,?,?,?)""",
        (numero_cni, nom, prenom, sexe, date_naissance, telephone, adresse, date_inscription))
    connection.commit()
    return curseur.lastrowid


def modifier(pid, numero_cni, nom, prenom, sexe, date_naissance, telephone, adresse):
    curseur.execute(
        """UPDATE patients SET numero_cni=?,nom=?,prenom=?,sexe=?,date_naissance=?,telephone=?,adresse=?
           WHERE id=?""",
        (numero_cni, nom, prenom, sexe, date_naissance, telephone, adresse, pid))
    connection.commit()


def supprimer(pid):
    curseur.execute("DELETE FROM patients WHERE id=?", (pid,))
    connection.commit()


def charger_tous():
    curseur.execute(
        "SELECT id,numero_cni,nom,prenom,sexe,date_naissance,telephone,adresse,date_inscription FROM patients ORDER BY nom")
    return curseur.fetchall()


def obtenir_par_id(pid):
    curseur.execute(
        "SELECT id,numero_cni,nom,prenom,sexe,date_naissance,telephone,adresse,date_inscription FROM patients WHERE id=?",
        (pid,))
    return curseur.fetchone()


def rechercher_par_cni(cni):
    curseur.execute(
        "SELECT id,numero_cni,nom,prenom,sexe,date_naissance,telephone,adresse,date_inscription FROM patients WHERE numero_cni=?",
        (cni,))
    return curseur.fetchone()


def rechercher(terme):
    t = f"%{terme}%"
    curseur.execute(
        """SELECT id,numero_cni,nom,prenom,sexe,date_naissance,telephone,adresse,date_inscription
           FROM patients WHERE numero_cni LIKE ? OR nom LIKE ? OR prenom LIKE ? OR telephone LIKE ?
           ORDER BY nom""", (t, t, t, t))
    return curseur.fetchall()


def cni_existe(cni, exclure_id=None):
    if exclure_id:
        curseur.execute("SELECT id FROM patients WHERE numero_cni=? AND id!=?", (cni, exclure_id))
    else:
        curseur.execute("SELECT id FROM patients WHERE numero_cni=?", (cni,))
    return curseur.fetchone() is not None


def a_des_enregistrements(pid):
    for t in ["file_attente", "rendez_vous", "consultations"]:
        curseur.execute(f"SELECT COUNT(*) FROM {t} WHERE patient_id=?", (pid,))
        if curseur.fetchone()[0] > 0:
            return True
    return False


def prochain_numero_auto(prefixe):
    """Génère le prochain numéro HOP-0001, HOP-0002, etc."""
    curseur.execute("SELECT numero_cni FROM patients WHERE numero_cni LIKE ? ORDER BY numero_cni DESC LIMIT 1",
                    (f"{prefixe}-%",))
    r = curseur.fetchone()
    if r is None:
        return f"{prefixe}-0001"
    try:
        dernier = int(r[0].split("-")[-1])
        return f"{prefixe}-{dernier + 1:04d}"
    except (ValueError, IndexError):
        return f"{prefixe}-0001"


# ── Informations médicales (allergies, antécédents, groupe sanguin) ──
# Fonctions additives : n'affectent pas les signatures existantes ni les
# index utilisés dans les vues déjà développées (obtenir_par_id, charger_tous...).

def obtenir_infos_medicales(pid):
    curseur.execute(
        "SELECT allergies, antecedents_medicaux, antecedents_chirurgicaux, groupe_sanguin "
        "FROM patients WHERE id=?", (pid,))
    return curseur.fetchone()


def modifier_infos_medicales(pid, allergies, antecedents_medicaux, antecedents_chirurgicaux, groupe_sanguin):
    curseur.execute(
        """UPDATE patients SET allergies=?, antecedents_medicaux=?, antecedents_chirurgicaux=?, groupe_sanguin=?
           WHERE id=?""",
        (allergies, antecedents_medicaux, antecedents_chirurgicaux, groupe_sanguin, pid))
    connection.commit()


# ── Validation du format CNI ──
import re as _re

def format_cni_valide(cni, prefixe_auto="HOP"):
    """
    Un CNI valide est soit :
      - un numéro auto-généré au format PREFIXE-0001 (patients sans pièce d'identité) ;
      - un identifiant officiel : au moins 5 caractères alphanumériques (lettres/chiffres),
        peut inclure des espaces ou tirets.
    """
    if not cni:
        return False
    if _re.fullmatch(rf"{prefixe_auto}-\d{{4,}}", cni):
        return True
    return _re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 \-]{4,19}", cni) is not None
