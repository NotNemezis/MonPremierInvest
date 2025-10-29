# MonPremierInvest' - POC Streamlit
# ==================================================
# Application simple pour:
# 1) Collecter la situation utilisateur
# 2) Simulateur d'emprunt (capacité sans apport)
# 3) Calculer l'épargne mensuelle nécessaire pour constituer un apport
# 4) Présenter un panorama simple des placements
# 
# Usage: streamlit run MonPremierInvest_poc_app.py

import streamlit as st
import pandas as pd
import numpy as np
from math import isclose

st.set_page_config(page_title="MonPremierInvest' - POC", layout="centered")

# ------------------------- Helpers -------------------------

def annuity_present_value(monthly_payment, monthly_rate, n_months):
    """Calcule le capital empruntable donné un paiement mensuel, taux mensuel et nombre de mois.
    PV = P * (1 - (1+r)^-N) / r
    Si r == 0, PV = P * N
    """
    if n_months <= 0:
        return 0.0
    if isclose(monthly_rate, 0.0):
        return monthly_payment * n_months
    return monthly_payment * (1 - (1 + monthly_rate) ** (-n_months)) / monthly_rate


def annuity_monthly_payment(pv, monthly_rate, n_months):
    """Inverse: calculer la mensualité pour un prêt de capital pv.
    P = pv * r / (1 - (1+r)^-N)
    Si r == 0, P = pv / N
    """
    if n_months <= 0:
        return 0.0
    if isclose(monthly_rate, 0.0):
        return pv / n_months
    return pv * monthly_rate / (1 - (1 + monthly_rate) ** (-n_months))


def future_value_of_series(monthly_deposit, monthly_rate, n_months, initial=0.0):
    """FV of a series of monthly deposits plus initial capital.
    FV = initial*(1+r)^N + monthly_deposit * ((1+r)^N - 1) / r
    If r == 0: FV = initial + monthly_deposit * N
    """
    if n_months <= 0:
        return initial
    if isclose(monthly_rate, 0.0):
        return initial + monthly_deposit * n_months
    return initial * (1 + monthly_rate) ** n_months + monthly_deposit * ((1 + monthly_rate) ** n_months - 1) / monthly_rate


def required_monthly_deposit(target, n_months, annual_rate, initial=0.0):
    """Calcule la mensualité nécessaire pour atteindre target en n_months avec un taux annuel donné.
    monthly_rate = annual_rate / 12
    m = (target - initial*(1+r)^N) * r / ((1+r)^N - 1)
    Si r == 0: m = (target - initial) / N
    """
    if n_months <= 0:
        return float('inf')
    r = annual_rate / 12.0
    if isclose(r, 0.0):
        return max(0.0, (target - initial) / n_months)
    denom = (1 + r) ** n_months - 1
    if isclose(denom, 0.0):
        return max(0.0, (target - initial) / n_months)
    return max(0.0, (target - initial * (1 + r) ** n_months) * r / denom)

# ------------------------- Data: placements -------------------------
placements = [
    {"Type": "Livret (ex: Livret A)", "Rendement_moyen_annuel_%": 3.0, "Risque": "Faible", "Horizon": "Court"},
    {"Type": "Compte à terme", "Rendement_moyen_annuel_%": 2.0, "Risque": "Faible", "Horizon": "Court"},
    {"Type": "Assurance-vie (fonds euros)", "Rendement_moyen_annuel_%": 2.5, "Risque": "Faible", "Horizon": "Moyen-Long"},
    {"Type": "Assurance-vie (UC)", "Rendement_moyen_annuel_%": 4.5, "Risque": "Moyen", "Horizon": "Long"},
    {"Type": "ETF (MSCI World)", "Rendement_moyen_annuel_%": 6.5, "Risque": "Élevé", "Horizon": "Long"},
    {"Type": "SCPI (immobilier collectif)", "Rendement_moyen_annuel_%": 4.5, "Risque": "Moyen", "Horizon": "Moyen-Long"},
    {"Type": "Crowdfunding immobilier", "Rendement_moyen_annuel_%": 6.0, "Risque": "Élevé", "Horizon": "Moyen"},
    {"Type": "Obligations (mix)", "Rendement_moyen_annuel_%": 3.0, "Risque": "Moyen", "Horizon": "Moyen-Long"},
    {"Type": "Cryptomonnaies", "Rendement_moyen_annuel_%": 15.0, "Risque": "Très élevé", "Horizon": "Long"}
]
placements_df = pd.DataFrame(placements)

# ------------------------- UI -------------------------
st.title("MonPremierInvest' — POC")
st.write("Application simplifiée pour aider un débutant à préparer son premier investissement. Ce POC se concentre sur profil, capacité d'emprunt, constitution d'apport, et panorama de placements.")

# Tabs
tabs = st.tabs(["1. Situation", "2. Simulateur d'emprunt", "3. Constitution d'apport", "4. Placements", "5. Exemples / Scénario"])

