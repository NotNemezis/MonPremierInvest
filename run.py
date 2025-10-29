from emprunt.calcul_emprunt import calcul_emprunt_excel

mensualite, cout, fichier = calcul_emprunt_excel(
    montant=20000,
    taux_annuel=3.5,
    duree_annees=10,
)