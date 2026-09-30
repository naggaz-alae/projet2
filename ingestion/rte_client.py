"""Client de l'API éCO2mix de RTE (plateforme ODRÉ, format Opendatasoft).

Deux jeux de données :
- `eco2mix-national-cons-def` : données consolidées puis définitives (fiables)
- `eco2mix-national-tr`       : données temps réel (les mois les plus récents)
On récupère les deux ; dbt choisira la meilleure version de chaque créneau.
"""

import logging
from datetime import date, timedelta

from ingestion.http_utils import APIError, get_json

logger = logging.getLogger(__name__)

ODRE_BASE_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
DATASET_DEFINITIF = "eco2mix-national-cons-def"
DATASET_TEMPS_REEL = "eco2mix-national-tr"

# Seules les colonnes utiles au projet (MW pour les puissances, g/kWh pour le CO2)
CHAMPS = [
    "date_heure",
    "consommation",
    "prevision_j1",
    "nucleaire",
    "eolien",
    "solaire",
    "hydraulique",
    "gaz",
    "charbon",
    "fioul",
    "bioenergies",
    "pompage",
    "ech_physiques",
    "taux_co2",
]


def periodes_annuelles(start: date, end: date) -> list[tuple[date, date]]:
    """Découpe [start, end] en tranches d'un an (1 appel API = 1 année)."""
    periodes = []
    debut = start
    while debut <= end:
        fin = min(date(debut.year, 12, 31), end)
        periodes.append((debut, fin))
        debut = fin + timedelta(days=1)
    return periodes


def construire_parametres(start: date, end: date) -> dict:
    """Paramètres de l'endpoint d'export (pas de limite de 100 lignes)."""
    fin_exclue = end + timedelta(days=1)
    return {
        "select": ",".join(CHAMPS),
        # Les lignes au quart d'heure ne contiennent que des prévisions :
        # on ne garde que les créneaux où la consommation réelle est connue.
        "where": (
            f"date_heure >= date'{start.isoformat()}' "
            f"AND date_heure < date'{fin_exclue.isoformat()}' "
            "AND consommation is not null"
        ),
        "order_by": "date_heure",
        # UTC : évite les doublons / trous lors des changements d'heure
        "timezone": "UTC",
    }


def recuperer_eco2mix(dataset: str, start: date, end: date) -> list[dict]:
    """Renvoie les lignes éCO2mix de `dataset` entre `start` et `end` inclus.

    Une liste vide est possible (ex. : période pas encore publiée dans ce jeu).
    """
    url = f"{ODRE_BASE_URL}/{dataset}/exports/json"
    lignes = get_json(url, params=construire_parametres(start, end))
    if not isinstance(lignes, list):
        raise APIError(f"Réponse inattendue de {dataset} : {str(lignes)[:200]}")
    logger.info("%s : %s créneaux entre %s et %s", dataset, len(lignes), start, end)
    return lignes
