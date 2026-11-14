
import csv
from pathlib import Path

from data_loader import load_csv
from procurement import calculate_product_cost


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================
# OUTPUT CSV CONFIGURATION
# ==========================================

COSTED_BOM_FIELDS = [
    "cost_no",
    "product_code",
    "build_qty",
    "part_number",
    "ref_prefix",
    "qty_per_unit",
    "required_qty",
    "vendor_code",
    "origin",
    "pack_size",
    "order_qty",
    "overage",
    "break_min_qty",
    "unit_price",
    "line_value",
    "duty",
    "tax",
    "line_landed_cost",
    "status"
]

PO_FIELDS = [
    "cost_no",
    "product_code",
    "vendor_code",
    "origin",
    "line_count",
    "po_value",
    "small_order_charge",
    "duty",
    "tax",
    "freight",
    "po_total"
]

PRODUCT_FIELDS = [
    "cost_no",
    "product_code",
    "build_qty",
    "need_by_days",
    "total_landed_cost",
    "per_unit_landed_cost",
    "status"
]


# ==========================================
# SAVE CSV FILE
# ==========================================

def save_csv(filename, fieldnames, rows):

    file_path = OUTPUT_DIR / filename

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Generated:", file_path)


# ==========================================
# PROCESS COMMAND FILE
# ==========================================

def run_project():

    print("\n========================================")
    print(" ECE-047 BOM COSTING AND PROCUREMENT ENGINE")
    print("========================================")

    print("Loading project data...")

    parts = load_csv("parts.csv")
    boms = load_csv("boms.csv")
    vendor_rows = load_csv("vendors.csv")
    offers = load_csv("vendor_offers.csv")

    vendors = {
        vendor["vendor_code"]: vendor
        for vendor in vendor_rows
    }

    print("Parts:", len(parts))
    print("BOM entries:", len(boms))
    print("Vendors:", len(vendors))
    print("Vendor offers:", len(offers))

    # Store all generated results
    all_costed_rows = []
    all_po_rows = []
    all_product_rows = []

    command_file = DATA_DIR / "commands.txt"

    if not command_file.exists():
        raise FileNotFoundError(
            "commands.txt was not found in the data folder."
        )

    cost_no = 0

    print("\nProcessing commands...")

    with open(
        command_file,
        "r",
        encoding="utf-8-sig"
    ) as file:

        for line_number, raw_line in enumerate(file, start=1):

            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            fields = line.split("|")
            command = fields[0].strip().upper()

            if command in (
                "LOAD_PARTS",
                "LOAD_BOMS",
                "LOAD_VENDORS"
            ):
                print(
                    f"Line {line_number}: {command} completed."
                )
                continue

            if command == "COST":

                if len(fields) != 4:
                    raise ValueError(
                        f"Invalid COST command on line {line_number}"
                    )

                product_code = fields[1].strip()
                build_qty = int(fields[2])
                need_by_days = int(fields[3])

                if build_qty <= 0 or need_by_days < 0:
                    raise ValueError(
                        f"Invalid quantity or delivery time "
                        f"on line {line_number}"
                    )

                cost_no += 1

                print(
                    f"\nCOST {cost_no}: {product_code} | "
                    f"Build: {build_qty} | "
                    f"Need by: {need_by_days} days"
                )

                costed_rows, po_rows, product_row = (
                    calculate_product_cost(
                        cost_no=cost_no,
                        product_code=product_code,
                        build_qty=build_qty,
                        need_by_days=need_by_days,
                        boms=boms,
                        offers=offers,
                        vendors=vendors
                    )
                )

                all_costed_rows.extend(costed_rows)
                all_po_rows.extend(po_rows)
                all_product_rows.append(product_row)

                print(
                    "Status:",
                    product_row["status"]
                )

                print(
                    "Total landed cost: Rs.",
                    product_row["total_landed_cost"]
                )

                print(
                    "Per-unit landed cost: Rs.",
                    product_row["per_unit_landed_cost"]
                )

            else:
                raise ValueError(
                    f"Unknown command '{command}' "
                    f"on line {line_number}"
                )

    # Generate all three output files
    print("\nGenerating output reports...")

    save_csv(
        "costed_bom.csv",
        COSTED_BOM_FIELDS,
        all_costed_rows
    )

    save_csv(
        "po_summary.csv",
        PO_FIELDS,
        all_po_rows
    )

    save_csv(
        "product_cost.csv",
        PRODUCT_FIELDS,
        all_product_rows
    )

    print("\n========================================")
    print(" PROJECT EXECUTION COMPLETED")
    print("========================================")
    print("Products processed:", len(all_product_rows))
    print("BOM cost lines:", len(all_costed_rows))
    print("Purchase orders:", len(all_po_rows))
    print("Reports saved in the output folder.")


# ==========================================
# PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":

    try:
        run_project()

    except Exception as error:

        print("\nPROJECT EXECUTION FAILED")
        print("Error:", error)
