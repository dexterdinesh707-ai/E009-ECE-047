
from decimal import Decimal, ROUND_HALF_UP

from cost_engine import (
    calculate_required_quantity,
    select_best_vendor
)


# ==========================================
# MONEY AND ROUNDING HELPERS
# ==========================================

ZERO = Decimal("0.00")
GST_RATE = Decimal("0.18")
IMPORT_DUTY_RATE = Decimal("0.10")
IMPORT_FREIGHT = Decimal("400.00")
SMALL_ORDER_CHARGE = Decimal("250.00")
SMALL_ORDER_LIMIT = Decimal("5000.00")


def money(value):
    """Round money to two decimal places."""

    return Decimal(value).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# ==========================================
# COST ONE BOM COMPONENT
# ==========================================

def calculate_component_cost(
    bom_row,
    build_qty,
    need_by_days,
    offers,
    vendors
):
    """Calculate the cost and vendor for one BOM component."""

    part_number = bom_row["part_number"]
    qty_per_unit = Decimal(bom_row["qty_per_unit"])
    ref_prefix = bom_row["ref_prefix"]

    required_qty = calculate_required_quantity(
        float(qty_per_unit),
        build_qty,
        ref_prefix
    )

    selected = select_best_vendor(
        offers=offers,
        vendors=vendors,
        part_number=part_number,
        required_qty=required_qty,
        need_by_days=need_by_days
    )

    if selected is None:
        return {
            "part_number": part_number,
            "ref_prefix": ref_prefix,
            "qty_per_unit": qty_per_unit,
            "required_qty": required_qty,
            "vendor_code": "",
            "origin": "",
            "pack_size": "",
            "order_qty": "",
            "overage": "",
            "break_min_qty": "",
            "unit_price": "",
            "line_value": ZERO,
            "duty": ZERO,
            "tax": ZERO,
            "line_landed_cost": ZERO,
            "status": "NO_SOURCE"
        }

    order_qty = selected["order_qty"]
    unit_price = selected["unit_price"]
    origin = selected["origin"]

    # Total value of the ordered components
    line_value = money(
        Decimal(order_qty) * unit_price
    )

    # Calculate domestic GST or import duty and IGST
    if origin == "DOMESTIC":

        duty = ZERO
        tax = money(line_value * GST_RATE)

    else:

        duty = money(line_value * IMPORT_DUTY_RATE)

        taxable_value = line_value + duty

        tax = money(taxable_value * GST_RATE)

    line_landed_cost = money(
        line_value + duty + tax
    )

    return {
        "part_number": part_number,
        "ref_prefix": ref_prefix,
        "qty_per_unit": qty_per_unit,
        "required_qty": required_qty,
        "vendor_code": selected["vendor_code"],
        "origin": origin,
        "pack_size": selected["pack_size"],
        "order_qty": order_qty,
        "overage": selected["overage"],
        "break_min_qty": selected["break_min_qty"],
        "unit_price": unit_price,
        "line_value": line_value,
        "duty": duty,
        "tax": tax,
        "line_landed_cost": line_landed_cost,
        "status": "OK"
    }


# ==========================================
# PROCESS ONE PRODUCT COST COMMAND
# ==========================================

def calculate_product_cost(
    cost_no,
    product_code,
    build_qty,
    need_by_days,
    boms,
    offers,
    vendors
):
    """Calculate all BOM component costs for one product."""

    product_boms = [
        row for row in boms
        if row["product_code"] == product_code
    ]

    if not product_boms:
        raise ValueError(
            f"No BOM entries found for {product_code}"
        )

    costed_rows = []

    for bom_row in product_boms:

        result = calculate_component_cost(
            bom_row=bom_row,
            build_qty=build_qty,
            need_by_days=need_by_days,
            offers=offers,
            vendors=vendors
        )

        result["cost_no"] = cost_no
        result["product_code"] = product_code
        result["build_qty"] = build_qty

        costed_rows.append(result)

    # Group successfully sourced lines by vendor
    vendor_groups = {}

    for row in costed_rows:

        if row["status"] != "OK":
            continue

        vendor_code = row["vendor_code"]

        vendor_groups.setdefault(
            vendor_code, []
        ).append(row)

    po_rows = []
    total_landed_cost = ZERO

    # Calculate each vendor purchase order
    for vendor_code, rows in vendor_groups.items():

        origin = rows[0]["origin"]

        po_value = money(sum(
            (row["line_value"] for row in rows),
            Decimal("0")
        ))

        duty = money(sum(
            (row["duty"] for row in rows),
            Decimal("0")
        ))

        tax = money(sum(
            (row["tax"] for row in rows),
            Decimal("0")
        ))

        small_order_charge = ZERO
        freight = ZERO

        if origin == "DOMESTIC":

            if po_value < SMALL_ORDER_LIMIT:
                small_order_charge = SMALL_ORDER_CHARGE

        else:

            # Import freight is charged once per vendor order
            freight = IMPORT_FREIGHT

        po_total = money(
            po_value
            + duty
            + tax
            + small_order_charge
            + freight
        )

        po_rows.append({
            "cost_no": cost_no,
            "product_code": product_code,
            "vendor_code": vendor_code,
            "origin": origin,
            "line_count": len(rows),
            "po_value": po_value,
            "small_order_charge": small_order_charge,
            "duty": duty,
            "tax": tax,
            "freight": freight,
            "po_total": po_total
        })

        total_landed_cost += po_total

    # Any unsourced component makes the product incomplete
    incomplete = any(
        row["status"] == "NO_SOURCE"
        for row in costed_rows
    )

    total_landed_cost = money(total_landed_cost)

    if incomplete:
        product_status = "INCOMPLETE"
        per_unit_cost = ZERO
    else:
        product_status = "COMPLETE"

        per_unit_cost = money(
            total_landed_cost / Decimal(build_qty)
        )

    product_row = {
        "cost_no": cost_no,
        "product_code": product_code,
        "build_qty": build_qty,
        "need_by_days": need_by_days,
        "total_landed_cost": total_landed_cost,
        "per_unit_landed_cost": per_unit_cost,
        "status": product_status
    }

    return costed_rows, po_rows, product_row
