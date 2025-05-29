"""
Test fixtures and configuration for VerbynDich provider tests
"""

import pytest
import logging
from app.api.verbynDich import VerbynDich


@pytest.fixture
def logger():
    """Create a logger for testing"""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger(__name__)


@pytest.fixture
def verbyndich_provider(logger):
    """Create a VerbynDich provider instance for testing"""
    return VerbynDich(logger=logger)


@pytest.fixture
def sample_offers():
    """Sample offer data from VerbynDich API responses"""
    return [
        {
            "product": "VerbynDich Basic 25",
            "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 30€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 25 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 29€.",
            "last": False,
            "valid": True
        },
        {
            "product": "VerbynDich Basic 500",
            "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 50€ im Monat erhalten Sie eine Fiber-Verbindung mit einer Geschwindigkeit von 500 Mbit/s. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Ab 250GB pro Monat wird die Geschwindigkeit gedrosselt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 48€.",
            "last": False,
            "valid": True
        },
        {
            "product": "VerbynDich Premium 100",
            "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 49€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 100 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€. Ab dem 24. Monat beträgt der monatliche Preis 48€.",
            "last": False,
            "valid": True
        },
        {
            "product": "VerbynDich Premium 25 Young",
            "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 35€ im Monat erhalten Sie eine DSL-Verbindung mit einer Geschwindigkeit von 25 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€.",
            "last": False,
            "valid": True
        }
    ]


@pytest.fixture
def invalid_offers():
    """Sample invalid offer data for testing error handling"""
    return [
        {
            "product": "",
            "description": "",
            "valid": False
        },
        {
            "product": "VerbynDich Invalid",
            "description": "Invalid description without price or speed info",
            "valid": True
        },
        {
            "valid": False
        }
    ]
