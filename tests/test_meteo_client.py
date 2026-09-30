"""Tests du client Open-Meteo : aucun appel réseau (API simulée)."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from ingestion.config import Ville
from ingestion.http_utils import APIError
from ingestion.meteo_client import recuperer_temperatures

PARIS = Ville("Paris", 48.85, 2.35)
LYON = Ville("Lyon", 45.76, 4.83)


def reponse_ville(temperatures: list) -> dict:
    jours = [f"2024-01-0{i + 1}" for i in range(len(temperatures))]
    return {"daily": {"time": jours, "temperature_2m_mean": temperatures}}


def fausse_reponse(payload) -> MagicMock:
    reponse = MagicMock()
    reponse.json.return_value = payload
    reponse.raise_for_status.return_value = None
    return reponse


@patch("ingestion.http_utils.requests.get")
def test_plusieurs_villes_une_ligne_par_ville_et_par_jour(mock_get):
    mock_get.return_value = fausse_reponse([reponse_ville([3.1, 4.2]), reponse_ville([1.0, 2.5])])
    lignes = recuperer_temperatures([PARIS, LYON], date(2024, 1, 1), date(2024, 1, 2))
    assert len(lignes) == 4
    assert lignes[0] == {"ville": "Paris", "date": "2024-01-01", "temperature_moyenne": 3.1}
    assert lignes[3] == {"ville": "Lyon", "date": "2024-01-02", "temperature_moyenne": 2.5}


@patch("ingestion.http_utils.requests.get")
def test_une_seule_ville_objet_au_lieu_de_liste(mock_get):
    mock_get.return_value = fausse_reponse(reponse_ville([5.0]))
    lignes = recuperer_temperatures([PARIS], date(2024, 1, 1), date(2024, 1, 1))
    assert lignes == [{"ville": "Paris", "date": "2024-01-01", "temperature_moyenne": 5.0}]


@patch("ingestion.http_utils.requests.get")
def test_nombre_de_villes_incoherent(mock_get):
    mock_get.return_value = fausse_reponse([reponse_ville([5.0])])
    with pytest.raises(APIError):
        recuperer_temperatures([PARIS, LYON], date(2024, 1, 1), date(2024, 1, 1))
