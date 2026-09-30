"""EXTRACT : API -> fichiers JSON dans la « landing zone » (data/landing).

On garde une copie brute de chaque réponse sur disque :
- on peut recharger la base sans rappeler les API ;
- on sait exactement ce que l'API a renvoyé en cas de doute.

Lancement :  python -m ingestion.extract
"""

import json
import logging
from pathlib import Path

from ingestion import config
from ingestion.meteo_client import recuperer_temperatures
from ingestion.rte_client import (
    DATASET_DEFINITIF,
    DATASET_TEMPS_REEL,
    periodes_annuelles,
    recuperer_eco2mix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("extract")


def ecrire_json(lignes: list[dict], chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(lignes, ensure_ascii=False), encoding="utf-8")
    logger.info("Écrit : %s (%s lignes)", chemin, len(lignes))


def run() -> None:
    landing = Path(config.LANDING_DIR)

    # 1. RTE éCO2mix, année par année et pour les deux jeux de données
    for debut, fin in periodes_annuelles(config.START_DATE, config.END_DATE):
        for dataset in (DATASET_DEFINITIF, DATASET_TEMPS_REEL):
            lignes = recuperer_eco2mix(dataset, debut, fin)
            if not lignes:
                logger.warning("%s : aucune donnée pour %s, fichier non créé", dataset, debut.year)
                continue
            ecrire_json(lignes, landing / "eco2mix" / f"{dataset}_{debut.year}.json")

    # 2. Météo : un seul appel pour toutes les villes et toute la période
    temperatures = recuperer_temperatures(config.VILLES_METEO, config.START_DATE, config.END_DATE)
    ecrire_json(temperatures, landing / "meteo" / "temperatures.json")


if __name__ == "__main__":
    run()
