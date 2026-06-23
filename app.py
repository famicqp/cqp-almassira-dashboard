# -*- coding: utf-8 -*-
"""
============================================================================
 DASHBOARD STRATÉGIQUE - CENTRE DE FORMATION PROFESSIONNELLE (E-NOTE)
============================================================================
 Auteur      : Assistant IA (Data Engineer / Pedagogical Consultant)
 Description : Tableau de bord interactif pour le pilotage pédagogique
               des groupes, modules, formateurs et taux de réalisation.
 Stack       : Streamlit + Plotly + Pandas

 Fonctionnalités principales :
   1. Upload dynamique de fichiers CSV (export E-note)
   2. Nettoyage et normalisation automatique des données
   3. Cartes de performance (KPIs)
   4. Analyse des écarts pédagogiques (Gap Analysis)
   5. Alertes intelligentes (modules en retard)
   6. Indice de performance par groupe / formateur
   7. Visualisations interactives (Plotly)
============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import re

# ============================================================================
# 1. CONFIGURATION GÉNÉRALE DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Pilotage Pédagogique | CFP Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Injection CSS personnalisée pour un design moderne et confortable ---
CUSTOM_CSS = """
<style>
    .main { background-color: #0e1117; }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1c2330 0%, #161b26 100%);
        border: 1px solid #2a3340;
        padding: 18px 14px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricLabel"] { font-weight: 600; opacity: 0.85; }
    .alert-box-danger {
        background-color: rgba(220, 53, 69, 0.12);
        border-left: 5px solid #dc3545;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #ff6b6b;
    }
    .alert-box-warning {
        background-color: rgba(255, 193, 7, 0.12);
        border-left: 5px solid #ffc107;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #ffd166;
    }
    .alert-box-success {
        background-color: rgba(40, 167, 69, 0.12);
        border-left: 5px solid #28a745;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #6fd08c;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
        border-bottom: 2px solid #2a3340;
        padding-bottom: 6px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# 2. DICTIONNAIRE DE MAPPING DES COLONNES (Tolérance aux variations E-note)
# ============================================================================
# E-note exporte parfois les colonnes avec des noms légèrement différents
# (majuscules, accents, espaces). Ce dictionnaire permet une détection
# intelligente et tolérante aux erreurs de nommage.

COLUMN_ALIASES = {
    "groupe": ["groupe", "group", "classe", "section"],
    "module": ["module", "mzouaa", "mzoua", "matiere", "matière", "mz"],
    "formateur": ["formateur", "formateurs", "enseignant", "professeur", "trainer"],
    "mh_totale": ["mh totale", "mh_totale", "heures prevues", "heures prévues",
                  "mh planifiee", "mh planifiée", "heures planifiees", "volume horaire"],
    "mh_realisee": ["mh realisee", "mh réalisée", "heures realisees", "heures réalisées",
                    "mh effectuee", "mh effectuée", "heures faites"],
    "taux_realisation": ["taux realisation", "taux de réalisation", "taux_realisation",
                          "% realisation", "% réalisation", "avancement"],
    "taux_absence": ["taux absence", "taux d'absence", "taux_absence",
                      "% absence", "absenteisme", "absentéisme"],
}


# ============================================================================
# 3. FONCTIONS DE NETTOYAGE ET NORMALISATION DES DONNÉES
# ============================================================================

def normaliser_nom_colonne(nom: str) -> str:
    """
    Normalise un nom de colonne brut : minuscule, sans accents, sans espaces
    superflus, pour faciliter le matching avec COLUMN_ALIASES.

    Args:
        nom (str): nom brut de la colonne.

    Returns:
        str: nom normalisé.
    """
    try:
        nom = str(nom).strip().lower()
        # Remplacement des caractères accentués les plus courants en français
        remplacements = {
            "é": "e", "è": "e", "ê": "e", "ë": "e",
            "à": "a", "â": "a", "ä": "a",
            "î": "i", "ï": "i",
            "ô": "o", "ö": "o",
            "ù": "u", "û": "u", "ü": "u",
            "ç": "c",
        }
        for src, dst in remplacements.items():
            nom = nom.replace(src, dst)
        nom = re.sub(r"\s+", " ", nom).strip()
        return nom
    except Exception:
        return str(nom)


def detecter_colonnes(df: pd.DataFrame) -> dict:
    """
    Détecte automatiquement les colonnes clés du DataFrame en se basant
    sur le dictionnaire COLUMN_ALIASES, indépendamment de la casse ou
    des variations de nommage E-note.

    Args:
        df (pd.DataFrame): DataFrame brut chargé depuis le CSV.

    Returns:
        dict: mapping {nom_standard: nom_colonne_reel_dans_df ou None}
    """
    mapping_final = {}
    colonnes_normalisees = {normaliser_nom_colonne(c): c for c in df.columns}

    for cle_standard, alias_list in COLUMN_ALIASES.items():
        trouve = None
        for alias in alias_list:
            alias_norm = normaliser_nom_colonne(alias)
            if alias_norm in colonnes_normalisees:
                trouve = colonnes_normalisees[alias_norm]
                break
        if trouve is None:
            for col_norm, col_orig in colonnes_normalisees.items():
                if any(normaliser_nom_colonne(a) in col_norm for a in alias_list):
                    trouve = col_orig
                    break
        mapping_final[cle_standard] = trouve

    return mapping_final


def convertir_en_numerique(serie: pd.Series) -> pd.Series:
    """
    Convertit une série en valeurs numériques de manière robuste.
    Gère les cas où les nombres sont écrits en texte, avec virgule
    décimale (format français), avec symbole '%', ou avec espaces.

    Args:
        serie (pd.Series): colonne brute (souvent de type object/string).

    Returns:
        pd.Series: colonne convertie en float, NaN remplacés par 0.0.
    """
    try:
        if pd.api.types.is_numeric_dtype(serie):
            return serie.fillna(0.0).astype(float)

        serie_str = serie.astype(str)
        serie_str = serie_str.str.replace("%", "", regex=False)
        serie_str = serie_str.str.replace(" ", "", regex=False)
        serie_str = serie_str.str.replace(",", ".", regex=False)
        serie_str = serie_str.replace(
            ["nan", "None", "none", "NaN", "", "N/A", "n/a", "-"], np.nan
        )

        serie_numerique = pd.to_numeric(serie_str, errors="coerce")
        return serie_numerique.fillna(0.0)
    except Exception as erreur:
        st.warning(f"⚠️ Conversion numérique partielle sur une colonne : {erreur}")
        return pd.Series(np.zeros(len(serie)), index=serie.index)


@st.cache_data(show_spinner=False)
def charger_et_nettoyer_donnees(fichier_bytes: bytes) -> pd.DataFrame:
    """
    Pipeline complet de chargement et nettoyage d'un fichier CSV E-note.

    Étapes :
        1. Lecture tolérante (détection encodage/séparateur)
        2. Détection intelligente des colonnes
        3. Renommage standardisé
        4. Conversion des types (numériques, texte)
        5. Calcul des indicateurs dérivés (écarts, taux si absents)

    Args:
        fichier_bytes (bytes): contenu brut du fichier uploadé.

    Returns:
        pd.DataFrame: DataFrame nettoyé et prêt pour l'analyse.

    Raises:
        ValueError: si le fichier est vide ou totalement illisible.
    """
    df_brut = None
    derniere_erreur = None

    # --- Tentative de lecture avec plusieurs combinaisons encodage/séparateur ---
    for encodage in ["utf-8-sig", "utf-8", "latin1", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                df_essai = pd.read_csv(
                    io.BytesIO(fichier_bytes),
                    encoding=encodage,
                    sep=sep,
                    engine="python",
                    on_bad_lines="skip",
                )
                if df_essai.shape[1] > 1:
                    df_brut = df_essai
                    break
            except Exception as e:
                derniere_erreur = e
                continue
        if df_brut is not None:
            break

    if df_brut is None or df_brut.empty:
        raise ValueError(
            f"Impossible de lire le fichier CSV. Vérifiez le format. "
            f"Détail technique : {derniere_erreur}"
        )

    # --- Nettoyage des lignes/colonnes totalement vides ---
    df_brut = df_brut.dropna(axis=0, how="all").dropna(axis=1, how="all")
    df_brut.columns = [str(c).strip() for c in df_brut.columns]

    # --- Détection intelligente des colonnes clés ---
    mapping = detecter_colonnes(df_brut)
    df = df_brut.copy()
    renommage = {v: k for k, v in mapping.items() if v is not None}
    df = df.rename(columns=renommage)

    # --- Garantir l'existence de toutes les colonnes attendues ---
    colonnes_requises = list(COLUMN_ALIASES.keys())
    for col in colonnes_requises:
        if col not in df.columns:
            df[col] = np.nan

    # --- Nettoyage des colonnes textuelles (catégorielles) ---
    # NOTE : fillna() est appliqué AVANT astype(str). Avec les versions récentes
    # de pandas (dtype "str" natif), convertir un NaN en texte puis le comparer
    # à la chaîne "nan" peut échouer silencieusement. Traiter le NaN en amont
    # garantit un nettoyage fiable quelle que soit la version de pandas.
    for col_texte in ["groupe", "module", "formateur"]:
        try:
            df[col_texte] = (
                df[col_texte]
                .fillna("Non spécifié")
                .astype(str)
                .str.strip()
                .replace(["nan", "None", ""], "Non spécifié")
            )
        except Exception:
            df[col_texte] = "Non spécifié"

    # --- Conversion robuste des colonnes numériques ---
    for col_num in ["mh_totale", "mh_realisee", "taux_realisation", "taux_absence"]:
        df[col_num] = convertir_en_numerique(df[col_num])

    # --- Calcul du taux de réalisation s'il est absent ou incohérent ---
    masque_taux_invalide = (df["taux_realisation"] <= 0) & (df["mh_totale"] > 0)
    df.loc[masque_taux_invalide, "taux_realisation"] = (
        df.loc[masque_taux_invalide, "mh_realisee"]
        / df.loc[masque_taux_invalide, "mh_totale"]
        * 100
    )
    df["taux_realisation"] = df["taux_realisation"].clip(lower=0, upper=100).round(1)

    # --- Calcul de l'écart pédagogique (Gap Analysis) ---
    df["ecart_heures"] = (df["mh_totale"] - df["mh_realisee"]).round(1)
    df["ecart_heures"] = df["ecart_heures"].clip(lower=0)

    # --- Indice de performance individuel (pondéré assiduité + réalisation) ---
    df["indice_performance"] = (
        (df["taux_realisation"] * 0.7) + ((100 - df["taux_absence"]) * 0.3)
    ).round(1)
    df["indice_performance"] = df["indice_performance"].clip(lower=0, upper=100)

    # --- Classification du statut pédagogique (pour les alertes) ---
    def classifier_statut(taux: float) -> str:
        if taux >= 85:
            return "✅ Conforme"
        elif taux >= 60:
            return "⚠️ À surveiller"
        else:
            return "🔴 Critique"

    df["statut"] = df["taux_realisation"].apply(classifier_statut)

    return df


# ============================================================================
# 4. FONCTIONS D'ANALYSE STRATÉGIQUE
# ============================================================================

def calculer_kpis_generaux(df: pd.DataFrame) -> dict:
    """
    Calcule les indicateurs clés (KPIs) globaux pour les cartes de tête.

    Args:
        df (pd.DataFrame): données nettoyées.

    Returns:
        dict: dictionnaire des KPIs prêts à afficher.
    """
    try:
        return {
            "nb_groupes": df["groupe"].nunique(),
            "nb_modules": df["module"].nunique(),
            "nb_formateurs": df["formateur"].nunique(),
            "mh_totale_globale": df["mh_totale"].sum(),
            "mh_realisee_globale": df["mh_realisee"].sum(),
            "taux_realisation_moyen": round(df["taux_realisation"].mean(), 1) if len(df) else 0,
            "taux_absence_moyen": round(df["taux_absence"].mean(), 1) if len(df) else 0,
            "nb_modules_critiques": int((df["statut"] == "🔴 Critique").sum()),
            "indice_performance_global": round(df["indice_performance"].mean(), 1) if len(df) else 0,
        }
    except Exception as e:
        st.error(f"Erreur lors du calcul des KPIs : {e}")
        return {k: 0 for k in [
            "nb_groupes", "nb_modules", "nb_formateurs", "mh_totale_globale",
            "mh_realisee_globale", "taux_realisation_moyen", "taux_absence_moyen",
            "nb_modules_critiques", "indice_performance_global"
        ]}


def generer_alertes(df: pd.DataFrame, seuil_critique: float = 60.0) -> pd.DataFrame:
    """
    Génère la liste des alertes pédagogiques (modules/groupes en retard).

    Args:
        df (pd.DataFrame): données nettoyées.
        seuil_critique (float): seuil en % sous lequel un module est jugé critique.

    Returns:
        pd.DataFrame: sous-ensemble trié des lignes à risque.
    """
    try:
        df_alertes = df[df["taux_realisation"] < seuil_critique].copy()
        df_alertes = df_alertes.sort_values("taux_realisation", ascending=True)
        return df_alertes[[
            "groupe", "module", "formateur", "mh_totale",
            "mh_realisee", "ecart_heures", "taux_realisation", "statut"
        ]]
    except Exception as e:
        st.error(f"Erreur lors de la génération des alertes : {e}")
        return pd.DataFrame()


def classement_performance(df: pd.DataFrame, par: str = "formateur") -> pd.DataFrame:
    """
    Construit un classement de performance agrégé par formateur ou par groupe.

    Args:
        df (pd.DataFrame): données nettoyées.
        par (str): colonne d'agrégation ('formateur' ou 'groupe').

    Returns:
        pd.DataFrame: classement trié par indice de performance décroissant.
    """
    try:
        agg = df.groupby(par).agg(
            indice_performance=("indice_performance", "mean"),
            taux_realisation=("taux_realisation", "mean"),
            taux_absence=("taux_absence", "mean"),
            mh_totale=("mh_totale", "sum"),
            mh_realisee=("mh_realisee", "sum"),
            nb_modules=("module", "nunique"),
        ).reset_index()
        agg = agg.round(1).sort_values("indice_performance", ascending=False)
        return agg
    except Exception as e:
        st.error(f"Erreur lors du classement de performance : {e}")
        return pd.DataFrame()


# ============================================================================
# 5. FONCTIONS D'AFFICHAGE (UI COMPONENTS)
# ============================================================================

def afficher_cartes_kpis(kpis: dict) -> None:
    """Affiche la rangée de cartes de performance (metrics) en haut du dashboard."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Groupes actifs", kpis["nb_groupes"])
    col2.metric("📚 Modules suivis", kpis["nb_modules"])
    col3.metric("🧑‍🏫 Formateurs", kpis["nb_formateurs"])
    col4.metric(
        "🚨 Modules critiques",
        kpis["nb_modules_critiques"],
        delta=None,
        delta_color="inverse"
    )

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("⏱️ Heures planifiées", f"{kpis['mh_totale_globale']:.0f} h")
    col6.metric("✅ Heures réalisées", f"{kpis['mh_realisee_globale']:.0f} h")
    col7.metric(
        "📈 Taux de réalisation moyen",
        f"{kpis['taux_realisation_moyen']}%",
        delta=f"{kpis['taux_realisation_moyen'] - 85:.1f} pts vs cible 85%"
    )
    col8.metric("🏆 Indice de performance global", f"{kpis['indice_performance_global']}/100")


def afficher_alertes(df_alertes: pd.DataFrame) -> None:
    """Affiche les alertes intelligentes sous forme de blocs colorés."""
    if df_alertes.empty:
        st.markdown(
            '<div class="alert-box-success">✅ Aucun module en situation critique. '
            'Le rythme pédagogique global est sous contrôle.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(
        f'<div class="alert-box-danger">🚨 <b>{len(df_alertes)} module(s)</b> '
        f'en retard critique (taux de réalisation &lt; 60%). Action corrective recommandée.</div>',
        unsafe_allow_html=True
    )

    for _, ligne in df_alertes.head(8).iterrows():
        try:
            st.markdown(
                f'<div class="alert-box-danger">'
                f'🔴 <b>{ligne["module"]}</b> — Groupe {ligne["groupe"]} '
                f'(Formateur : {ligne["formateur"]}) → '
                f'Réalisé : <b>{ligne["taux_realisation"]}%</b> | '
                f'Écart : <b>{ligne["ecart_heures"]:.0f} h</b> non rattrapées'
                f'</div>',
                unsafe_allow_html=True
            )
        except Exception:
            continue


def afficher_graphique_gap_analysis(df: pd.DataFrame) -> None:
    """Affiche un graphique en barres comparant heures planifiées vs réalisées par module."""
    try:
        df_gap = df.groupby("module").agg(
            mh_totale=("mh_totale", "sum"),
            mh_realisee=("mh_realisee", "sum"),
        ).reset_index().sort_values("mh_totale", ascending=False).head(15)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_gap["module"], y=df_gap["mh_totale"],
            name="Heures planifiées (MH Totale)",
            marker_color="#4361ee"
        ))
        fig.add_trace(go.Bar(
            x=df_gap["module"], y=df_gap["mh_realisee"],
            name="Heures réalisées",
            marker_color="#2ec4b6"
        ))
        fig.update_layout(
            barmode="group",
            title="Analyse des écarts pédagogiques (Gap Analysis) par module",
            xaxis_title="Module", yaxis_title="Heures",
            template="plotly_dark",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Impossible de générer le graphique Gap Analysis : {e}")


def afficher_graphique_taux_par_groupe(df: pd.DataFrame) -> None:
    """Affiche un graphique du taux de réalisation moyen par groupe, coloré selon le statut."""
    try:
        df_groupe = df.groupby("groupe").agg(
            taux_realisation=("taux_realisation", "mean")
        ).reset_index().round(1).sort_values("taux_realisation")

        def couleur_taux(t):
            if t >= 85:
                return "#28a745"
            elif t >= 60:
                return "#ffc107"
            return "#dc3545"

        couleurs = [couleur_taux(t) for t in df_groupe["taux_realisation"]]

        fig = go.Figure(go.Bar(
            x=df_groupe["taux_realisation"],
            y=df_groupe["groupe"],
            orientation="h",
            marker_color=couleurs,
            text=df_groupe["taux_realisation"].astype(str) + "%",
            textposition="outside"
        ))
        fig.add_vline(x=85, line_dash="dash", line_color="white", opacity=0.4,
                       annotation_text="Cible 85%")
        fig.update_layout(
            title="Taux de réalisation moyen par groupe",
            xaxis_title="Taux de réalisation (%)", yaxis_title="Groupe",
            template="plotly_dark", height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Impossible de générer le graphique par groupe : {e}")


def afficher_graphique_radar_formateurs(df_classement: pd.DataFrame) -> None:
    """Affiche un radar chart comparant les meilleurs formateurs sur plusieurs axes."""
    try:
        top5 = df_classement.head(5)
        if top5.empty:
            st.info("Pas assez de données pour générer le radar des formateurs.")
            return

        fig = go.Figure()
        for _, row in top5.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row["indice_performance"], row["taux_realisation"], 100 - row["taux_absence"]],
                theta=["Indice Performance", "Taux Réalisation", "Taux Présence"],
                fill="toself",
                name=str(row["formateur"])
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            template="plotly_dark",
            title="Comparatif multi-critères — Top 5 formateurs",
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Impossible de générer le radar des formateurs : {e}")


def afficher_distribution_statuts(df: pd.DataFrame) -> None:
    """Affiche un donut chart de répartition des modules par statut pédagogique."""
    try:
        repartition = df["statut"].value_counts().reset_index()
        repartition.columns = ["statut", "nombre"]

        couleurs_map = {
            "✅ Conforme": "#28a745",
            "⚠️ À surveiller": "#ffc107",
            "🔴 Critique": "#dc3545",
        }
        fig = px.pie(
            repartition, names="statut", values="nombre", hole=0.55,
            color="statut", color_discrete_map=couleurs_map,
            title="Répartition des modules par statut pédagogique"
        )
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Impossible de générer la répartition des statuts : {e}")


# ============================================================================
# 6. DONNÉES DE DÉMONSTRATION (utilisées si aucun fichier n'est uploadé)
# ============================================================================

def generer_donnees_demo() -> pd.DataFrame:
    """Génère un jeu de données fictif réaliste pour la démonstration du dashboard."""
    np.random.seed(42)
    groupes = ["DEV101", "DEV102", "RC201", "ID301", "GE105"]
    modules = ["Algorithmique", "Base de données", "Réseaux", "POO Java",
               "Développement Web", "Gestion de projet", "Anglais technique"]
    formateurs = ["M. El Amrani", "Mme. Bensalem", "M. Tahiri", "Mme. Idrissi", "M. Cherkaoui"]

    lignes = []
    for groupe in groupes:
        for module in np.random.choice(modules, size=4, replace=False):
            mh_totale = np.random.choice([20, 30, 40, 60, 80])
            taux = np.random.uniform(35, 100)
            mh_realisee = round(mh_totale * taux / 100, 1)
            lignes.append({
                "groupe": groupe,
                "module": module,
                "formateur": np.random.choice(formateurs),
                "mh_totale": mh_totale,
                "mh_realisee": mh_realisee,
                "taux_absence": round(np.random.uniform(0, 25), 1),
            })
    return pd.DataFrame(lignes)


# ============================================================================
# 7. APPLICATION PRINCIPALE (MAIN)
# ============================================================================

def main() -> None:
    """Point d'entrée principal de l'application Streamlit."""

    st.title("📊 Tableau de Bord Pédagogique — Centre de Formation")
    st.caption(
        "Pilotage stratégique des groupes, modules et formateurs · "
        "Données issues du système E-note"
    )

    # --- Barre latérale : upload + paramètres ---
    with st.sidebar:
        st.header("⚙️ Paramètres")
        fichier_upload = st.file_uploader(
            "📁 Importer un fichier E-note (.csv)",
            type=["csv"],
            help="Glissez-déposez l'export CSV depuis E-note (groupes, modules, formateurs, heures)."
        )
        seuil_critique = st.slider(
            "Seuil d'alerte critique (%)", min_value=20, max_value=80, value=60, step=5,
            help="Sous ce seuil de réalisation, un module est considéré en situation critique."
        )
        st.markdown("---")
        st.caption("💡 Aucun fichier ? Le dashboard affiche des données de démonstration.")

    # --- Chargement des données (upload ou démo) avec gestion d'erreurs totale ---
    df = None
    mode_demo = False

    if fichier_upload is not None:
        try:
            contenu = fichier_upload.read()
            df = charger_et_nettoyer_donnees(contenu)
            if df is None or df.empty:
                raise ValueError("Le fichier a été lu mais ne contient aucune donnée exploitable.")
            st.sidebar.success(f"✅ Fichier chargé : {len(df)} lignes analysées.")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur de lecture du fichier : {e}")
            st.error(
                "🚫 Le fichier importé n'a pas pu être traité correctement. "
                "Vérifiez l'encodage ou la structure des colonnes. "
                "Affichage des données de démonstration en attendant."
            )
            df = generer_donnees_demo()
            df = charger_et_nettoyer_donnees(
                df.to_csv(index=False).encode("utf-8")
            )
            mode_demo = True
    else:
        df_demo_brut = generer_donnees_demo()
        df = charger_et_nettoyer_donnees(df_demo_brut.to_csv(index=False).encode("utf-8"))
        mode_demo = True

    if mode_demo:
        st.info("ℹ️ Mode démonstration actif — importez votre fichier E-note dans le menu latéral pour analyser vos données réelles.")

    # --- Filtres dynamiques ---
    with st.sidebar:
        st.markdown("### 🔍 Filtres")
        try:
            groupes_dispo = ["Tous"] + sorted(df["groupe"].unique().tolist())
            formateurs_dispo = ["Tous"] + sorted(df["formateur"].unique().tolist())
            groupe_sel = st.selectbox("Groupe", groupes_dispo)
            formateur_sel = st.selectbox("Formateur", formateurs_dispo)
        except Exception:
            groupe_sel, formateur_sel = "Tous", "Tous"

    df_filtre = df.copy()
    try:
        if groupe_sel != "Tous":
            df_filtre = df_filtre[df_filtre["groupe"] == groupe_sel]
        if formateur_sel != "Tous":
            df_filtre = df_filtre[df_filtre["formateur"] == formateur_sel]
    except Exception as e:
        st.warning(f"⚠️ Erreur d'application des filtres : {e}")

    if df_filtre.empty:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        return

    # --- 1. Cartes KPI ---
    st.markdown('<p class="section-title">📌 Indicateurs Clés de Performance</p>', unsafe_allow_html=True)
    kpis = calculer_kpis_generaux(df_filtre)
    afficher_cartes_kpis(kpis)

    # --- 2. Alertes intelligentes ---
    st.markdown('<p class="section-title">🚨 Alertes Pédagogiques Intelligentes</p>', unsafe_allow_html=True)
    df_alertes = generer_alertes(df_filtre, seuil_critique=seuil_critique)
    afficher_alertes(df_alertes)

    # --- 3. Graphiques d'analyse ---
    st.markdown('<p class="section-title">📈 Analyse des Écarts (Gap Analysis)</p>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        afficher_graphique_gap_analysis(df_filtre)
    with col_g2:
        afficher_graphique_taux_par_groupe(df_filtre)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        afficher_distribution_statuts(df_filtre)
    with col_g4:
        df_classement_formateurs = classement_performance(df_filtre, par="formateur")
        afficher_graphique_radar_formateurs(df_classement_formateurs)

    # --- 4. Classements détaillés ---
    st.markdown('<p class="section-title">🏆 Classement de Performance</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🧑‍🏫 Par Formateur", "👥 Par Groupe"])

    with tab1:
        try:
            df_form = classement_performance(df_filtre, par="formateur")
            st.dataframe(
                df_form.style.background_gradient(subset=["indice_performance"], cmap="RdYlGn"),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erreur d'affichage du classement formateurs : {e}")

    with tab2:
        try:
            df_grp = classement_performance(df_filtre, par="groupe")
            st.dataframe(
                df_grp.style.background_gradient(subset=["indice_performance"], cmap="RdYlGn"),
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erreur d'affichage du classement groupes : {e}")

    # --- 5. Données détaillées ---
    with st.expander("📋 Voir les données détaillées et nettoyées"):
        st.dataframe(df_filtre, use_container_width=True)
        try:
            csv_export = df_filtre.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ Télécharger les données nettoyées (CSV)",
                data=csv_export,
                file_name=f"export_nettoye_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.warning(f"Export impossible : {e}")

    st.markdown("---")
    st.caption("Dashboard généré automatiquement · Dernière analyse : " +
               datetime.now().strftime("%d/%m/%Y à %H:%M"))


# ============================================================================
# 8. POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as erreur_globale:
        st.error(
            f"🚫 Une erreur inattendue est survenue dans l'application : {erreur_globale}"
        )
        st.info("Veuillez rafraîchir la page ou vérifier le fichier importé.")
