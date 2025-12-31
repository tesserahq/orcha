"""Utility for caching unique event types using tessera cache."""

from typing import List, Optional
from tessera_sdk.utils.cache import Cache

# Cache key for storing event types list
EVENT_TYPES_CACHE_KEY = "orcha.event_types"

# Long TTL (1 year in seconds) since event types should persist
EVENT_TYPES_TTL = 31536000


def _get_event_types_cache() -> Cache:
    """Get or create the event types cache instance."""
    return Cache(namespace="event_types")


def add_event_type(event_type: str) -> None:
    """
    Add an event type to the cache if it doesn't already exist.

    Args:
        event_type: The event type string to add to the cache
    """
    if not event_type:
        return

    cache = _get_event_types_cache()
    event_types: List[str] = cache.read(EVENT_TYPES_CACHE_KEY) or []

    # Add event type if not already in the list (maintain uniqueness)
    if event_type not in event_types:
        event_types.append(event_type)
        cache.write(EVENT_TYPES_CACHE_KEY, event_types, ttl=EVENT_TYPES_TTL)


def get_event_types() -> List[str]:
    """
    Get the list of all registered event types from cache.

    Returns:
        List of unique event type strings, empty list if none exist
    """
    cache = _get_event_types_cache()
    return cache.read(EVENT_TYPES_CACHE_KEY) or []


def set_event_types(event_types: List[str]) -> None:
    """
    Set all event types in the cache (replaces existing list).
    Used for backfilling the cache from the database.

    Args:
        event_types: List of unique event type strings to store in cache
    """
    cache = _get_event_types_cache()
    # Filter out empty strings and ensure uniqueness
    unique_event_types = list(set(filter(None, event_types)))
    cache.write(EVENT_TYPES_CACHE_KEY, unique_event_types, ttl=EVENT_TYPES_TTL)
