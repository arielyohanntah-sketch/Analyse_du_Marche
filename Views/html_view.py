"""Vue HTML : génère un rapport autonome, sans dépendance externe.

Le fichier produit peut être ouvert directement dans un navigateur ou
imprimé en PDF. Tout le CSS est inclus dans la page.
"""

from __future__ import annotations

import html
from pathlib import Path

from Models.Analyse import ResultatAnalyse

NOMS_COURTS = {
    "Marché Lagune": "Marché",
    "Baobab Shop": "Baobab",
    "Comptoir Ivoire": "Comptoir",
}


def _esc(texte: object) -> str:
    return html.escape(str(texte))


def _fcfa(montant: int | float | None) -> str:
    if montant is None:
        return "-"
    return f"{montant:,.0f}".replace(",", " ") + " FCFA"


def _pct(valeur: float | None) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:.1f}".replace(".", ",") + " %"


def _duree(secondes: float | None) -> str:
    if secondes is None:
        return "-"
    if secondes < 0.001:
        return f"{secondes * 1_000_000:.0f} µs"
    if secondes < 1:
        return f"{secondes * 1000:.2f} ms"
    return f"{secondes:.2f} s"


def _badge(gravite: str) -> str:
    classe = {
        "INFO": "info",
        "AVERTISSEMENT": "warn",
        "ERREUR": "error",
    }.get(gravite, "info")
    return f'<span class="badge {classe}">{_esc(gravite)}</span>'


def _table(entetes: list[str], lignes: list[list[str]],
           classes: str = "") -> str:
    head = "".join(f"<th>{_esc(e)}</th>" for e in entetes)
    body = "".join(
        "<tr>" + "".join(f"<td>{cellule}</td>" for cellule in ligne) + "</tr>"
        for ligne in lignes
    )
    return (
        f'<div class="table-wrap"><table class="{classes}">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody>"
        f"</table></div>"
    )


