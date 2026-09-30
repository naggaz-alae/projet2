"""Appel HTTP partagé par tous les clients API : JSON + retries."""

import logging
import time

import requests

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Levée quand une API ne renvoie pas de réponse exploitable."""


def get_json(url: str, params: dict | None = None, retries: int = 3, timeout: int = 120):
    """GET qui renvoie le JSON décodé, avec jusqu'à `retries` tentatives
    (attente de 2 s, puis 4 s… entre deux essais : backoff exponentiel)."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as err:
            last_error = err
            logger.warning("Tentative %s/%s échouée sur %s : %s", attempt, retries, url, err)
            if attempt < retries:
                time.sleep(2**attempt)
    raise APIError(f"Échec après {retries} tentatives sur {url} : {last_error}")
