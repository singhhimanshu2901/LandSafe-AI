import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../backend/.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be configured in the environment.")
FEATURE_WINDOWS = [1, 6, 12, 24, 72, 168]  # hours (168 = 7 days)
