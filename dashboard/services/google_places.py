import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Wrapper voor Google Places API (New) — Text Search endpoint."""

    BASE_URL = "https://places.googleapis.com/v1/places:searchText"
    FIELD_MASK = (
        "places.id,places.displayName,places.formattedAddress,"
        "places.nationalPhoneNumber,places.websiteUri,"
        "places.rating,places.userRatingCount,"
        "places.primaryType,places.location"
    )

    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY

    def text_search(self, query, location_bias=None, radius_m=10000,
                     max_results=20, min_rating=None, included_type=None):
        """Search for places using the Text Search (New) endpoint.

        Returns a list of dicts with normalised keys.
        """
        if not self.api_key:
            raise RuntimeError("GOOGLE_PLACES_API_KEY is niet geconfigureerd")

        body = {"textQuery": query, "maxResultCount": max_results}
        if min_rating is not None:
            body["minRating"] = min_rating
        if included_type:
            body["includedType"] = included_type
        if location_bias:
            body["locationBias"] = {
                "circle": {
                    "center": {
                        "latitude": location_bias["lat"],
                        "longitude": location_bias["lng"],
                    },
                    "radius": radius_m,
                }
            }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": self.FIELD_MASK,
        }

        try:
            resp = requests.post(self.BASE_URL, json=body, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            logger.exception("Google Places API request failed")
            raise

        results = []
        for place in data.get("places", []):
            display_name = place.get("displayName", {})
            location = place.get("location", {})
            results.append({
                "place_id": place.get("id", ""),
                "name": display_name.get("text", ""),
                "address": place.get("formattedAddress", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "website": place.get("websiteUri", ""),
                "rating": place.get("rating"),
                "reviews_count": place.get("userRatingCount", 0),
                "business_type": place.get("primaryType", ""),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
            })
        return results
