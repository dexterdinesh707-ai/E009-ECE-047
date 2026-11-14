
import sys
import unittest
from pathlib import Path
from decimal import Decimal

# Allow tests to import files from the src folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from cost_engine import (
    calculate_required_quantity,
    calculate_order_quantity,
    select_price_break,
    select_best_vendor,
)


class TestCostEngine(unittest.TestCase):

    # Test 1: Exact price-break minimum must be eligible
    def test_exact_price_break_minimum(self):
        offers = [
            {"break_min_qty": "1000", "unit_price": "10.0000"},
            {"break_min_qty": "2000", "unit_price": "9.0000"},
        ]

        selected = select_price_break(offers, 1000)

        self.assertIsNotNone(selected)
        self.assertEqual(int(selected["break_min_qty"]), 1000)

    # Test 2: Exact pack multiple must not create overage
    def test_exact_pack_multiple(self):
        order_qty, overage = calculate_order_quantity(10000, 5000)

        self.assertEqual(order_qty, 10000)
        self.assertEqual(overage, 0)

    # Test 3: Domestic vendor wins an equal landed-cost comparison
    def test_domestic_wins_equal_landed_cost(self):
        offers = [
            {
                "part_number": "PRT-TEST",
                "vendor_code": "DOM-01",
                "lead_time_days": "10",
                "pack_size": "1",
                "break_min_qty": "1",
                "unit_price": "110.0000",
            },
            {
                "part_number": "PRT-TEST",
                "vendor_code": "IMP-01",
                "lead_time_days": "3",
                "pack_size": "1",
                "break_min_qty": "1",
                "unit_price": "100.0000",
            },
        ]

        vendors = {
            "DOM-01": {"origin": "DOMESTIC"},
            "IMP-01": {"origin": "IMPORT"},
        }

        result = select_best_vendor(
            offers, vendors, "PRT-TEST", 1, 30
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["vendor_code"], "DOM-01")

    # Test 4: Vendors with excessive lead time must be excluded
    def test_no_vendor_meets_deadline(self):
        offers = [
            {
                "part_number": "PRT-TEST",
                "vendor_code": "VND-01",
                "lead_time_days": "10",
                "pack_size": "1",
                "break_min_qty": "1",
                "unit_price": "10.0000",
            }
        ]

        vendors = {
            "VND-01": {"origin": "DOMESTIC"},
        }

        result = select_best_vendor(
            offers, vendors, "PRT-TEST", 1, 7
        )

        self.assertIsNone(result)

    # Test 5: Build quantity 1 with pack size 5000
    def test_build_quantity_one_large_pack(self):
        required_qty = calculate_required_quantity(1, 1, "U")

        order_qty, overage = calculate_order_quantity(
            required_qty, 5000
        )

        self.assertEqual(required_qty, 1)
        self.assertEqual(order_qty, 5000)
        self.assertEqual(overage, 4999)


if __name__ == "__main__":
    unittest.main(verbosity=2)
