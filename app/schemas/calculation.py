"""This module provides a validation schema for IO data related to the calculation model"""
import pydantic as pyd

from enum import Enum
from datetime import datetime
from uuid import UUID
from typing import Optional

class CalculationForm(pyd.BaseModel):
    """Schema for incoming Calculation forms from the UI"""
    a: float
    b: float
    calc_type: str

    model_config = pyd.ConfigDict(from_attributes=True)

class CalculationRecord(pyd.BaseModel):
    """Schema for outgoing Calculation records from the database"""
    id: UUID
    user_id: UUID
    type: str
    inputs: list
    created_at: datetime
    updated_at: datetime

    model_config = pyd.ConfigDict(from_attributes=True)


