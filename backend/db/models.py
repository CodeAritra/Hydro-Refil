"""
RTRWH Platform — Database Models
=================================
SQLAlchemy ORM models for persisting assessment records, site inputs,
and calculated hydrological evaluation results.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AssessmentModel(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    site_name = Column(String(255), nullable=False, index=True)
    assessor_name = Column(String(255), nullable=True, default="Field Assessor")
    organization = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)

    # Core scalar fields for quick indexing & listing
    roof_area_m2 = Column(Float, nullable=False, default=0.0)
    annual_rainfall_mm = Column(Float, nullable=False, default=0.0)
    annual_harvestable_m3 = Column(Float, nullable=False, default=0.0)
    recommended_structure = Column(String(100), nullable=True)
    feasibility_label = Column(String(50), nullable=True)

    # Structured JSON payloads
    location_data = Column(JSON, nullable=False, default=dict)
    roof_data = Column(JSON, nullable=False, default=dict)
    rainfall_data = Column(JSON, nullable=False, default=dict)
    demand_data = Column(JSON, nullable=False, default=dict)
    site_data = Column(JSON, nullable=False, default=dict)
    calculation_results = Column(JSON, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
