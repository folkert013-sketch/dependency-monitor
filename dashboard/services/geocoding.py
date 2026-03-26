import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def geocode_address(address):
    """Convert an address string to (latitude, longitude) using Google Geocoding API.

    Returns a tuple (lat, lng) on success, or None on failure.
    """
    api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
    if not api_key or not address:
        return None

    try:
        resp = requests.get(
            GEOCODE_URL,
            params={
                "address": address,
                "key": api_key,
                "region": "nl",
                "language": "nl",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        logger.exception("Google Geocoding API request failed for: %s", address[:100])
        return None

    # Log API usage
    try:
        from dashboard.services.api_usage import log_api_call
        log_api_call(service="google_geocoding", description=f"Geocode: {address[:100]}")
    except Exception:
        logger.warning("Could not log Geocoding API usage", exc_info=True)

    results = data.get("results", [])
    if not results:
        logger.info("No geocoding results for: %s", address[:100])
        return None

    location = results[0].get("geometry", {}).get("location", {})
    lat = location.get("lat")
    lng = location.get("lng")
    if lat is not None and lng is not None:
        return (lat, lng)
    return None


def geocode_prospect(prospect):
    """Geocode a prospect if it has an address but no coordinates.

    Returns True if coordinates were set, False otherwise.
    """
    if not prospect.address or (prospect.latitude is not None and prospect.longitude is not None):
        return False

    result = geocode_address(prospect.address)
    if result:
        prospect.latitude, prospect.longitude = result
        prospect.save(update_fields=["latitude", "longitude"])
        return True
    return False