# ------------------------- Tab 1: Situation -------------------------
with tabs[0]:
    st.header("1. Votre situation")
    st.info("Renseignez votre situation pour personnaliser les calculs")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Âge", min_value=18, max_value=100, value=28)
        situation = st.selectbox("Situation professionnelle", ["Salarié", "Indépendant", "Étudiant", "Sans emploi", "Retraité"]) 
        revenu_mensuel = st.number_input("Revenu net mensuel (€)", min_value=0.0, value=2500.0, step=50.0)
        epargne_actuelle = st.number_input("Épargne disponible actuellement (€)", min_value=0.0, value=3000.0, step=100.0)
    with col2:
        depenses_mensuelles = st.number_input("Dépenses mensuelles moyennes (€)", min_value=0.0, value=1400.0, step=50.0)
        tol_risque = st.selectbox("Tolérance au risque", ["Faible", "Moyen", "Élevé"], index=0)
        objectif = st.selectbox("Objectif principal", ["Apport immobilier", "Constituer un capital", "Préparer la retraite", "Diversifier"])

    st.write("---")
    st.markdown("**Résumé rapide :**")
    st.write(f"Âge: {age}  Situation: {situation}  Revenu: {revenu_mensuel:.0f} €/mois  Dépenses: {depenses_mensuelles:.0f} €/mois  Épargne: {epargne_actuelle:.0f} €  Tolérance au risque: {tol_risque}  Objectif: {objectif}")

# ------------------------- Tab 2: Simulateur d'emprunt -------------------------
with tabs[1]:
    st.header("2. Simulateur d'emprunt (capacité sans apport)")
    st.write("Estimez combien vous pourriez emprunter aujourd'hui *sans apport* en vous basant sur votre capacité de remboursement.")

    st.subheader("Paramètres")
    debt_ratio = st.slider("Taux d'endettement maximal (en % des revenus)", min_value=20, max_value=40, value=33) / 100.0
    loan_years = st.select_slider("Durée de l'emprunt (années)", options=[10, 12, 15, 18, 20, 22, 25], value=20)
    annual_rate = st.number_input("Taux d'intérêt annuel (%)", min_value=0.0, value=4.0, step=0.1) / 100.0

    # Calculs
    max_monthly_payment = max(0.0, revenu_mensuel * debt_ratio - depenses_mensuelles)
    monthly_rate = annual_rate / 12.0
    n_months = loan_years * 12
    emprunt_max = annuity_present_value(max_monthly_payment, monthly_rate, n_months)
    mensualite_example = annuity_monthly_payment(emprunt_max, monthly_rate, n_months)

    st.metric("Mensualité disponible estimée", f"{max_monthly_payment:.0f} €/mois")
    st.metric("Montant empruntable estimé", f"{emprunt_max:,.0f} €")
    st.write(f"(Hypothèses: taux={annual_rate*100:.2f}% annuel, durée={loan_years} ans, taux d'endettement={debt_ratio*100:.0f}%)")

    st.write("---")
    st.subheader("Simuler un capital et affichage d'un tableau d'amortissement (exemple)")
    user_capital = st.number_input("Simuler un capital emprunté (€)", min_value=0.0, value=round(emprunt_max, -2), step=100.0)
    if user_capital > 0:
        monthly_payment = annuity_monthly_payment(user_capital, monthly_rate, n_months)
        st.write(f"Mensualité pour un prêt de {user_capital:,.0f} € sur {loan_years} ans: {monthly_payment:.2f} €/mois")

        if st.checkbox("Afficher tableau d'amortissement (premières lignes) "):
            # tableau simple (premiers 24 mois)
            balance = user_capital
            rows = []
            for month in range(1, min(25, n_months+1)):
                interest = balance * monthly_rate
                principal = monthly_payment - interest
                balance = max(0.0, balance - principal)
                rows.append({"Mois": month, "Mensualité": round(monthly_payment,2), "Intérêts": round(interest,2), "Principal": round(principal,2), "Reste": round(balance,2)})
            st.dataframe(pd.DataFrame(rows))

