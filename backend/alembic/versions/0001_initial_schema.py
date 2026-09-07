"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("district", sa.String()),
        sa.Column("village", sa.String()),
        sa.Column("elevation", sa.Float()),
        sa.Column("slope", sa.Float()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "weather_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("rainfall", sa.Float()),
        sa.Column("temperature", sa.Float()),
        sa.Column("humidity", sa.Float()),
        sa.Column("source", sa.String()),
    )

    op.create_table(
        "sensor_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sensor_id", sa.String(), nullable=False, index=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("soil_moisture", sa.Float()),
        sa.Column("battery", sa.Float()),
        sa.Column("quality", sa.String()),
    )

    op.create_table(
        "landslide_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("event_time", sa.DateTime(), nullable=False),
        sa.Column("severity", sa.String()),
        sa.Column("source", sa.String()),
        sa.Column("verification_status", sa.String()),
    )

    op.create_table(
        "risk_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("probability", sa.Float()),
        sa.Column("score", sa.Float()),
        sa.Column("level", sa.String()),
        sa.Column("model_version", sa.String()),
    )

    op.create_table(
        "infrastructure",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("type", sa.String()),
        sa.Column("name", sa.String()),
        sa.Column("importance", sa.String()),
    )

    op.create_table(
        "roads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="LINESTRING", srid=4326)),
        sa.Column("road_type", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("last_updated", sa.DateTime()),
    )

    op.create_table(
        "field_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POINT", srid=4326)),
        sa.Column("category", sa.String()),
        sa.Column("severity", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("media_ref", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("risk_prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_predictions.id")),
        sa.Column("audience", sa.String()),
        sa.Column("channel", sa.String()),
        sa.Column("template", sa.String()),
        sa.Column("sent_at", sa.DateTime()),
        sa.Column("delivery_status", sa.String()),
    )


def downgrade():
    op.drop_table("alerts")
    op.drop_table("field_reports")
    op.drop_table("roads")
    op.drop_table("infrastructure")
    op.drop_table("risk_predictions")
    op.drop_table("landslide_events")
    op.drop_table("sensor_readings")
    op.drop_table("weather_observations")
    op.drop_table("locations")
