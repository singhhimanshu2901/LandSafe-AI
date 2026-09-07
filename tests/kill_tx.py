from sqlalchemy import create_engine, text
from ml.feature_engineering.config import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' OR state = 'active' AND pid != pg_backend_pid()"))
    conn.commit()
print("Done")
