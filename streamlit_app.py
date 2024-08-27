import streamlit as st
import pytesseract
from PIL import Image

# Définition des risques
press_max_risque = {
    "léger": 10.0,
    "ordinaire": 12.0,
    "extra": 14.0,
}

# Base de données complète des normes NFPA
nfpa_standards = {
    "acier_soude": {
        "pressure_max": 20.7,  # en bars
        "min_wall_thickness": {
            25: {"mm": 2.77, "inch": 0.109},
            32: {"mm": 2.87, "inch": 0.113},
            38: {"mm": 3.38, "inch": 0.133},
            51: {"mm": 3.40, "inch": 0.134},
            64: {"mm": 3.56, "inch": 0.140},
            76: {"mm": 3.68, "inch": 0.145},
            102: {"mm": 4.06, "inch": 0.160},
            127: {"mm": 4.78, "inch": 0.188},
            152: {"mm": 4.78, "inch": 0.188},
            203: {"mm": 4.78, "inch": 0.188},
            254: {"mm": 6.02, "inch": 0.237},
        },
        "standards": ["ASTM A 795", "ANSI / ASTM A 53", "ASTM A 135"],
    },
    "acier_filete": {
        "pressure_max": 20.7,
        "min_wall_thickness": {
            25: {"mm": 3.40, "inch": 0.134},
            32: {"mm": 3.73, "inch": 0.147},
            38: {"mm": 3.91, "inch": 0.154},
            51: {"mm": 4.09, "inch": 0.161},
            64: {"mm": 4.78, "inch": 0.188},
            76: {"mm": 5.16, "inch": 0.203},
            102: {"mm": 5.44, "inch": 0.214},
            127: {"mm": 5.74, "inch": 0.226},
            152: {"mm": 6.02, "inch": 0.237},
            203: {"mm": 6.35, "inch": 0.250},
        },
        "standards": ["ASTM A 795", "ANSI / ASTM A 53", "ASTM A 135"],
    },
    "cuivre_K": {
        "pressure_max": 20.7,
        "min_wall_thickness": {
            15: {"mm": 1.02, "inch": 0.040},
            20: {"mm": 1.22, "inch": 0.048},
            25: {"mm": 1.65, "inch": 0.065},
            32: {"mm": 2.11, "inch": 0.083},
            38: {"mm": 2.41, "inch": 0.095},
            51: {"mm": 2.77, "inch": 0.109},
            64: {"mm": 3.05, "inch": 0.120},
        },
        "standards": ["ASTM B 75", "ASTM B 88", "ASTM B 251"],
    },
    "cuivre_L": {
        "pressure_max": 15.0,
        "min_wall_thickness": {
            15: {"mm": 0.89, "inch": 0.035},
            20: {"mm": 1.02, "inch": 0.040},
            25: {"mm": 1.27, "inch": 0.050},
            32: {"mm": 1.65, "inch": 0.065},
            38: {"mm": 1.83, "inch": 0.072},
            51: {"mm": 2.11, "inch": 0.083},
            64: {"mm": 2.41, "inch": 0.095},
        },
        "standards": ["ASTM B 75", "ASTM B 88", "ASTM B 251"],
    },
    "cuivre_M": {
        "pressure_max": 10.0,
        "min_wall_thickness": {
            15: {"mm": 0.71, "inch": 0.028},
            20: {"mm": 0.81, "inch": 0.032},
            25: {"mm": 0.99, "inch": 0.039},
            32: {"mm": 1.27, "inch": 0.050},
            38: {"mm": 1.50, "inch": 0.059},
            51: {"mm": 1.78, "inch": 0.070},
            64: {"mm": 2.03, "inch": 0.080},
        },
        "standards": ["ASTM B 75", "ASTM B 88", "ASTM B 251"],
    },
    "CPVC": {
        "pressure_max": 20.7,
        "min_wall_thickness": {
            25: {"mm": 2.77, "inch": 0.109},
            32: {"mm": 3.38, "inch": 0.133},
            51: {"mm": 4.06, "inch": 0.160},
        },
        "standards": ["ASTM F 442", "ASTM D 2846", "ASTM F 493"],
    },
    "acier_sans_soudure": {
        "pressure_max": 20.7,
        "min_wall_thickness": {
            25: {"mm": 2.77, "inch": 0.109},
            32: {"mm": 2.87, "inch": 0.113},
            38: {"mm": 3.38, "inch": 0.133},
            51: {"mm": 3.40, "inch": 0.134},
            64: {"mm": 3.56, "inch": 0.140},
            76: {"mm": 3.68, "inch": 0.145},
            102: {"mm": 4.06, "inch": 0.160},
            127: {"mm": 4.78, "inch": 0.188},
            152: {"mm": 4.78, "inch": 0.188},
            203: {"mm": 4.78, "inch": 0.188},
            254: {"mm": 6.02, "inch": 0.237},
        },
        "standards": ["ASTM A 53", "ASTM A 106", "API 5L"],
    },
}

# Fonction de vérification de conformité
def verifier_conformite(tuyau, diametre, pression, epaisseur, type_risque):
    if tuyau not in nfpa_standards:
        return False, "Type de tuyau non reconnu par les normes NFPA."

    specs = nfpa_standards[tuyau]

    # Vérification de la pression en fonction du type de risque
    if type_risque in press_max_risque:
        max_pressure_risque = press_max_risque[type_risque]
    else:
        return False, "Type de risque non reconnu."

    if pression > max_pressure_risque:
        return False, f"Pression {pression} bar dépasse la pression maximale autorisée de {max_pressure_risque} bar pour le type de risque {type_risque}."

    if pression > specs["pressure_max"]:
        return False, f"Pression {pression} bar dépasse la pression maximale de {specs['pressure_max']} bar pour le tuyau {tuyau}."

    if "min_wall_thickness" in specs:
        if diametre in specs["min_wall_thickness"]:
            min_thickness = specs["min_wall_thickness"][diametre]
        else:
            return False, "Aucune épaisseur minimale spécifiée pour ce diamètre."

        if epaisseur < min_thickness["mm"]:
            return False, f"Épaisseur {epaisseur} mm est inférieure à l'épaisseur minimale requise de {min_thickness['mm']} mm pour ce tuyau et diamètre."

    return True, "Tuyau conforme aux normes NFPA."

# Interface Streamlit
st.title("Analyse de Bordereau selon NFPA")

uploaded_file = st.file_uploader("Choisissez une image de bordereau", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Bordereau chargé', use_column_width=True)
    
    # Extraire le texte de l'image
    texte = pytesseract.image_to_string(image)
    st.write("Texte extrait :", texte)
    
    # Simuler l'analyse d'un tuyau basé sur des données extraites
    # Vous pouvez remplacer les valeurs ici par celles extraites du texte
    conforme, message = verifier_conformite("acier_sans_soudure", 25, 10.0, 4.0, "léger")
    st.write(f"Conformité: {conforme}, Message: {message}")

