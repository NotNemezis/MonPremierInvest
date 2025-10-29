from openpyxl import Workbook
from datetime import datetime

def calcul_emprunt_excel(montant, taux_annuel, duree_annees):
    """
    Calcule un tableau d'amortissement d'un emprunt et exporte le résultat en Excel.
    Tout est fait "à la main", sans fonction mathématique avancée.

    Retourne :
    - mensualite : montant constant des mensualités
    - cout_total : coût total du crédit (intérêts)
    - fichier_excel : nom du fichier généré
    """
    # Nom automatique du fichier
    fichier_excel = f"tableau_amortissement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    # Conversion du taux annuel en taux mensuel
    taux_mensuel = taux_annuel / 100 / 12
    nb_mois = duree_annees * 12

    # Calcul de (1 + taux_mensuel)^nb_mois "à la main"
    facteur = 1.0
    for _ in range(nb_mois):
        facteur *= (1 + taux_mensuel)

    # Calcul de la mensualité (formule manuelle)
    mensualite = montant * (taux_mensuel * facteur) / (facteur - 1)

    capital_restant = montant
    total_interets = 0

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Amortissement"

    headers = ["Mois", "Mensualité (€)", "Intérêts (€)", "Principal (€)", "Capital restant dû (€)"]
    ws.append(headers)

    for mois in range(1, nb_mois + 1):
        interet = capital_restant * taux_mensuel
        principal = mensualite - interet
        capital_restant -= principal
        total_interets += interet

        ws.append([
            mois,
            round(mensualite, 2),
            round(interet, 2),
            round(principal, 2),
            round(max(capital_restant, 0), 2)
        ])

    wb.save(fichier_excel)

    montant_total_rembourse = mensualite * nb_mois

    print(f"✅ Fichier Excel généré : {fichier_excel}")
    print(f"Mensualité : {mensualite:.2f} €")
    print(f"Coût total des intérêts : {total_interets:.2f} €")
    print(f"Montant total remboursé : {montant_total_rembourse:.2f} €")

    return mensualite, total_interets, fichier_excel