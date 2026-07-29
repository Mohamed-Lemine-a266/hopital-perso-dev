import tempfile
import webbrowser
from models import parametres


def _en_tete_html():
    nom = parametres.nom_hopital()
    email = parametres.email()
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #1B4965; padding-bottom: 10px; margin-bottom: 20px; }}
        .header h1 {{ color: #1B4965; margin: 0; font-size: 22px; }}
        .header p {{ margin: 3px 0; font-size: 12px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #1B4965; color: white; padding: 8px; text-align: left; font-size: 13px; }}
        td {{ padding: 6px 8px; border-bottom: 1px solid #ddd; font-size: 13px; }}
        .label {{ font-weight: bold; width: 180px; }}
        .section {{ font-size: 16px; font-weight: bold; color: #1B4965; margin-top: 20px; }}
        .signature {{ margin-top: 50px; text-align: right; }}
        .ticket {{ border: 2px dashed #333; padding: 20px; max-width: 350px; margin: auto; text-align: center; }}
        .ticket h2 {{ margin: 5px 0; }}
        .ticket .numero {{ font-size: 48px; font-weight: bold; color: #1B4965; }}
        @media print {{ body {{ margin: 15px; }} }}
    </style></head><body>
    <div class="header"><h1>{nom}</h1>
    {"<p>" + email + "</p>" if email else ""}</div>"""


def _ouvrir(html):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
    f.write(html)
    f.close()
    webbrowser.open('file://' + f.name)


def imprimer_ticket(numero_ticket, patient_nom, patient_prenom, specialite, medecin, heure, priorite):
    html = _en_tete_html()
    html += f"""
    <div class="ticket">
        <p>Ticket de file d'attente</p>
        <div class="numero">{numero_ticket}</div>
        <h2>{patient_nom} {patient_prenom}</h2>
        <p><strong>Spécialité :</strong> {specialite}</p>
        <p><strong>Médecin :</strong> Dr. {medecin}</p>
        <p><strong>Heure d'arrivée :</strong> {heure}</p>
        <p><strong>Priorité :</strong> {priorite}</p>
    </div></body></html>"""
    _ouvrir(html)


def imprimer_fiche_patient(p, consultations_list, rdv_list, infos_medicales=None,
                            derniere_vitale=None, documents_list=None):
    html = _en_tete_html()
    html += f"""<p class="section">Fiche Patient</p>
    <table>
        <tr><td class="label">CNI</td><td>{p[1]}</td></tr>
        <tr><td class="label">Nom</td><td>{p[2]}</td></tr>
        <tr><td class="label">Prénom</td><td>{p[3]}</td></tr>
        <tr><td class="label">Sexe</td><td>{p[4] or '—'}</td></tr>
        <tr><td class="label">Date de naissance</td><td>{p[5] or '—'}</td></tr>
        <tr><td class="label">Téléphone</td><td>{p[6] or '—'}</td></tr>
        <tr><td class="label">Adresse</td><td>{p[7] or '—'}</td></tr>
        <tr><td class="label">Date d'inscription</td><td>{p[8]}</td></tr>
    </table>"""

    if infos_medicales and any(infos_medicales):
        allergies, atcd_med, atcd_chir, groupe = infos_medicales
        html += '<p class="section">Informations médicales</p><table>'
        html += f'<tr><td class="label">Groupe sanguin</td><td>{groupe or "—"}</td></tr>'
        html += f'<tr><td class="label">Allergies</td><td>{allergies or "—"}</td></tr>'
        html += f'<tr><td class="label">Antécédents médicaux</td><td>{atcd_med or "—"}</td></tr>'
        html += f'<tr><td class="label">Antécédents chirurgicaux</td><td>{atcd_chir or "—"}</td></tr>'
        html += "</table>"

    if derniere_vitale:
        _, dv_date, taille, poids, temp, tension, freq, sat = derniere_vitale
        html += f'<p class="section">Dernières constantes vitales ({dv_date})</p><table>'
        html += f'<tr><td class="label">Taille</td><td>{taille or "—"} cm</td></tr>'
        html += f'<tr><td class="label">Poids</td><td>{poids or "—"} kg</td></tr>'
        html += f'<tr><td class="label">Température</td><td>{temp or "—"} °C</td></tr>'
        html += f'<tr><td class="label">Tension artérielle</td><td>{tension or "—"}</td></tr>'
        html += f'<tr><td class="label">Fréquence cardiaque</td><td>{freq or "—"} bpm</td></tr>'
        html += f'<tr><td class="label">Saturation O2</td><td>{sat or "—"} %</td></tr>'
        html += "</table>"
    if consultations_list:
        html += '<p class="section">Historique des consultations</p><table><tr><th>Date</th><th>Médecin</th><th>Diagnostic</th><th>Traitement</th></tr>'
        for c in consultations_list:
            html += f"<tr><td>{c[1]}</td><td>{c[2]}</td><td>{c[4] or ''}</td><td>{c[5] or ''}</td></tr>"
        html += "</table>"
    if rdv_list:
        html += '<p class="section">Rendez-vous</p><table><tr><th>Date</th><th>Médecin</th><th>Motif</th><th>Statut</th></tr>'
        for r in rdv_list:
            html += f"<tr><td>{r[5]}</td><td>{r[3]}</td><td>{r[7] or ''}</td><td>{r[8]}</td></tr>"
        html += "</table>"

    if documents_list:
        html += '<p class="section">Documents associés</p><table><tr><th>Type</th><th>Fichier</th><th>Ajouté le</th></tr>'
        for d in documents_list:
            html += f"<tr><td>{d[1]}</td><td>{d[2]}</td><td>{d[4]}</td></tr>"
        html += "</table>"

    html += "</body></html>"
    _ouvrir(html)


def imprimer_consultation(patient_nom, medecin_nom, specialite, date_h, diagnostic, traitement, observations):
    html = _en_tete_html()
    html += f"""<p class="section">Compte-rendu de consultation</p>
    <table>
        <tr><td class="label">Patient</td><td>{patient_nom}</td></tr>
        <tr><td class="label">Médecin</td><td>Dr. {medecin_nom}</td></tr>
        <tr><td class="label">Spécialité</td><td>{specialite}</td></tr>
        <tr><td class="label">Date</td><td>{date_h}</td></tr>
        <tr><td class="label">Diagnostic</td><td>{diagnostic or '—'}</td></tr>
        <tr><td class="label">Traitement</td><td>{traitement or '—'}</td></tr>
        <tr><td class="label">Observations</td><td>{observations or '—'}</td></tr>
    </table>
    <div class="signature">
        <p>Signature du médecin</p>
        <p>_________________________</p>
    </div></body></html>"""
    _ouvrir(html)
