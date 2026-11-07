
from decimal import Decimal
import pytest
from app.calculate import calculate_totals
from app.validate import validate_quotation
from pathlib import Path
import json

def test_calculation_vat_excluded():
    result = calculate_totals(
        [{"description": "A", "quantity": 2, "unit_price": 100}],
        discount=0, vat_rate=7, vat_included=False
    )
    assert result["subtotal"] == Decimal("200.00")
    assert result["vat_amount"] == Decimal("14.00")
    assert result["grand_total"] == Decimal("214.00")

def test_discount_cannot_exceed_subtotal():
    with pytest.raises(ValueError):
        calculate_totals(
            [{"description": "A", "quantity": 1, "unit_price": 100}],
            discount=101
        )

def test_example_matches_schema():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "examples" / "quotation.json").read_text(encoding="utf-8"))
    assert validate_quotation(data)
