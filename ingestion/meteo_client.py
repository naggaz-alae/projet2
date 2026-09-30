"""Client de l'API historique Open-Meteo (gratuite, sans clé)."""

import logging
from datetime import date

from ingestion.config import Ville
from ingestion.http_utils import APIError, get_json

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def recuperer_temperatures(villes: list[Ville], start: date, end: date) -> list[dict]:
    """Température moyenne journalière de chaque ville, en un seul appel.

    Renvoie une ligne par ville et par jour :
    {"ville": "Paris", "date": "2023-01-01", "temperature_moyenne": 12.3}
    """
    params = {
        "latitude": ",".join(str(v.latitude) for v in villes),
        "longitude": ",".join(str(v.longitude) for v in villes),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_mean",
        "timezone": "Europe/Paris",
    }
    reponse = get_json(ARCHIVE_URL, params=params)

    # Plusieurs lieux -> l'API renvoie une liste ; un seul lieu -> un objet
    resultats = reponse if isinstance(reponse, list) else [reponse]
    if len(resultats) != len(villes):
        raise APIError(f"{len(villes)} villes demandées, {len(resultats)} reçues")

    lignes = []
    for ville, resultat in zip(villes, resultats):
        jours = resultat["daily"]["time"]
        temperatures = resultat["daily"]["temperature_2m_mean"]
        if len(jours) != len(temperatures):
            raise APIError(f"Données incohérentes pour {ville.nom}")
        lignes.extend(
            {"ville": ville.nom, "date": jour, "temperature_moyenne": temp}
            for jour, temp in zip(jours, temperatures)
        )
    logger.info("Open-Meteo : %s lignes (%s villes)", len(lignes), len(villes))
    return lignes
