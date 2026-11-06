# Rôle : Nettoie les noms/prix et associe chaque article au catalogue officiel (P01 à P30).
# Emplacement MVC : MODÈLE (Normalisation et rapprochement)

import re


def normaliser_texte(texte):
    """Met le texte en minuscules et standardise les unités (go, to, pouces, cv)."""
    if not texte:
        return ""
    t = str(texte).strip().lower()
    t = t.replace("samsun ", "samsung ")
    t = t.replace("gb", "go").replace("tb", "to").replace("ssd", "")
    t = t.replace("pc portable", "").replace("laptop", "")
    t = t.replace('"', ' pouces').replace("''", " pouces").replace("4k", "")
    t = t.replace("crystal uhd", "")
    t = t.replace("wireless mouse", "souris sans fil")
    t = t.replace("printer", "imprimante")
    t = t.replace("fridge", "refrigerateur").replace("frigo", "refrigerateur")
    t = t.replace("air conditioner", "climatiseur").replace("clim ", "climatiseur ")
    t = t.replace("blender", "mixeur")
    t = t.replace("steam iron", "fer a repasser").replace("fer philips", "fer a repasser philips")
    t = t.replace("microwave", "micro ondes")
    t = t.replace("electric kettle", "bouilloire").replace("bouilloire", "bouilloire electrique")
    t = t.replace("1hp", "1 cv").replace("1.5hp", "1.5 cv")
    t = t.replace("ventilo", "ventilateur").replace("dd externe", "disque dur externe")
    t = t.replace("seagate expansion 1to", "disque dur externe seagate 1 to")
    t = t.replace("sandisk ultra usb", "cle usb sandisk")
    t = re.sub(r'[^a-z0-9]', ' ', t)
    return " ".join(t.split())


def nettoyer_prix(valeur):
    """Convertit un prix texte en nombre flottant (retire 'FCFA', espaces et virgules)."""
    if valeur is None:
        return None
    texte = str(valeur).strip()
    if not texte or "demande" in texte.lower() or texte.lower() == "none":
        return None
    
    texte = texte.replace("FCFA", "").replace("fcfa", "").replace("cfa", "")
    texte = texte.replace("\xa0", "").replace("\u202f", "").replace(" ", "")
    texte = texte.replace(",", ".")
    
    try:
        prix = float(texte)
        return prix if prix > 0 else None
    except ValueError:
        return None


def trouver_produit_id(designation, code=""):
    """Associe le nom ou code d'un article à son identifiant officiel (P01 à P30)."""
    t = normaliser_texte(designation)
    code_propre = (code or "").upper().strip()

    # Règle pour Baobab Shop : le code BBxx correspond directement à Pxx
    if code_propre.startswith("BB") and len(code_propre) >= 4 and code_propre[2:4].isdigit():
        num = int(code_propre[2:4])
        if 1 <= num <= 30:
            return f"P{num:02d}"

    # Règles par mots-clés distinctifs
    if "a15" in t: return "P01"
    if "a25" in t: return "P02"
    if "a55" in t: return "P03"
    if "spark 20" in t: return "P04"
    if "camon 30" in t: return "P05"
    if "hot 40" in t: return "P06"
    if "note 40" in t: return "P07"
    if "a70" in t: return "P08"
    if "iphone 13" in t: return "P09"
    if "redmi note 13" in t: return "P10"
    if "250 g9" in t or ("hp" in t and "i5" in t and ("512" in t or "g9" in t)): return "P11"
    if "ideapad 3" in t or "lenovo" in t: return "P12"
    if "inspiron 15" in t or "dell" in t: return "P13"
    if "cle usb" in t or "sandisk" in t: return "P14"
    if "disque dur" in t or "seagate" in t or "1to" in t or "1 to" in t: return "P15"
    if "souris" in t or "m185" in t or "mouse" in t: return "P16"
    if "deskjet" in t or "2720" in t or "imprimante" in t or "printer" in t: return "P17"
    if "archer c6" in t or "tp link" in t or "routeur" in t: return "P18"
    if "24 pouces" in t or ("ecran" in t and "samsung" in t) or ("monitor" in t and "24" in t): return "P19"
    if "205" in t or ("refrigerateur" in t and "hisense" in t) or "frigo" in t: return "P20"
    if "200" in t or "congelateur" in t or "nasco" in t: return "P21"
    if "43 pouces" in t or ("tv" in t and "samsung" in t): return "P22"
    if "32 pouces" in t or ("tv" in t and "hisense" in t): return "P23"
    if ("climatiseur" in t or "clim" in t or "air conditioner" in t) and ("1 cv" in t or "1cv" in t or "1hp" in t or "lg" in t): return "P24"
    if "binatone" in t or "ventilateur" in t or "16 pouces" in t or "ventilo" in t: return "P25"
    if "moulinex" in t or "mixeur" in t or "blender" in t: return "P26"
    if "philips" in t or "fer" in t or "iron" in t: return "P27"
    if "micro ondes" in t or "microwave" in t or "23" in t: return "P28"
    if "bouilloire" in t or "kettle" in t or "1 7" in t or "1.7" in t: return "P29"
    if ("climatiseur" in t or "clim" in t or "air conditioner" in t) and ("1 5" in t or "1.5" in t or "hisense" in t): return "P30"

    return None
