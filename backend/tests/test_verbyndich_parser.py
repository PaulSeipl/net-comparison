#!/usr/bin/env python3
"""
Test script for VerbynDich offer parsing functionality
"""

import json
import logging
from app.api.verbynDich import VerbynDich

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test data from notes.md
test_offers = [
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
        "product": "VerbynDich Premium 100 Young",
        "description": "Dieses einzigartige Angebot ist der perfekte Match für Sie. Für nur 45€ im Monat erhalten Sie eine Cable-Verbindung mit einer Geschwindigkeit von 100 Mbit/s. Zusätzlich sind folgende Fernsehsender enthalten RobynTV+. Zögern Sie nicht und schlagen Sie jetzt zu!\n\nBitte beachten Sie, dass die Mindestvertragslaufzeit 12 Monate beträgt. Dieses Angebot ist nur für Personen unter 27 Jahren verfügbar. Mit diesem Angebot erhalten Sie einen Rabatt von 12% auf Ihre monatliche Rechnung bis zum 24. Monat. Der maximale Rabatt beträgt 107€.",
        "last": False,
        "valid": True
    }
]

def test_verbyndich_parser():
    """Test the VerbynDich offer parser with sample data"""
    print("Testing VerbynDich Offer Parser")
    print("=" * 50)
    
    # Create VerbynDich instance
    provider = VerbynDich(logger=logger)
    
    for i, test_offer in enumerate(test_offers, 1):
        print(f"\nTest {i}: {test_offer['product']}")
        print("-" * 40)
        
        # Parse the offer
        normalized_offer = provider.normalize_offer(test_offer)
        
        if normalized_offer:
            print("✅ Successfully parsed!")
            print(f"Provider: {normalized_offer['provider']}")
            print(f"Offer ID: {normalized_offer['offer_id']}")
            print(f"Name: {normalized_offer['name']}")
            print(f"Speed: {normalized_offer['speed']} Mbps")
            print(f"Monthly Cost: €{normalized_offer['monthly_cost'] / 100:.2f}")
            print(f"Contract Duration: {normalized_offer['contract_duration']} months")
            print(f"Connection Type: {normalized_offer['connection_type']}")
            
            if normalized_offer.get('price_after_promotion'):
                print(f"Price After Promotion: €{normalized_offer['price_after_promotion'] / 100:.2f}")
            
            if normalized_offer.get('special_features'):
                print("Special Features:")
                for feature in normalized_offer['special_features']:
                    print(f"  - {feature}")
        else:
            print("❌ Failed to parse offer")
        
        print()

if __name__ == "__main__":
    test_verbyndich_parser()