# ------------------------- Tab 3: Constitution d'apport -------------------------
with tabs[2]:
    st.header("3. Comment constituer un apport ?")
    st.write("Calculez combien épargner chaque mois pour atteindre un objectif d'apport en X années. Vous pouvez indiquer un taux de rendement attendu (ex: livret, fonds)")

    objectif_apport = st.number_input("Objectif d'apport souhaité (€)", min_value=0.0, value=20000.0, step=100.0)
    duree_ans = st.slider("Durée (années)", min_value=1, max_value=20, value=5)
    taux_annuel_attendu = st.number_input("Taux de rendement annuel attendu (%)", min_value=0.0, value=1.5, step=0.1) / 100.0

    n_months_apport = duree_ans * 12
    monthly_needed = required_monthly_deposit(objectif_apport, n_months_apport, taux_annuel_attendu, initial=epargne_actuelle)
    fv_with_equal_deposit = future_value_of_series(monthly_needed, taux_annuel_attendu/12.0, n_months_apport, initial=epargne_actuelle)

    st.metric("Épargne mensuelle nécessaire (approx.)", f"{monthly_needed:.0f} €/mois")
    st.write(f"Si vous partez de {epargne_actuelle:.0f} € et obtenez {taux_annuel_attendu*100:.2f}%/an, vous atteindrez {fv_with_equal_deposit:,.0f} € en {duree_ans} ans.")

    st.write("---")
    st.subheader("Calcul inverse : si je peux épargner X €/mois, que j'obtiendrai ?")
    exemple_mensuel = st.number_input("Je peux épargner chaque mois (€)", min_value=0.0, value=monthly_needed, step=10.0)
    fv2 = future_value_of_series(exemple_mensuel, taux_annuel_attendu/12.0, n_months_apport, initial=epargne_actuelle)
    st.write(f"Avec {exemple_mensuel:.0f} €/mois, vous obtiendrez ~{fv2:,.0f} € au bout de {duree_ans} ans (à {taux_annuel_attendu*100:.2f}%/an).")

# ------------------------- Tab 4: Placements -------------------------
with tabs[3]:
    st.header("4. Panorama des placements")
    st.write("Vue simple des différentes familles de placements pour un premier investisseur. Les rendements sont indicatifs et historiques — à personnaliser dans un produit final.")

    risk_filter = st.multiselect("Filtrer par niveau de risque", options=placements_df['Risque'].unique().tolist(), default=placements_df['Risque'].unique().tolist())
    horizon_filter = st.multiselect("Filtrer par horizon conseillé", options=placements_df['Horizon'].unique().tolist(), default=placements_df['Horizon'].unique().tolist())

    filtered = placements_df[placements_df['Risque'].isin(risk_filter) & placements_df['Horizon'].isin(horizon_filter)]
    st.dataframe(filtered.reset_index(drop=True))

    st.write("---")
    st.subheader("Recommandation simplifiée (démo)")
    if st.button("Obtenir une recommandation simple"):
        # règle très simple basée sur tolérance au risque
        if tol_risque == "Faible":
            reco = ["Livret (sécurité)", "Assurance-vie (fonds euros)", "Petite exposition SCPI"]
        elif tol_risque == "Moyen":
            reco = ["Assurance-vie (UC)", "SCPI", "ETF monde (exposition long terme)"]
        else:
            reco = ["ETF monde", "Cryptomonnaies (portion réduite)", "Crowdfunding (si connaissance)"]
        st.write("Recommandation (exemple):")
        for r in reco:
            st.write("- ", r)

# ------------------------- Tab 5: Exemples / Scénario -------------------------
with tabs[4]:
    st.header("5. Exemple de scénario utilisateur")
    st.write("Nous présentons un scénario type illustrant l'utilisation des deux fonctionnalités principales.")

    st.subheader("Persona: Laura, 28 ans, salariée")
    st.write("Laura gagne 2 500 €/mois, dépense 1 400 €/mois, a 3 000 € d'épargne et souhaite constituer 20 000 € d'apport en 5 ans pour un premier achat immobilier. Tolérance au risque: Faible.")
    if st.button("Simuler le scénario Laura"):
        # paramètres de Laura
        laura_revenu = 2500.0
        laura_depenses = 1400.0
        laura_epargne = 3000.0
        laura_objectif = 20000.0
        laura_duree = 5
        laura_taux = 0.015
        laura_debt_ratio = 0.33
        laura_loan_years = 20
        laura_max_monthly = max(0.0, laura_revenu * laura_debt_ratio - laura_depenses)
        laura_emprunt = annuity_present_value(laura_max_monthly, laura_taux/12.0, laura_loan_years*12)
        laura_monthly_needed = required_monthly_deposit(laura_objectif, laura_duree*12, laura_taux, initial=laura_epargne)

        st.write(f"Capacité d'emprunt estimée (sans apport) : {laura_emprunt:,.0f} €")
        st.write(f"Épargne mensuelle recommandée pour atteindre {laura_objectif} € en {laura_duree} ans : {laura_monthly_needed:.0f} €/mois")
        st.write("Recommandation produit (exemple) : privilégier une épargne sécurisée (livret, fonds euros) pour l'apport, puis allocation progressive vers ETF ou SCPI si l'horizon dépasse 5 ans.")

# ------------------------- Footer -------------------------
st.write("---")
st.markdown("**Notes & limites du POC :**   - Les calculs ci-dessus sont simplifiés et destinés à la démonstration.  - Les rendements et taux sont indicatifs et non contractuels.   - Pour un usage réel, il faudra intégrer des données de marché en temps réel, la fiscalité, et une validation réglementaire (MIFID/Conseil en investissement).")
st.markdown("_Si tu veux, je peux :_  - Générer un fichier `requirements.txt` minimal,  - Ajouter export CSV pour les scénarios,  - Étendre le simulateur d'emprunt avec comparatif taux fixes/variables,  - Ou générer une version Dockerisable du POC.")
