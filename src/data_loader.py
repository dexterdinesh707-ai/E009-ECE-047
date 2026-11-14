
import csv
from pathlib import Path

# Find the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Find the data folder
DATA_DIR = PROJECT_DIR / "data"


def load_csv(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return list(reader)


# Load the four actual assignment files
parts = load_csv("parts.csv")
boms = load_csv("boms.csv")
vendors = load_csv("vendors.csv")
vendor_offers = load_csv("vendor_offers.csv")

print("===== ECE-047 DATA LOADER =====")

print("Parts loaded:", len(parts))
print("BOM entries loaded:", len(boms))
print("Vendors loaded:", len(vendors))
print("Vendor offers loaded:", len(vendor_offers))

print("===============================")
print("Data loading completed!")
