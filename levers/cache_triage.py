import hashlib
import json
import time

# ---------------------------------------------------------
# SIMPLE IN-MEMORY CACHE
# ---------------------------------------------------------

CACHE = {}

CACHE_TTL_SECONDS = 300


# ---------------------------------------------------------
# CACHE STATISTICS
# ---------------------------------------------------------

CACHE_HITS = 0
CACHE_MISSES = 0


def make_cache_key(
    symptoms: str,
    age: int,
) -> str:
    """
    Create a stable hash key from the request data.

    Same age + same symptoms
    will produce the same cache key.
    """

    normalized_data = {
        "age": age,
        "symptoms": symptoms.strip().lower(),
    }

    raw = json.dumps(
        normalized_data,
        sort_keys=True,
    )

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_from_cache(
    key: str,
):
    """
    Return cached value if:
    - key exists
    - entry has not expired
    """

    global CACHE_HITS
    global CACHE_MISSES

    entry = CACHE.get(key)

    if entry is None:
        CACHE_MISSES += 1
        return None

    age_seconds = time.time() - entry["created_at"]

    if age_seconds > CACHE_TTL_SECONDS:
        del CACHE[key]

        CACHE_MISSES += 1

        return None

    CACHE_HITS += 1

    return entry["value"]


def save_to_cache(
    key: str,
    value: dict,
):
    """
    Save result into cache.
    """

    CACHE[key] = {
        "value": value,
        "created_at": time.time(),
    }


def get_cache_stats():
    """
    Return cache metrics.
    """

    total = CACHE_HITS + CACHE_MISSES

    if total == 0:
        hit_rate = 0.0
    else:
        hit_rate = (CACHE_HITS / total) * 100

    return {
        "hits": CACHE_HITS,
        "misses": CACHE_MISSES,
        "total": total,
        "hit_rate_percent": hit_rate,
        "cache_size": len(CACHE),
    }


def clear_cache():
    """
    Clear both stored responses and metrics.
    """

    global CACHE_HITS
    global CACHE_MISSES

    CACHE.clear()

    CACHE_HITS = 0
    CACHE_MISSES = 0
