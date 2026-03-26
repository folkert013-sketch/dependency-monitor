"""
App-wide prospect deduplication utilities.

All prospect save/import operations should use find_existing_prospect()
to prevent duplicate companies across all ProspectGroups.
"""

import re

from dashboard.models import Prospect


# Common Dutch/English company suffixes to strip for fuzzy matching
_COMPANY_SUFFIXES = [
    "b.v.", "bv", "b.v", "n.v.", "nv",
    "holding", "groep", "group",
    "nederland", "netherlands", "nl",
    "international", "intl",
]

_SUFFIX_PATTERN = re.compile(
    r"\s*[-.,]?\s*(" + "|".join(re.escape(s) for s in _COMPANY_SUFFIXES) + r")\s*$",
    re.IGNORECASE,
)


def clean_company_name(name: str) -> str:
    """Strip common company suffixes (BV, Holding, etc.) for fuzzy matching."""
    cleaned = name.strip()
    # Iteratively strip suffixes (e.g., "Foo Holding B.V." → "Foo")
    prev = None
    while cleaned != prev:
        prev = cleaned
        cleaned = _SUFFIX_PATTERN.sub("", cleaned).strip()
    return cleaned


def find_existing_prospect(name: str, address: str = "", place_id: str = "") -> Prospect | None:
    """
    Find an existing prospect using multiple matching strategies.

    Order: place_id → name+address exact → name exact → cleaned name.
    Returns the first match or None.
    """
    name = name.strip()
    if not name:
        return None

    # 1. Exact place_id match (most reliable)
    if place_id:
        match = Prospect.objects.filter(place_id=place_id).first()
        if match:
            return match

    # 2. Exact name + address match
    if address:
        match = Prospect.objects.filter(
            name__iexact=name, address__iexact=address.strip()
        ).first()
        if match:
            return match

    # 3. Exact name match (without address)
    match = Prospect.objects.filter(name__iexact=name).first()
    if match:
        return match

    # 4. Cleaned name match (strip BV, Holding, etc.)
    cleaned = clean_company_name(name)
    if cleaned and cleaned.lower() != name.lower():
        match = Prospect.objects.filter(name__iexact=cleaned).first()
        if match:
            return match
        # Also try: does an existing prospect's cleaned name match?
        for prospect in Prospect.objects.filter(name__icontains=cleaned):
            if clean_company_name(prospect.name).lower() == cleaned.lower():
                return prospect

    return None


def check_duplicates_bulk(names: list[str]) -> dict[str, Prospect]:
    """
    Bulk duplicate check for a list of company names.

    Returns dict mapping lowercased name → existing Prospect.
    """
    result = {}
    for name in names:
        name = name.strip()
        if not name or name.lower() in result:
            continue
        match = find_existing_prospect(name)
        if match:
            result[name.lower()] = match
    return result


def is_duplicate_in_group(prospect: Prospect, group) -> bool:
    """Check if prospect is already in this group."""
    return prospect.groups.filter(pk=group.pk).exists()
