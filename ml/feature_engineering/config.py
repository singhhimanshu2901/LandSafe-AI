import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../backend/.env'))

def get_db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL must be configured in the environment.")
    return url

FEATURE_WINDOWS = [1, 6, 12, 24, 72, 168]  # hours (168 = 7 days)
