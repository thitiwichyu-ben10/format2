
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

def money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)

def calculate_totals(items, discount=0, vat_rate=7, vat_included=False):
    """Calculate totals deterministically. discount is a document-level THB amount."""
    subtotal = Decimal("0.00")
    normalized_items = []

    for item in items:
        qty = Decimal(str(item["quantity"]))
        unit_price = Decimal(str(item["unit_price"]))
        amount = money(qty * unit_price)
        subtotal += amount
        normalized_items.append({**item, "amount": amount})

    subtotal = money(subtotal)
    discount = money(discount)
    if discount < 0 or discount > subtotal:
        raise ValueError("ส่วนลดต้องอยู่ระหว่าง 0 ถึงยอดก่อนหักส่วนลด")

    taxable = money(subtotal - discount)
    rate = Decimal(str(vat_rate)) / Decimal("100")

    if vat_included:
        # Prices already include VAT. Extract VAT from the discounted gross amount.
        grand_total = taxable
        vat_amount = money(taxable - (taxable / (Decimal("1") + rate)))
        before_vat = money(taxable - vat_amount)
    else:
        before_vat = taxable
        vat_amount = money(before_vat * rate)
        grand_total = money(before_vat + vat_amount)

    return {
        "items": normalized_items,
        "subtotal": subtotal,
        "discount": discount,
        "before_vat": before_vat,
        "vat_rate": money(vat_rate),
        "vat_amount": vat_amount,
        "grand_total": money(grand_total),
    }
