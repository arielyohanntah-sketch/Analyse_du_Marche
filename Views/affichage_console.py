# Rôle : Gère tout l'affichage des tableaux, menus interactifs et résultats dans le terminal.
# Emplacement MVC : VUE (Présentation console)


class AffichageConsole:
    """Interface console interactive (menu, recherche, tableaux, synthèse)."""

    @staticmethod
    def formater_prix(montant):
        """Ajoute un espace pour les milliers et le symbole F."""
        if montant is None:
            return "Indisp."
        return f"{int(round(montant)):,}".replace(",", " ") + " F"

    def afficher_menu_principal(self):
        """Affiche le menu de navigation de l'application console."""
        print("\n" + "=" * 65)
        print("          COMPARATEUR DE MARCHÉ - MENU PRINCIPAL")
        print("=" * 65)
        print("  [1] Voir le tableau comparatif des prix (produits en stock)")
        print("  [2] Rechercher un produit (ordinateur, smartphone, etc.)")
        print("  [3] Consulter la synthèse décisionnelle (qui est le moins cher ?)")
        print("  [4] Évaluer le panier de rentrée scolaire (5 articles)")
        print("  [5] Analyser l'historique des prix (Offres Black Friday)")
        print("  [6] Consulter le journal des anomalies détectées")
        print("  [7] Étude de la complexité algorithmique (Big-O)")
        print("  [0] Quitter l'application")
        print("-" * 65)

    def demander_choix(self):
        """Demande à l'utilisateur de saisir son choix."""
        try:
            return input(" -> Entrez votre choix (0-7) : ").strip()
        except (EOFError, KeyboardInterrupt):
            return "0"

    def demander_recherche(self):
        """Demande le mot-clé pour chercher un produit."""
        try:
            return input("\n -> Entrez un mot-clé ou nom de produit (ex: hp, tecno, tv, ecran) : ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    def pause(self):
        """Met en pause l'écran pour laisser l'utilisateur lire."""
        try:
            input("\n [Appuyez sur Entrée pour revenir au menu...]")
        except (EOFError, KeyboardInterrupt):
            pass

    def afficher_resultats_recherche(self, resultats):
        """Affiche les détails précis d'un ou plusieurs produits recherchés."""
        print("\n" + "=" * 80)
        print("                    RÉSULTAT DE LA RECHERCHE PRODUIT")
        print("=" * 80)

        if not resultats:
            print(" Aucun produit correspondant n'a été trouvé.")
            print("-" * 80)
            return

        for p in resultats:
            print(f"\n* [{p['produit_id']}] {p['nom']} ({p['categorie']} - Marque: {p['marque']})")
            print("   Détail des offres par boutique :")
            for ens in ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]:
                o = p["offres"].get(ens)
                if not o:
                    print(f"     - {ens:<16} : Non référencé")
                elif not o.get("en_stock") or o.get("prix") is None:
                    print(f"     - {ens:<16} : En Rupture de stock")
                else:
                    print(f"     - {ens:<16} : {self.formater_prix(o['prix'])} ({o.get('detail', '')})")

            if p["meilleure"]:
                print(f"\n   [RECOMMANDATION D'ACHAT] :")
                print(f"      -> Achetez chez : {p['meilleure']}")
                print(f"      -> Meilleur prix : {self.formater_prix(p['prix_min'])}")
                if p["ecart_fcfa"] > 0:
                    print(f"      -> Vous gagnez {self.formater_prix(p['ecart_fcfa'])} (marge/écart de {p['ecart_pct']} % par rapport au plus cher)")
                else:
                    print(f"      -> Prix identique dans les boutiques en stock.")
            else:
                print("   [ATTENTION] Aucune offre en stock pour ce produit actuellement.")
            print("-" * 80)

    def afficher_journal_anomalies(self, anomalies):
        """Affiche les anomalies détectées dans les catalogues."""
        print("\n" + "=" * 90)
        print("                   JOURNAL DES ANOMALIES DÉTECTÉES ET TRAITÉES")
        print("=" * 90)
        print(f"Total anomalies identifiées : {len(anomalies)}\n")

        for a in anomalies:
            print(f"  [{a['boutique']}] {a['anomalie']} (Réf: {a['reference']})")
            print(f"     Problème : {a['description']}")
            print(f"     Action   : {a['solution']}\n")
        print("-" * 90)

    def afficher_tableau_comparatif(self, rapport):
        """Affiche le grand tableau comparatif trié par écart décroissant."""
        print("\n" + "=" * 95)
        print("         TABLEAU COMPARATIF DES PRIX (PRODUITS DISPONIBLES EN STOCK >= 2 BOUTIQUES)")
        print("=" * 95)

        en_tete = f"{'ID':<4} | {'Produit':<26} | {'M. Lagune':<11} | {'Baobab':<11} | {'C. Ivoire':<11} | {'Meilleur':<9} | {'Écart F':<9} | {'Écart %':<7}"
        print(en_tete)
        print("-" * len(en_tete))

        for r in rapport:
            pid = r["produit_id"]
            nom = r["nom"] if len(r["nom"]) <= 24 else r["nom"][:21] + "..."
            toutes = r["toutes_offres"]

            def case_prix(ens):
                o = toutes.get(ens)
                if not o: return "-"
                if not o.get("en_stock") or o.get("prix") is None:
                    return "Rupture"
                return self.formater_prix(o["prix"])

            p_ml = case_prix("Marché Lagune")
            p_bb = case_prix("Baobab Shop")
            p_ci = case_prix("Comptoir Ivoire")
            meilleure = r["meilleure"].replace("Marché Lagune", "M.Lagune").replace("Comptoir Ivoire", "C.Ivoire").replace("Baobab Shop", "Baobab")
            ecart_f = self.formater_prix(r["ecart_fcfa"])
            ecart_pct = f"{str(r['ecart_pct']).replace('.', ',')}%"

            print(f"{pid:<4} | {nom:<26} | {p_ml:<11} | {p_bb:<11} | {p_ci:<11} | {meilleure:<9} | {ecart_f:<9} | {ecart_pct:>7}")

        print("-" * len(en_tete))

    def afficher_synthese(self, synthese):
        """Affiche les victoires par boutique, l'écart moyen et le top 3 des gains."""
        print("\n" + "=" * 90)
        print("                             SYNTHÈSE DÉCISIONNELLE")
        print("=" * 90)
        total = synthese["total_produits"]
        print(f"Total de produits comparables (disponibles chez au moins 2 boutiques) : {total}\n")

        print("Nombre de victoires (combien de fois chaque boutique propose le meilleur prix) :")
        for ens, v in synthese["victoires"].items():
            pct = (v / total * 100) if total > 0 else 0
            print(f"  * {ens:<16} : {v:>2} fois ({pct:.1f} % des cas)")

        print("\nÉcart moyen par rapport au prix le plus bas :")
        for ens, em in synthese["ecarts_moyens"].items():
            print(f"  * {ens:<16} : +{em:.2f} % en moyenne")

        print("\nTop 3 des produits où il y a le plus à gagner en comparant :")
        for i, item in enumerate(synthese["top3_gains"], 1):
            print(f"  {i}. {item['nom']} (ID: {item['produit_id']})")
            print(f"     Gain réalisable : {self.formater_prix(item['ecart_fcfa'])} (écart de {item['ecart_pct']} %)")
            print(f"     Moins cher chez : {item['meilleure']} à {self.formater_prix(item['prix_min'])}\n")
        print("-" * 90)

    def afficher_panier_rentree(self, panier):
        """Affiche le coût du panier de rentrée par boutique et la combinaison optimale."""
        print("\n" + "=" * 90)
        print("                        ÉVALUATION DU PANIER DE RENTRÉE")
        print("=" * 90)
        print("Composition : 1x Tecno Spark 20, 1x Lenovo IdeaPad 3, 2x Clés USB, 1x Disque dur 1To, 1x Micro-ondes\n")

        print("Coût total dans chaque boutique prise isolément :")
        for ens, cout in panier["couts_enseignes"].items():
            if cout is not None:
                print(f"  * {ens:<16} : {self.formater_prix(cout)}")
            else:
                print(f"  * {ens:<16} : Impossible (article manquant ou en rupture)")

        cout_opt = panier["cout_optimal"]
        print(f"\nPanier Optimisé Multi-Boutiques : {self.formater_prix(cout_opt)}")
        print("Détail de la répartition optimale :")
        for c in panier["details_optimal"]:
            tot = self.formater_prix(c["prix_total"])
            u = self.formater_prix(c["prix_unitaire"])
            print(f"  - {c['nom']:<32} x{c['qte']} -> chez {c['enseigne']:<15} ({u}/u = {tot})")

        couts_valides = [c for c in panier["couts_enseignes"].values() if c is not None]
        if couts_valides:
            pire = max(couts_valides)
            gain = pire - cout_opt
            gain_pct = (gain / pire) * 100
            print(f"\nÉconomie maximale réalisée : {self.formater_prix(gain)} (-{gain_pct:.1f} % par rapport à la plus chère)")
        print("-" * 90)

    def afficher_black_friday(self, resultats_bf):
        """Affiche les résultats de l'analyse Black Friday vs reste de l'année."""
        print("\n" + "=" * 90)
        print("               ANALYSE HISTORIQUE : LE BLACK FRIDAY EST-IL UNE BONNE AFFAIRE ?")
        print("=" * 90)
        print(f"{'Enseigne':<18} | {'Moyenne Annuelle':<18} | {'Moyenne Black Friday':<22} | {'Variation (%)':<15}")
        print("-" * 80)
        for r in resultats_bf:
            ens = r["enseigne"]
            annuel = self.formater_prix(r["moyenne_annuelle"])
            bf = self.formater_prix(r["moyenne_black_friday"])
            var = f"{r['difference_pct']:+.2f} %"
            verdict = "Vraie réduction" if r["est_promotion"] else "Non avantageux"
            print(f"{ens:<18} | {annuel:<18} | {bf:<22} | {var:<8} ({verdict})")

        print("\nConclusion décisionnelle :")
        print("  - Marché Lagune et Baobab Shop font de réelles réductions (-11,2% et -11,6%).")
        print("  - Comptoir Ivoire n'a fait aucune réduction (+3,7% pendant cette période).")
        print("-" * 90)

    def afficher_complexite(self, total_lignes, temps_ms):
        """Affiche le temps d'exécution et l'explication de la complexité Big-O."""
        print("\n" + "=" * 90)
        print("             ÉTUDE DE COMPLEXITÉ ALGORITHMIQUE & PERFORMANCE BIG-O")
        print("=" * 90)
        print(f"  * Volume traité dans l'historique : {total_lignes:,} lignes.".replace(",", " "))
        print(f"  * Temps d'exécution mesuré : {temps_ms:.2f} millisecondes.")
        print("  * Complexité temporelle : O(N) où N est le nombre total de lignes.")
        print("    Grâce aux tables de hachage (dictionnaires Python), la recherche se fait en O(1) moyen,")
        print("    ce qui évite un algorithme quadratique lent en O(N²).")
        print("  * Complexité mémoire : O(K) minimale grâce au streaming ligne par ligne (csv.DictReader),")
        print("    ce qui évite de charger tout le fichier en mémoire RAM.")
        print("=" * 90 + "\n")
