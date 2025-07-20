"""This module provides a test swuite for the Calculation object family"""

import logging as logs
import pytest

from sqlalchemy.exc import IntegrityError
from uuid import uuid4

from app.models.calculation import Calculation
from app.models.user import User
from tests.conftest import managed_db_session

logger = logs.getLogger(__name__)

def test_calculation_properties(test_user, db_session):
    """
    Verifies basic creation and deletion cascade functionality
    - Create a single calculation associated with a user and verify its fields
    - Delete the associated user and verify cascade deletion
    """
    new_calc = Calculation.create(
        "addition",
        user_id=test_user.id,
        inputs=[1, 2]
    )
    db_session.add(new_calc)
    db_session.commit()
    
    user_record = db_session.query(User).filter_by(email=test_user.email).first()
    calc_record = db_session.query(Calculation).filter_by(user_id=test_user.id).first()
    assert calc_record is not None, \
        "test_calculation_properties failure: new_calc not inserted"
    assert calc_record.user_id == user_record.id
    assert calc_record.type == 'addition'
    assert 1 in calc_record.inputs
    assert 2 in calc_record.inputs

    db_session.delete(test_user)
    db_session.commit()

    calc_record = db_session.query(Calculation).filter_by(id=calc_record.id).first()
    assert calc_record is None, \
        "test_calculation_properties failure: calc_record delete cascade failed"
    
def test_calculation_foreign_key_constraint(test_user, db_session):
    """Tests error handling in cases of incorrect/missing user relations"""
    db_session.delete(test_user)
    db_session.commit()
    new_calc = Calculation.create(
        "addition",
        user_id=test_user.id,
        inputs=[1, 2]
    )
    db_session.add(new_calc)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

# ===================================================================
# Factory Testing
# ===================================================================

def test_calculation_create_unsupported_type(test_user):
    """Tests error handling in cases of invalid type input"""
    with pytest.raises(ValueError, match="Unsupported calculation type: bad_type"):
        Calculation.create(
            "bad_type", 
            user_id=test_user.id,
            inputs=[1, 2]
        )

def test_calculation_create_short_inputs(test_user):
    """Tests error handling in cases of invalid operand inputs"""
    with pytest.raises(ValueError, match="addition requires at least 2 operands"):
        Calculation.create(
            "addition",
            user_id=test_user.id,
            inputs=[0]
        )

def test_bad_registration():
    """Tests error handling in cases of faulty class registration"""
    class BadCalcClass():
        pass
    with pytest.raises(TypeError, match="Registered class must inherit from Calculation"):
        Calculation.register(BadCalcClass)

def test_calculation_repr(test_user):
    """Tests the __repr__ function's label format"""
    new_calc = Calculation.create(
        "Addition",
        user_id=test_user.id,
        inputs=[1, 2]
    )
    assert str(new_calc) == "<Calculation(type=addition, inputs=[1, 2])>"

@pytest.mark.parametrize(
    "calc_type, inputs, expected", [
        ("Addition", [1, 2], 3),
        ("Subtraction", [3, 2], 1),
        ("Multiplication", [2, 3], 6),
        ("Division", [6, 3], 2),
        ("Modulus", [6, 3], 0),
    ],
    ids=[
        "get_add_result",
        "get_subtract_result",
        "get_multiply_result",
        "get_divide_result",
        "get_modulo_result",
    ]
)
def test_calculation_get_result(calc_type: str, inputs: list[float], expected: float, test_user):
    """Verifies a basic get_result case for each Calculation subtype"""
    new_calc = Calculation.create(
        calc_type,
        user_id=test_user.id,
        inputs=inputs
    )
    assert new_calc.get_result() == expected, \
        f"test_calculation_get_result failed for {str(new_calc)}"

@pytest.mark.parametrize(
    "calc_type, tag", [
        ("Division", "Division"),
        ("Modulus", "Modulo Division"),
    ]
)
def test_zero_divisor_handling(calc_type: str, tag: str, test_user):
    """Tests zero divisor handling with appropriate calculation types"""
    new_calc = Calculation.create(
        calc_type,
        user_id=test_user.id,
        inputs=[12, 2, 0, 2]
    )
    with pytest.raises(ValueError, match=f"Zero divisor input invalid for {tag}"):
        new_calc.get_result()
