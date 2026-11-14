
import math
from decimal import Decimal


def calculate_required_quantity(qty_per_unit, build_qty, ref_prefix):
    """
    Calculate required quantity with 2% attrition
    for passive components R, C and L.
    """

    required = qty_per_unit * build_qty

    if ref_prefix in ("R", "C", "L"):
        required = required * 1.02

    return math.ceil(required)


def calculate_order_quantity(required_qty, pack_size):
    """
    Round required quantity up to a complete vendor pack.
    """

    order_qty = math.ceil(required_qty / pack_size) * pack_size
    overage = order_qty - required_qty

    return order_qty, overage


def select_price_break(offers, order_qty):
    """
    Select the largest price-break minimum
    that does not exceed the order quantity.
    """

    eligible_breaks = [
        offer for offer in offers
        if int(offer["break_min_qty"]) <= order_qty
    ]

    if not eligible_breaks:
        return None

    return max(
        eligible_breaks,
        key=lambda offer: int(offer["break_min_qty"])
    )


def select_best_vendor(
    offers, vendors, part_number, required_qty, need_by_days
):
    """
    Select the best eligible vendor for one part.

    Rules:
    1. Exclude vendors whose lead time exceeds need-by days.
    2. Exclude offers that do not meet a price break.
    3. Compare landed unit costs.
    4. On a tie, prefer DOMESTIC.
    5. If still tied, prefer shorter lead time.
    """

    candidates = []

    # Get all offers for the required part
    part_offers = [
        offer for offer in offers
        if offer["part_number"] == part_number
    ]

    # Identify vendors offering this part
    vendor_codes = set(
        offer["vendor_code"] for offer in part_offers
    )

    for vendor_code in vendor_codes:

        vendor_offers = [
            offer for offer in part_offers
            if offer["vendor_code"] == vendor_code
        ]

        vendor = vendors.get(vendor_code)

        if vendor is None:
            continue

        # Check vendor lead time
        lead_time = int(vendor_offers[0]["lead_time_days"])

        if lead_time > need_by_days:
            continue

        # Calculate order quantity using vendor pack size
        pack_size = int(vendor_offers[0]["pack_size"])

        order_qty, overage = calculate_order_quantity(
            required_qty, pack_size
        )

        # Select applicable price break
        selected_offer = select_price_break(
            vendor_offers, order_qty
        )

        if selected_offer is None:
            continue

        unit_price = Decimal(selected_offer["unit_price"])
        origin = vendor["origin"]

        # Calculate landed unit cost before order-level charges
        if origin == "DOMESTIC":

            landed_unit_cost = (
                unit_price * Decimal("1.18")
            )

        elif origin == "IMPORT":

            duty = unit_price * Decimal("0.10")

            landed_unit_cost = (
                unit_price + duty
            ) * Decimal("1.18")

        else:
            continue

        candidates.append({
            "vendor_code": vendor_code,
            "origin": origin,
            "lead_time_days": lead_time,
            "pack_size": pack_size,
            "order_qty": order_qty,
            "overage": overage,
            "break_min_qty": int(
                selected_offer["break_min_qty"]
            ),
            "unit_price": unit_price,
            "landed_unit_cost": landed_unit_cost,
            "offer": selected_offer
        })

    if not candidates:
        return None

    # Sort by landed cost, origin preference and lead time
    candidates.sort(
        key=lambda item: (
            item["landed_unit_cost"],
            0 if item["origin"] == "DOMESTIC" else 1,
            item["lead_time_days"]
        )
    )

    return candidates[0]


# ==========================================
# TEST THE VENDOR SELECTION FUNCTION
# ==========================================

if __name__ == "__main__":

    from data_loader import load_csv

    # Load actual project CSV files
    offers = load_csv("vendor_offers.csv")
    vendor_rows = load_csv("vendors.csv")

    # Convert vendor list into a dictionary
    vendors = {
        vendor["vendor_code"]: vendor
        for vendor in vendor_rows
    }

    # Test required quantity calculation
    required = calculate_required_quantity(5, 1000, "C")

    print("\n===== QUANTITY CALCULATION TEST =====")
    print("Required quantity:", required)

    # Test vendor selection
    result = select_best_vendor(
        offers=offers,
        vendors=vendors,
        part_number="PRT-003",
        required_qty=100,
        need_by_days=30
    )

    print("\n===== VENDOR SELECTION TEST =====")

    if result is None:
        print("No eligible vendor found.")

    else:
        print("Selected vendor:", result["vendor_code"])
        print("Origin:", result["origin"])
        print("Lead time:", result["lead_time_days"], "days")
        print("Order quantity:", result["order_qty"])
        print("Overage:", result["overage"])
        print("Unit price:", result["unit_price"])
        print("Landed unit cost:", result["landed_unit_cost"])

    print("\n===== TEST COMPLETED =====")