CSS = """
:root {
  --bg: #f5f7f8;
  --card: #ffffff;
  --ink: #17202a;
  --muted: #5b6770;
  --accent: #0f766e;
  --accent-dark: #115e59;
  --amber: #b45309;
  --danger: #b91c1c;
  --line: #e3e8eb;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.55;
}
header {
  background: linear-gradient(135deg, #0f766e 0%, #115e59 60%, #134e4a 100%);
  color: #fff;
  padding: 46px 24px 40px;
}
.wrap { max-width: 1180px; margin: 0 auto; }
header h1 { margin: 0 0 8px; font-size: clamp(1.7rem, 3vw, 2.6rem); letter-spacing: -0.02em; }
header p { margin: 0; color: #d1fae5; max-width: 780px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; margin-top: 26px; }
.card { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); border-radius: 14px; padding: 16px; }
.card .big { display: block; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.03em; }
.card .label { color: #ccfbf1; font-size: .86rem; }
nav { background: #fff; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 5; }
nav .wrap { display: flex; gap: 18px; overflow-x: auto; padding: 12px 24px; }
nav a { color: var(--muted); text-decoration: none; font-size: .9rem; white-space: nowrap; }
nav a:hover { color: var(--accent); }
main { padding: 30px 24px 50px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 24px; margin: 0 0 22px; box-shadow: 0 1px 2px rgba(16,24,40,.03); }
h2 { margin: 0 0 6px; font-size: 1.3rem; letter-spacing: -0.01em; }
.lead { color: var(--muted); margin: 0 0 18px; }
h3 { margin: 22px 0 10px; font-size: 1rem; }
.table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; }
table { width: 100%; border-collapse: collapse; font-size: .88rem; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--line); vertical-align: top; }
th { background: #eef4f4; color: #234; font-weight: 600; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:nth-child(even) { background: #fbfcfc; }
tbody tr:hover { background: #f0fdfa; }
tr.alert td { background: #fff7ed; }
tr.alert:hover td { background: #ffedd5; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: .72rem; font-weight: 700; letter-spacing: .02em; }
.badge.info { background: #e0f2fe; color: #075985; }
.badge.warn { background: #fef3c7; color: #92400e; }
.badge.error { background: #fee2e2; color: #991b1b; }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }
.panel { background: #f8fafb; border: 1px solid var(--line); border-radius: 12px; padding: 16px; }
.panel h3 { margin-top: 0; }
.bar-row { display: grid; grid-template-columns: 130px 1fr 48px; gap: 10px; align-items: center; margin: 8px 0; font-size: .9rem; }
.bar-track { background: #e5e7eb; border-radius: 999px; height: 12px; overflow: hidden; }
.bar-fill { background: linear-gradient(90deg, #0f766e, #14b8a6); height: 100%; border-radius: 999px; }
.bar-fill.alt { background: linear-gradient(90deg, #b45309, #f59e0b); }
.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.money { font-variant-numeric: tabular-nums; white-space: nowrap; }
.note { color: var(--muted); font-size: .86rem; margin-top: 10px; }
.callout { border-left: 4px solid var(--accent); background: #f0fdfa; padding: 12px 14px; border-radius: 0 10px 10px 0; margin: 14px 0; }
.callout.warn { border-left-color: var(--amber); background: #fffbeb; }
.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.step { background: #f8fafb; border: 1px solid var(--line); border-radius: 12px; padding: 14px; }
.step .n { display: inline-flex; width: 26px; height: 26px; align-items: center; justify-content: center; border-radius: 50%; background: var(--accent); color: #fff; font-weight: 700; font-size: .8rem; margin-bottom: 8px; }
.step strong { display: block; margin-bottom: 4px; }
.step span { color: var(--muted); font-size: .85rem; }
ul.clean { margin: 8px 0; padding-left: 20px; }
ul.clean li { margin: 4px 0; }
footer { color: var(--muted); text-align: center; padding: 0 24px 40px; font-size: .82rem; }
details summary { cursor: pointer; color: var(--accent); font-weight: 600; margin: 10px 0; }
@media (max-width: 700px) {
  section { padding: 18px; }
  .bar-row { grid-template-columns: 100px 1fr 40px; }
}
@media print {
  nav { display: none; }
  body { background: #fff; }
  section { box-shadow: none; break-inside: avoid; }
  header { background: #115e59 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


def generer(resultat: ResultatAnalyse, chemin: str | Path) -> None:
    """Génère le rapport HTML complet."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    synthese = resultat.synthese
    panier = resultat.panier
    historique = resultat.historique

    # --- Cartes de synthèse ---
    nb_offres = len(resultat.offres)
    nb_comparables = synthese.nb_produits_compares
    nb_non_compares = len(synthese.produits_non_compares)
    gagnant = max(synthese.victoires, key=synthese.victoires.get)
    economie_panier = panier.economie or 0

    cartes = f"""
    <div class="cards">
      <div class="card"><span class="big">{nb_comparables}</span><span class="label">produits comparés</span></div>
      <div class="card"><span class="big">{nb_offres}</span><span class="label">offres collectées</span></div>
      <div class="card"><span class="big">{nb_non_compares}</span><span class="label">produits non comparables</span></div>
      <div class="card"><span class="big">{_esc(NOMS_COURTS.get(gagnant, gagnant))}</span><span class="label">plus souvent la moins chère</span></div>
      <div class="card"><span class="big">{_fcfa(economie_panier)}</span><span class="label">économie sur le panier</span></div>
    </div>
    """

    # --- Démarche ---
    demarche = """
    <section id="demarche">
      <h2>La démarche</h2>
      <p class="lead">Cinq étapes, de la donnée brute à la décision d'achat.</p>
      <div class="steps">
        <div class="step"><span class="n">1</span><strong>Collecter</strong><span>CSV, JSON et Excel : trois formats, trois façons d'écrire.</span></div>
        <div class="step"><span class="n">2</span><strong>Normaliser</strong><span>Accents, casse, espaces, unités et synonymes.</span></div>
        <div class="step"><span class="n">3</span><strong>Indexer</strong><span>Un dictionnaire produit → prix par boutique.</span></div>
        <div class="step"><span class="n">4</span><strong>Comparer</strong><span>Minimum, maximum, écart en FCFA et en %.</span></div>
        <div class="step"><span class="n">5</span><strong>Décider</strong><span>Meilleure boutique, alertes, panier optimal.</span></div>
      </div>
    </section>
    """

    # --- Collecte ---
    lignes_collecte = []
    for source in ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]:
        offres_source = [o for o in resultat.offres if o.source == source]
        lignes_collecte.append([
            _esc(source),
            str(len(offres_source)),
            str(sum(1 for o in offres_source if o.disponible)),
            str(sum(1 for o in offres_source if o.produit_id)),
        ])
    collecte = f"""
    <section id="collecte">
      <h2>1. Collecte et rapprochement</h2>
      <p class="lead">Chaque offre est rattachée à un produit_id du catalogue commun.</p>
      {_table(["Boutique", "Offres lues", "Disponibles", "Rapprochées"], lignes_collecte)}
      <p class="note">Une offre est disponible si elle a un prix exploitable et n'est pas en rupture de stock.</p>
    </section>
    """

    # --- Journal ---
    compteur = resultat.journal.compter()
    lignes_journal = []
    for ligne in resultat.journal.lignes:
        lignes_journal.append([
            _badge(ligne.gravite),
            _esc(ligne.etape),
            _esc(ligne.source),
            _esc(ligne.reference),
            _esc(ligne.probleme),
            _esc(ligne.action),
        ])
    journal = f"""
    <section id="journal">
      <h2>2. Journal de nettoyage</h2>
      <p class="lead">{compteur['INFO']} informations, {compteur['AVERTISSEMENT']} avertissements, {compteur['ERREUR']} erreurs.</p>
      <div class="callout">
        Les problèmes sont traités et conservés : rien n'est corrigé en silence.
      </div>
      <details>
        <summary>Voir les {len(resultat.journal.lignes)} lignes du journal</summary>
        {_table(["Niveau", "Étape", "Source", "Référence", "Problème", "Action"], lignes_journal)}
      </details>
    </section>
    """

    # --- Comparatif ---
    lignes_comparatif = []
    for ligne in resultat.comparaisons:
        meilleure = " + ".join(
            NOMS_COURTS.get(source, source) for source in ligne.sources_min
        )
        lignes_comparatif.append([
            _esc(ligne.produit.produit_id),
            _esc(ligne.produit.nom),
            _esc(meilleure),
            f'<span class="money">{_fcfa(ligne.prix_min)}</span>',
            f'<span class="money">{_fcfa(ligne.prix_max)}</span>',
            f'<span class="money">{_fcfa(ligne.ecart_fcfa)}</span>',
            f'<span class="num">{_pct(ligne.ecart_pct)}</span>',
            '<span class="badge warn">à surveiller</span>' if ligne.ecart_pct >= 10 else '<span class="badge info">normal</span>',
        ])
    # Les lignes en alerte doivent avoir la classe sur le <tr>. On régénère
    # le tableau à la main pour appliquer cette classe.
    entetes_comparatif = ["ID", "Produit", "Meilleure", "Prix min", "Prix max",
                          "Écart FCFA", "Écart %", "Statut"]
    corps = []
    for ligne, cellules in zip(resultat.comparaisons, lignes_comparatif):
        classe = ' class="alert"' if ligne.ecart_pct >= 10 else ""
        corps.append(
            f"<tr{classe}>" + "".join(f"<td>{c}</td>" for c in cellules) + "</tr>"
        )
    comparatif = f"""
    <section id="comparatif">
      <h2>3. Comparatif des prix</h2>
      <p class="lead">Trié par écart décroissant : les décisions les plus intéressantes d'abord.</p>
      <div class="table-wrap"><table>
        <thead><tr>{''.join(f'<th>{_esc(e)}</th>' for e in entetes_comparatif)}</tr></thead>
        <tbody>{''.join(corps)}</tbody>
      </table></div>
      <p class="note">Écart = prix le plus élevé − prix le plus bas : c'est la marge réalisée en évitant la boutique la plus chère. Le pourcentage est calculé par rapport au prix le plus bas.</p>
    </section>
    """

    # --- Synthèse ---
    max_victoires = max(synthese.victoires.values()) or 1
    barres = []
    for source in sorted(synthese.victoires, key=lambda s: synthese.victoires[s], reverse=True):
        valeur = synthese.victoires[source]
        largeur = valeur / max_victoires * 100
        barres.append(
            f'<div class="bar-row"><span>{_esc(source)}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{largeur:.0f}%"></div></div>'
            f'<span class="num">{valeur}</span></div>'
        )

    lignes_surcout = [
        [_esc(source), f'<span class="num">{_pct(valeur)}</span>']
        for source, valeur in sorted(
            synthese.surcout_moyen_pct.items(), key=lambda item: item[1]
        )
    ]

    top_gains = "".join(
        f"<li><strong>{_esc(l.produit.produit_id)} — {_esc(l.produit.nom)}</strong> : "
        f"{_fcfa(l.ecart_fcfa)} d'écart ({_pct(l.ecart_pct)})</li>"
        for l in synthese.top_gains_fcfa
    )
    top_pct = "".join(
        f"<li><strong>{_esc(l.produit.produit_id)} — {_esc(l.produit.nom)}</strong> : "
        f"{_pct(l.ecart_pct)} ({_fcfa(l.ecart_fcfa)})</li>"
        for l in synthese.top_ecarts_pct
    )

    lignes_non_compares = [
        [
            _esc(n.produit.produit_id),
            _esc(n.produit.nom),
            _esc(n.raison),
            _esc(", ".join(NOMS_COURTS.get(s, s) for s in n.sources_disponibles) or "-"),
        ]
        for n in synthese.produits_non_compares
    ]

    synthese_html = f"""
    <section id="synthese">
      <h2>4. Synthèse et décision</h2>
      <p class="lead">Qui gagne le plus souvent, et où se trouvent les plus gros écarts ?</p>
      <div class="grid2">
        <div class="panel">
          <h3>Victoires (égalités comprises)</h3>
          {''.join(barres)}
          <p class="note">{synthese.nb_egalites} égalité(s) entre boutiques.</p>
        </div>
        <div class="panel">
          <h3>Écart moyen vs prix le plus bas</h3>
          {_table(["Boutique", "Surcoût moyen"], lignes_surcout)}
          <p class="note">Plus le pourcentage est bas, plus la boutique est compétitive en moyenne.</p>
        </div>
      </div>
      <div class="grid2">
        <div class="panel">
          <h3>Top 3 des économies absolues</h3>
          <ul class="clean">{top_gains}</ul>
        </div>
        <div class="panel">
          <h3>Top 3 des écarts relatifs</h3>
          <ul class="clean">{top_pct}</ul>
        </div>
      </div>
      <h3>Produits non comparés</h3>
      {_table(["ID", "Produit", "Raison", "Boutiques disponibles"], lignes_non_compares)}
    </section>
    """

    # --- Panier ---
    lignes_totaux = []
    for total in panier.totaux:
        if total.complet:
            lignes_totaux.append([
                _esc(total.source),
                f'<span class="money">{_fcfa(total.total)}</span>',
                '<span class="badge info">complet</span>',
            ])
        else:
            lignes_totaux.append([
                _esc(total.source),
                '<span class="badge warn">incomplet</span>',
                _esc(", ".join(total.manquants)),
            ])

    lignes_optimales = []
    for ligne in panier.lignes:
        lignes_optimales.append([
            _esc(ligne.produit_id),
            _esc(ligne.nom),
            str(ligne.quantite),
            _esc(NOMS_COURTS.get(ligne.source or "", ligne.source or "-")),
            f'<span class="money">{_fcfa(ligne.prix_unitaire)}</span>',
            f'<span class="money">{_fcfa(ligne.total)}</span>',
        ])

    panier_html = f"""
    <section id="panier">
      <h2>5. Panier de rentrée</h2>
      <p class="lead">1 Tecno Spark 20, 1 Lenovo IdeaPad 3, 2 clés USB, 1 disque dur, 1 micro-ondes.</p>
      <div class="grid2">
        <div class="panel">
          <h3>Coût si tout est acheté dans une seule boutique</h3>
          {_table(["Boutique", "Total", "Statut"], lignes_totaux)}
        </div>
        <div class="panel">
          <h3>Décision</h3>
          <p><strong>Meilleure combinaison :</strong> {_fcfa(panier.total_optimal)}</p>
          <p><strong>Meilleure boutique unique :</strong> {_esc(panier.source_unique_moins_chere or "-")} ({_fcfa(panier.total_source_unique)})</p>
          <p><strong>Économie :</strong> {_fcfa(panier.economie)}</p>
          <div class="callout">Acheter chaque article là où il est le moins cher est optimal ici, car les articles sont indépendants.</div>
        </div>
      </div>
      <h3>Détail de la combinaison optimale</h3>
      {_table(["ID", "Produit", "Qté", "Boutique", "Prix unitaire", "Total"], lignes_optimales)}
    </section>
    """

    # --- Historique ---
    lignes_historique = []
    for stats in historique.stats:
        variation_classe = "info" if stats.variation_pct < 0 else "warn"
        lignes_historique.append([
            _esc(stats.source),
            f'<span class="money">{_fcfa(stats.moyenne_annuelle)}</span>',
            f'<span class="money">{_fcfa(stats.moyenne_black_friday)}</span>',
            f'<span class="badge {variation_classe}">{_pct(stats.variation_pct)}</span>',
            _esc(stats.meilleur_mois),
            f'<span class="money">{_fcfa(stats.moyenne_meilleur_mois)}</span>',
        ])
    conclusions = []
    for stats in historique.stats:
        if stats.variation_pct < 0:
            conclusions.append(
                f"<li><strong>{_esc(stats.source)}</strong> : le Black Friday était "
                f"moins cher de {_pct(abs(stats.variation_pct))}.</li>"
            )
        else:
            conclusions.append(
                f"<li><strong>{_esc(stats.source)}</strong> : le Black Friday était "
                f"plus cher de {_pct(stats.variation_pct)} ; le meilleur mois "
                f"était {_esc(stats.meilleur_mois)}.</li>"
            )
    historique_html = f"""
    <section id="historique">
      <h2>6. Historique : quand fallait-il acheter ?</h2>
      <p class="lead">Période {_esc(historique.debut)} → {_esc(historique.fin)} · {historique.nb_lignes} relevés.</p>
      {_table(["Boutique", "Moyenne annuelle", "Black Friday", "Variation", "Meilleur mois", "Prix moyen"], lignes_historique)}
      <div class="callout"><ul class="clean">{''.join(conclusions)}</ul></div>
      <p class="note">Pour Comptoir Ivoire, l'historique contient le prix catalogue, sans la remise.</p>
    </section>
    """

    # --- Complexité ---
    benchmark_html = ""
    if resultat.benchmark is not None:
        blocs = []
        for titre, mesures in [
            ("Recherche dans l'historique", resultat.benchmark.historique),
            ("Recherche dans un catalogue", resultat.benchmark.correspondance),
        ]:
            if not mesures:
                continue
            lignes = []
            for mesure in mesures:
                acceleration = (
                    mesure.temps_naif / mesure.temps_index
                    if mesure.temps_index > 0 else 0
                )
                lignes.append([
                    _esc(mesure.libelle),
                    f"{_esc(mesure.complexite_naive)}<br><span class='money'>{_duree(mesure.temps_naif)}</span>",
                    f"{_esc(mesure.complexite_index)}<br><span class='money'>{_duree(mesure.temps_index)}</span>",
                    f'<span class="badge info">×{acceleration:.0f}</span>',
                ])
            blocs.append(
                f"<h3>{_esc(titre)}</h3>"
                + _table(["Opération", "Version naïve", "Version indexée", "Gain"], lignes)
            )
        benchmark_html = f"""
        <section id="complexite">
          <h2>7. Complexité : le temps mesuré</h2>
          <p class="lead">Même opération, deux structures de données.</p>
          {''.join(blocs)}
          <p class="note">Mesures refaites à chaque exécution sur la machine qui produit le rapport.</p>
        </section>
        """

    # --- Temps par étape ---
    lignes_temps = [
        [_esc(etape), f'<span class="money">{_duree(temps)}</span>']
        for etape, temps in resultat.temps.items()
    ]
    temps_html = f"""
    <section id="temps">
      <h2>8. Temps d'exécution par étape</h2>
      {_table(["Étape", "Temps"], lignes_temps)}
    </section>
    """

    # --- Choix techniques ---
    choix = """
    <section id="choix">
      <h2>Choix techniques</h2>
      <div class="grid2">
        <div class="panel">
          <h3>Nettoyage</h3>
          <ul class="clean">
            <li>Accents, casse, espaces multiples et guillemets normalisés.</li>
            <li>Unités unifiées : Go → GB, To → TB, CV → HP, 1,5 L → 1.5L.</li>
            <li>Synonymes : frigo/fridge/réfrigérateur, clim/air conditioner, blender/mixeur.</li>
            <li>Prix texte converti en entier FCFA.</li>
            <li>Doublons supprimés, ruptures et prix absents écartés.</li>
            <li>Prix incohérent avec l'ancien prix signalé et écarté.</li>
          </ul>
        </div>
        <div class="panel">
          <h3>Rapprochement</h3>
          <ul class="clean">
            <li>Signature : mots, marque, capacité et modèle.</li>
            <li>Index inversé mot → produits candidats.</li>
            <li>Règles : marque, capacité et modèle incompatibles = rejet.</li>
            <li>Score de recouvrement des mots, avec bonus de marque.</li>
            <li>Les correspondances faibles sont signalées dans le journal.</li>
          </ul>
        </div>
      </div>
    </section>
    """

    html_page = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Analyse comparative de marché</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>Analyse comparative de marché</h1>
    <p>Trois boutiques en ligne, un même catalogue, des prix différents.
    Le programme collecte, normalise, rapproche, compare et décide où acheter.</p>
    {cartes}
  </div>
</header>
<nav><div class="wrap">
  <a href="#demarche">Démarche</a>
  <a href="#collecte">Collecte</a>
  <a href="#journal">Journal</a>
  <a href="#comparatif">Comparatif</a>
  <a href="#synthese">Synthèse</a>
  <a href="#panier">Panier</a>
  <a href="#historique">Historique</a>
  <a href="#complexite">Complexité</a>
  <a href="#choix">Choix techniques</a>
</div></nav>
<main class="wrap">
  {demarche}
  {collecte}
  {journal}
  {comparatif}
  {synthese_html}
  {panier_html}
  {historique_html}
  {benchmark_html}
  {temps_html}
  {choix}
</main>
<footer>
  Rapport généré automatiquement par le projet Analyse comparative de marché.
  Données fictives de l'exercice — DA Python, L2 Computer Science.
</footer>
</body>
</html>
"""
    chemin.write_text(html_page, encoding="utf-8")
