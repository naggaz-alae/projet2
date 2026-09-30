"""Configuration centrale de l'ingestion (lue depuis le fichier .env)."""

import os
from dataclasses import dataclass
from datetime import date

from dotenv import load_dotenv

load_dotenv()

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/novawatt.duckdb")
LANDING_DIR = os.getenv("LANDING_DIR", "data/landing")
START_DATE = date.fromisoformat(os.getenv("START_DATE", "2023-01-01"))
END_DATE = date.fromisoformat(os.getenv("END_DATE", "2025-12-31"))


@dataclass(frozen=True)
class Ville:
    nom: str
    latitude: float
    longitude: float


# Grandes villes réparties sur le territoire : leur moyenne (pondérée par la
# population, calculée plus tard dans dbt) sert de « température France ».
VILLES_METEO = [
    Ville("Paris", 48.8566, 2.3522),
    Ville("Lyon", 45.7640, 4.8357),
    Ville("Marseille", 43.2965, 5.3698),
    Ville("Lille", 50.6292, 3.0573),
    Ville("Toulouse", 43.6047, 1.4442),
    Ville("Bordeaux", 44.8378, -0.5792),
    Ville("Nantes", 47.2184, -1.5536),
    Ville("Strasbourg", 48.5734, 7.7521),
]
