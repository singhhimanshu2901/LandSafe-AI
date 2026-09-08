import pandas as pd
import os
from sqlalchemy import create_engine

from ml.feature_engineering.config import get_db_url

_engine = None

def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine(get_db_url())
    return _engine


def load_weather(date_from=None, date_to=None):
    q = "SELECT * FROM weather_observations WHERE 1=1"
    if date_from:
        q += f" AND timestamp >= '{date_from}'"
    if date_to:
        q += f" AND timestamp <= '{date_to}'"
    return pd.read_sql(q, get_engine())


def load_sensors(date_from=None, date_to=None):
    q = "SELECT * FROM sensor_readings WHERE 1=1"
    if date_from:
        q += f" AND timestamp >= '{date_from}'"
    if date_to:
        q += f" AND timestamp <= '{date_to}'"
    df = pd.read_sql(q, get_engine())
    return df


def load_locations(location_ids=None):
    q = "SELECT id, district, village, elevation, slope, ST_X(geometry::geometry) as lon, ST_Y(geometry::geometry) as lat FROM locations"
    if location_ids:
        ids = ",".join(f"'{i}'" for i in location_ids)
        q += f" WHERE id IN ({ids})"
    return pd.read_sql(q, get_engine())


def load_landslide_events():
    q = "SELECT id, ST_X(geometry::geometry) as lon, ST_Y(geometry::geometry) as lat, event_time, verification_status FROM landslide_events"
    df = pd.read_sql(q, get_engine())
    return df
