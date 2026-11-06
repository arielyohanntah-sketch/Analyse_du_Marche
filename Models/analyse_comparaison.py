# Rôle : Compare les prix, trouve le moins cher, calcule le panier et le Black Friday.
# Emplacement MVC : MODÈLE (Logique d'analyse et calculs)

import csv


def comparer_prix(donnees):
    """Compare les offres valides (en stock) et calcule les écarts de prix."""
    rapport = []

    for pid, pdata in donnees.items():
        nom = pdata["nom_ref"]
        categorie = pdata["categorie"]
        offres = pdata["offres"]

        # Ne retient que les offres en stock avec un prix chiffré
        offres_valides = {
            ens: o["prix"]
            for ens, o in offres.items()
            if o.get("en_stock") and o.get("prix") is not None
        }

        # Comparaison possible uniquement si >= 2 boutiques ont l'article
        if len(offres_valides) < 2:
            continue

        meilleure = min(offres_valides, key=offres_valides.get)
        prix_min = offres_valides[meilleure]
        prix_max = max(offres_valides.values())
        ecart_f = round(prix_max - prix_min, 0)
        ecart_pct = round(((prix_max - prix_min) / prix_min) * 100, 1)

        rapport.append({
            "produit_id": pid,
            "nom": nom,
            "categorie": categorie,
            "meilleure": meilleure,
            "prix_min": prix_min,
            "prix_max": prix_max,
            "ecart_fcfa": ecart_f,
            "ecart_pct": ecart_pct,
            "offres_valides": offres_valides,
            "toutes_offres": offres
        })

    # Classement par écart de pourcentage décroissant
    return sorted(rapport, key=lambda r: r["ecart_pct"], reverse=True)


def rechercher_produit(terme, donnees):
    """Recherche un produit par mot-clé (avec synonymes comme 'ordinateur', 'frigo', etc.)."""
    mot = terme.strip().lower()
    
    # Dictionnaire de synonymes courants
    synonymes = {
        "ordinateur": ["hp 250", "lenovo", "dell", "informatique", "laptop", "pc"],
        "pc": ["hp 250", "lenovo", "dell", "informatique"],
        "telephone": ["smartphone", "galaxy", "spark", "camon", "hot 40", "note 40", "iphone"],
        "frigo": ["réfrigérateur", "hisense 205", "refrigerateur"],
        "clim": ["climatiseur", "lg 1 cv", "hisense 1,5"],
        "ventilo": ["ventilateur", "binatone"],
        "fer": ["fer à repasser", "philips"]
    }
    
    mots_cibles = [mot]
    if mot in synonymes:
        mots_cibles.extend(synonymes[mot])

    resultats = []

    for pid, pdata in donnees.items():
        nom = pdata["nom_ref"].lower()
        cat = pdata["categorie"].lower()
        marque = pdata["marque"].lower()
        ident = pid.lower()

        # Vérifie si le mot ou l'un de ses synonymes est présent
        correspond = any(
            c in nom or c in cat or c in marque or c in ident
            for c in mots_cibles
        )

        if correspond:
            offres = pdata["offres"]
            offres_valides = {
                ens: o["prix"]
                for ens, o in offres.items()
                if o.get("en_stock") and o.get("prix") is not None
            }

            meilleure = None
            prix_min = None
            ecart_f = 0
            ecart_pct = 0

            if offres_valides:
                meilleure = min(offres_valides, key=offres_valides.get)
                prix_min = offres_valides[meilleure]
                prix_max = max(offres_valides.values())
                ecart_f = prix_max - prix_min
                ecart_pct = round((ecart_f / prix_min) * 100, 1) if prix_min > 0 else 0

            resultats.append({
                "produit_id": pid,
                "nom": pdata["nom_ref"],
                "categorie": pdata["categorie"],
                "marque": pdata["marque"],
                "offres": offres,
                "meilleure": meilleure,
                "prix_min": prix_min,
                "ecart_fcfa": ecart_f,
                "ecart_pct": ecart_pct
            })

    return resultats


