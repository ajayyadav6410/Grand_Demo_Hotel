
import extensions


def get_cache(key):
    if extensions.redis_client is None:
        return None

    try:
        return extensions.redis_client.get(key)
    except Exception:
        return None


def set_cache(key, value, expiry=300):
    if extensions.redis_client is None:
        return False

    try:
        extensions.redis_client.setex(key, expiry, value)
        return True
    except Exception:
        return False


def delete_cache(key):
    if extensions.redis_client is None:
        return False

    try:
        extensions.redis_client.delete(key)
        return True
    except Exception:
        return False
