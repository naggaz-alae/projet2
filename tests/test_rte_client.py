"""Tests du client éCO2mix : aucun appel réseau (API simulée)."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import requests

from ingestion.http_utils import APIError
from ingestion.rte_client import construire_parametres, periodes_annuelles, recuperer_eco2mix

LIGNE_EXEMPLE = {
    "date_heure": "2024-01-15T18:00:00+00:00",
    "consommation": 78450,
    "nucleaire": 51200,
    "eolien": 6300,
    "solaire": 0,
    "taux_co2": 48,
}


def fausse_reponse(payload) -> MagicMock:
    reponse = MagicMock()
    reponse.json.return_value = payload
    reponse.raise_for_status.return_value = None
    return reponse


def test_periodes_annuelles_decoupe_par_annee():
    assert periodes_annuelles(date(2023, 3, 1), date(2025, 6, 30)) == [
        (date(2023, 3, 1), date(2023, 12, 31)),
        (date(2024, 1, 1), date(2024, 12, 31)),
        (date(2025, 1, 1), date(2025, 6, 30)),
    ]


def test_parametres_filtrent_periode_et_consommation():
    params = construire_parametres(date(2024, 1, 1), date(2024, 12, 31))
    assert "date'2024-01-01'" in params["where"]
    assert "date'2025-01-01'" in params["where"]  # borne de fin exclue = lendemain
    assert "consommation is not null" in params["where"]
    assert params["timezone"] == "UTC"
    assert "taux_co2" in params["select"]


@patch("ingestion.http_utils.requests.get")
def test_recuperer_eco2mix_renvoie_les_lignes(mock_get):
    mock_get.return_value = fausse_reponse([LIGNE_EXEMPLE])
    lignes = recuperer_eco2mix("eco2mix-national-cons-def", date(2024, 1, 1), date(2024, 12, 31))
    assert lignes == [LIGNE_EXEMPLE]
    assert "eco2mix-national-cons-def/exports/json" in mock_get.call_args.args[0]


@patch("ingestion.http_utils.requests.get")
def test_recuperer_eco2mix_accepte_une_periode_vide(mock_get):
    mock_get.return_value = fausse_reponse([])
    assert recuperer_eco2mix("eco2mix-national-tr", date(2023, 1, 1), date(2023, 12, 31)) == []


@patch("ingestion.http_utils.requests.get")
def test_recuperer_eco2mix_rejette_une_reponse_inattendue(mock_get):
    mock_get.return_value = fausse_reponse({"error": "quota dépassé"})
    with pytest.raises(APIError):
        recuperer_eco2mix("eco2mix-national-tr", date(2024, 1, 1), date(2024, 1, 31))


@patch("ingestion.http_utils.time.sleep")
@patch("ingestion.http_utils.requests.get")
def test_reessaie_trois_fois_puis_echoue(mock_get, _mock_sleep):
    mock_get.side_effect = requests.ConnectionError("réseau coupé")
    with pytest.raises(APIError):
        recuperer_eco2mix("eco2mix-national-tr", date(2024, 1, 1), date(2024, 1, 31))
    assert mock_get.call_count == 3