def exporter_tableau_csv(rapport, chemin_csv):
    """Enregistre le tableau comparatif dans un fichier CSV avec séparateur point-virgule."""
    with open(chemin_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "ID", "Produit", "Catégorie",
            "Prix Marché Lagune", "Prix Baobab Shop", "Prix Comptoir Ivoire",
            "Meilleure Enseigne", "Prix Min (FCFA)", "Écart (FCFA)", "Écart (%)"
        ])

        for item in rapport:
            toutes = item["toutes_offres"]

            def format_case(ens):
                o = toutes.get(ens)
                if not o: return "Non référencé"
                if not o.get("en_stock"): return f"{o.get('prix', 'N/A')} (Rupture)"
                return f"{o.get('prix')}"

            writer.writerow([
                item["produit_id"],
                item["nom"],
                item["categorie"],
                format_case("Marché Lagune"),
                format_case("Baobab Shop"),
                format_case("Comptoir Ivoire"),
                item["meilleure"],
                f"{item['prix_min']:.0f}",
                f"{item['ecart_fcfa']:.0f}",
                f"{item['ecart_pct']} %"
            ])


def faire_synthese(rapport):
    """Compte les victoires par enseigne, calcule l'écart moyen et sort le top 3 des gains."""
    victoires = {"Marché Lagune": 0, "Baobab Shop": 0, "Comptoir Ivoire": 0}
    ecarts = {"Marché Lagune": [], "Baobab Shop": [], "Comptoir Ivoire": []}

    for item in rapport:
        gagnant = item["meilleure"]
        victoires[gagnant] = victoires.get(gagnant, 0) + 1

        p_min = item["prix_min"]
        for ens, prix in item["offres_valides"].items():
            ecarts[ens].append(((prix - p_min) / p_min) * 100)

    ecarts_moyens = {
        ens: round(sum(vals) / len(vals), 2) if vals else 0.0
        for ens, vals in ecarts.items()
    }

    top3 = sorted(rapport, key=lambda r: r["ecart_fcfa"], reverse=True)[:3]

    return {
        "total_produits": len(rapport),
        "victoires": victoires,
        "ecarts_moyens": ecarts_moyens,
        "top3_gains": top3
    }


def calculer_panier_rentree(donnees):
    """Calcule le coût du panier de rentrée par boutique et en panachage optimal."""
    panier_articles = {
        "P04": {"nom": "Tecno Spark 20 128 Go", "qte": 1},
        "P12": {"nom": "Lenovo IdeaPad 3 Core i3", "qte": 1},
        "P14": {"nom": "Clé USB SanDisk 64 Go", "qte": 2},
        "P15": {"nom": "Disque dur externe Seagate 1 To", "qte": 1},
        "P28": {"nom": "Micro-ondes Samsung 23 L", "qte": 1}
    }

    enseignes = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]
    couts = {}

    for ens in enseignes:
        total = 0.0
        possible = True
        for pid, spec in panier_articles.items():
            o = donnees.get(pid, {}).get("offres", {}).get(ens)
            if not o or not o.get("en_stock") or o.get("prix") is None:
                possible = False
                break
            total += o["prix"] * spec["qte"]
        couts[ens] = total if possible else None

    cout_opt = 0.0
    details_opt = []
    for pid, spec in panier_articles.items():
        offres = {
            ens: o["prix"]
            for ens, o in donnees.get(pid, {}).get("offres", {}).items()
            if o.get("en_stock") and o.get("prix") is not None
        }
        meilleure = min(offres, key=offres.get)
        prix_unitaire = offres[meilleure]
        prix_ligne = prix_unitaire * spec["qte"]
        cout_opt += prix_ligne
        details_opt.append({
            "nom": spec["nom"],
            "qte": spec["qte"],
            "enseigne": meilleure,
            "prix_unitaire": prix_unitaire,
            "prix_total": prix_ligne
        })

    return {
        "couts_enseignes": couts,
        "cout_optimal": cout_opt,
        "details_optimal": details_opt
    }


def analyser_black_friday(stats_hist):
    """Compare la moyenne annuelle et la semaine du Black Friday (24 au 30 nov 2025)."""
    resultats = []
    for ens, st in stats_hist.items():
        moy_an = st["somme_an"] / st["nb_an"] if st["nb_an"] > 0 else 0.0
        moy_bf = st["somme_bf"] / st["nb_bf"] if st["nb_bf"] > 0 else 0.0
        diff_pct = ((moy_bf - moy_an) / moy_an) * 100 if moy_an > 0 else 0.0

        resultats.append({
            "enseigne": ens,
            "moyenne_annuelle": round(moy_an, 0),
            "moyenne_black_friday": round(moy_bf, 0),
            "difference_pct": round(diff_pct, 2),
            "est_promotion": diff_pct < 0
        })

    return resultats
