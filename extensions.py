
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = None


def init_extensions(app):
    global redis_client

    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        app.logger.info(
            "REDIS_URL not configured. Running without Redis."
        )
        redis_client = None
        return

    try:
        from redis import Redis

        client = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3
        )

        client.ping()
        redis_client = client

        app.logger.info("Redis connected successfully.")

    except Exception as error:
        redis_client = None

        app.logger.warning(
            "Redis connection unavailable. "
            "Application will continue without Redis. Details: %s",
            error
        )
