# Rôle : Lit les fichiers des 3 boutiques (CSV, JSON, Excel) et l'historique des prix.
# Emplacement MVC : MODÈLE (Collecte des données)

import csv
import json
import os
import openpyxl
from models.nettoyage_donnees import nettoyer_prix, trouver_produit_id
from models.journal_erreurs import JournalErreurs


def charger_catalogue_reference(chemin_csv):
    """Charge le catalogue de référence commun (P01 à P30)."""
    catalogue = {}
    with open(chemin_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            pid = ligne["produit_id"].strip()
            catalogue[pid] = {
                "produit_id": pid,
                "nom": ligne["nom"].strip(),
                "categorie": ligne["categorie"].strip(),
                "marque": ligne["marque"].strip()
            }
    return catalogue


def charger_donnees_boutiques(chemin_ml, chemin_bb, chemin_ci, catalogue_ref, journal):
    """Charge les données des 3 boutiques dans une structure unique indexée par produit_id."""
    donnees = {}
    for pid, info in catalogue_ref.items():
        donnees[pid] = {
            "produit_id": pid,
            "nom_ref": info["nom"],
            "categorie": info["categorie"],
            "marque": info["marque"],
            "offres": {}
        }

    # 1. Marché Lagune (CSV avec ;)
    _charger_marche_lagune(chemin_ml, donnees, journal)

    # 2. Baobab Shop (JSON)
    _charger_baobab_shop(chemin_bb, donnees, journal)

    # 3. Comptoir Ivoire (Excel)
    _charger_comptoir_ivoire(chemin_ci, donnees, journal)

    return donnees


def _charger_marche_lagune(chemin_csv, donnees, journal):
    """Lit et nettoie le catalogue Marché Lagune."""
    if not os.path.exists(chemin_csv):
        return

    vus = set()
    with open(chemin_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for ligne in reader:
            ref = ligne.get("reference", "").strip()
            nom = ligne.get("designation", "").strip()
            dispo = ligne.get("disponibilite", "").strip()

            # Vérifie les doublons
            if ref in vus:
                journal.ajouter("Marché Lagune", ref, "Doublon", f"Article {nom} en double.", "Ligne doublon ignorée.")
                continue
            vus.add(ref)

            pid = trouver_produit_id(nom, ref)
            if not pid or pid not in donnees:
                journal.ajouter("Marché Lagune", ref, "Non reconnu", f"Produit '{nom}' non trouvé.", "Exclu.")
                continue

            prix = nettoyer_prix(ligne.get("prix", ""))
            if prix is None:
                journal.ajouter("Marché Lagune", ref, "Prix invalide", f"Valeur : '{ligne.get('prix')}'.", "Prix ignoré.")

            # Détecte le prix anormal sur le P04 (779 000 F)
            if pid == "P04" and prix and prix > 500000:
                journal.ajouter("Marché Lagune", ref, "Prix aberrant", f"Prix de {prix:,.0f} F anormalement élevé.", "Signalé.")

            en_stock = (dispo in ["En stock", "Stock limité"])
            if not en_stock:
                journal.ajouter("Marché Lagune", ref, "Rupture", f"Statut '{dispo}' pour '{nom}'.", "Non retenu pour le moins cher.")

            donnees[pid]["offres"]["Marché Lagune"] = {
                "prix": prix,
                "en_stock": en_stock,
                "detail": dispo,
                "ref": ref
            }


def _charger_baobab_shop(chemin_json, donnees, journal):
    """Lit et nettoie le catalogue Baobab Shop."""
    if not os.path.exists(chemin_json):
        return

    with open(chemin_json, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data.get("items", []):
        sku = item.get("sku", "").strip()
        titre = item.get("title", "").strip()
        pricing = item.get("pricing", {})
        amount = pricing.get("amount")
        frais = pricing.get("delivery_fee", 0) or 0
        stock = item.get("stock", 0)

        pid = trouver_produit_id(titre, sku)
        if not pid or pid not in donnees:
            journal.ajouter("Baobab Shop", sku, "Non reconnu", f"Produit '{titre}' non trouvé.", "Exclu.")
            continue

        if amount is None:
            journal.ajouter("Baobab Shop", sku, "Prix manquant", f"Montant vide pour '{titre}'.", "Prix non exploitable.")
            prix_total = None
        else:
            prix_total = float(amount) + float(frais)

        en_stock = (stock > 0)
        if not en_stock:
            journal.ajouter("Baobab Shop", sku, "Rupture", f"Stock à 0 pour '{titre}'.", "Non retenu pour le moins cher.")

        donnees[pid]["offres"]["Baobab Shop"] = {
            "prix": prix_total,
            "en_stock": en_stock,
            "detail": f"Stock: {stock}, Frais: {frais} F",
            "ref": sku
        }


def _charger_comptoir_ivoire(chemin_xlsx, donnees, journal):
    """Lit et nettoie le catalogue Comptoir Ivoire (classeur Excel)."""
    if not os.path.exists(chemin_xlsx):
        return

    wb = openpyxl.load_workbook(chemin_xlsx, data_only=True)
    ws = wb["Tarifs octobre 2026"]

    for row in ws.iter_rows(values_only=True):
        code = row[0]
        if not code or not str(code).startswith("CI"):
            continue

        code_str = str(code).strip()
        nom = str(row[1] or "").strip()
        prix_cat = nettoyer_prix(row[3])
        remise = row[4] or 0
        qte = row[5] or 0

        pid = trouver_produit_id(nom, code_str)
        if not pid or pid not in donnees:
            journal.ajouter("Comptoir Ivoire", code_str, "Non reconnu", f"Article '{nom}' non trouvé.", "Exclu.")
            continue

        if prix_cat is None:
            journal.ajouter("Comptoir Ivoire", code_str, "Prix invalide", f"Prix brut : '{row[3]}'.", "Prix ignoré.")
            prix_net = None
        else:
            try:
                remise_pct = float(remise)
            except ValueError:
                remise_pct = 0.0
            prix_net = round(prix_cat * (1.0 - (remise_pct / 100.0)), 2)

        try:
            qte_num = int(qte)
        except ValueError:
            qte_num = 0

        en_stock = (qte_num > 0)
        if not en_stock:
            journal.ajouter("Comptoir Ivoire", code_str, "Rupture", f"Quantité à 0 pour '{nom}'.", "Non retenu pour le moins cher.")

        donnees[pid]["offres"]["Comptoir Ivoire"] = {
            "prix": prix_net,
            "en_stock": en_stock,
            "detail": f"Stock: {qte_num}, Remise: {remise}%",
            "ref": code_str
        }


def charger_historique_prix(chemin_csv):
    """Lit les 20 876 lignes de l'historique en streaming (ligne par ligne) pour économiser la mémoire."""
    stats = {}
    total_lignes = 0

    if not os.path.exists(chemin_csv):
        return 0, stats

    with open(chemin_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_lignes += 1
            src = row["source"].strip()
            date = row["date"].strip()
            prix = float(row["prix_fcfa"])

            if src not in stats:
                stats[src] = {"somme_an": 0.0, "nb_an": 0, "somme_bf": 0.0, "nb_bf": 0}

            s = stats[src]
            s["somme_an"] += prix
            s["nb_an"] += 1

            if "2025-11-24" <= date <= "2025-11-30":
                s["somme_bf"] += prix
                s["nb_bf"] += 1

    return total_lignes, stats
