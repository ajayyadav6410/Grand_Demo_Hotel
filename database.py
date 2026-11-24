
import os

import turso_serverless
from dotenv import load_dotenv

# Load private database credentials from .env
load_dotenv()


def get_db_connection():
    """
    Create and return a connection to the Turso database.
    """

    database_url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not database_url:
        raise RuntimeError(
            "TURSO_DATABASE_URL is missing in the .env file."
        )

    if not auth_token:
        raise RuntimeError(
            "TURSO_AUTH_TOKEN is missing in the .env file."
        )

    connection = turso_serverless.connect(
        database_url,
        auth_token=auth_token
    )

    return connection
