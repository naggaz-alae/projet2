"""LOAD : fichiers de la landing zone -> tables `raw` de DuckDB.

`CREATE OR REPLACE` rend le chargement idempotent : on peut le relancer
autant de fois qu'on veut, le résultat est toujours le même.

Lancement :  python -m ingestion.load_raw
"""

import logging
from pathlib import Path

import duckdb

from ingestion import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("load_raw")


def run() -> None:
    landing = Path(config.LANDING_DIR)
    Path(config.DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(config.DUCKDB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # éCO2mix : on garde le nom du fichier pour savoir de quel jeu vient la ligne
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.eco2mix AS
        SELECT
            *,
            CASE WHEN filename LIKE '%cons-def%' THEN 'definitif' ELSE 'temps_reel' END AS jeu_source,
            current_timestamp AS charge_le
        FROM read_json_auto('{landing}/eco2mix/*.json', filename = true, union_by_name = true)
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE raw.meteo AS
        SELECT *, current_timestamp AS charge_le
        FROM read_json_auto('{landing}/meteo/temperatures.json')
    """)

    controler_qualite(con)
    con.close()


def controler_qualite(con: duckdb.DuckDBPyConnection) -> None:
    """Premiers contrôles : couverture par année et valeurs manquantes."""
    logger.info("--- Couverture éCO2mix (créneaux de 30 min, ~17 520 attendus par an) ---")
    for annee, jeu, nb in con.execute("""
        SELECT year(date_heure::TIMESTAMPTZ) AS annee, jeu_source, count(*) AS nb
        FROM raw.eco2mix GROUP BY ALL ORDER BY annee, jeu_source
    """).fetchall():
        logger.info("%s | %-10s | %s créneaux", annee, jeu, nb)

    nb_sans_co2 = con.execute("SELECT count(*) FROM raw.eco2mix WHERE taux_co2 IS NULL").fetchone()[0]
    logger.info("Créneaux sans taux de CO2 : %s", nb_sans_co2)

    for ville, nb, nb_nuls in con.execute("""
        SELECT ville, count(*), count(*) FILTER (WHERE temperature_moyenne IS NULL)
        FROM raw.meteo GROUP BY ville ORDER BY ville
    """).fetchall():
        logger.info("Météo %-10s : %s jours (%s manquants)", ville, nb, nb_nuls)


if __name__ == "__main__":
    run()
