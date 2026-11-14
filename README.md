# BOM Costing and Procurement Engine

**Project Code:** ECE-047  
**Team ID:** E009  
**Team Members:** Dinesh G and Gagan Deep K  
**Section:** ECM A  
**Programming Language:** Python 3.10+

---

## 1. Project Overview

The BOM Costing and Procurement Engine is a command-file-driven Python application that calculates the material requirements and procurement costs for manufacturing products.

The system reads Bill of Materials (BOM), parts, vendor and vendor-offer information from CSV files. It calculates the required quantity of each component, determines the order quantity based on vendor pack sizes, evaluates vendor price breaks and selects the most suitable eligible vendor.

It also calculates taxes, customs duty, freight and other applicable procurement charges.

The system generates three output reports:

- `costed_bom.csv`
- `po_summary.csv`
- `product_cost.csv`

## 2. Project Objectives

- Calculate component quantities based on production requirements.
- Apply attrition to passive components.
- Calculate order quantities using vendor pack sizes.
- Select eligible vendors based on delivery deadlines.
- Apply vendor price breaks.
- Calculate domestic and import procurement costs.
- Generate purchase order summaries.
- Identify components that have no eligible vendor.
- Generate structured CSV reports.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CSV | Input and output data storage |
| Decimal | Accurate financial calculations |
| unittest | Automated testing |
| Command Prompt | Running the application |
| Visual Studio Code | Development environment |

## 4. Project Folder Structure

```text
E009-ECE-047/
│
├── data/
│   ├── parts.csv
│   ├── boms.csv
│   ├── vendors.csv
│   ├── vendor_offers.csv
│   └── commands.txt
│
├── src/
│   ├── main.py
│   ├── data_loader.py
│   ├── cost_engine.py
│   └── procurement.py
│
├── tests/
│   └── test_cost_engine.py
│
├── output/
│   ├── costed_bom.csv
│   ├── po_summary.csv
│   └── product_cost.csv
│
├── docs/
│
└── README.md
```

## 5. Business Rules and Calculations

### 5.1 Required Quantity

Required quantity is calculated using:

`Required Quantity = Quantity per Unit × Build Quantity`

For passive components with reference prefixes R, C and L, an additional 2% attrition is applied.

The final required quantity is rounded up to the next whole number.

### 5.2 Order Quantity

The order quantity is rounded up to the nearest multiple of the vendor's pack size.

`Order Quantity = Ceiling(Required Quantity / Pack Size) × Pack Size`

`Overage = Order Quantity - Required Quantity`

### 5.3 Vendor Price Break Selection

- Only price breaks whose minimum quantity is less than or equal to the order quantity are eligible.
- The largest eligible minimum quantity is selected.
- If the order quantity is below the first available price break, that vendor is ineligible.

### 5.4 Vendor Eligibility

A vendor is eligible only if its lead time does not exceed the required delivery time.

A vendor whose lead time is greater than the need-by days is excluded.

### 5.5 Vendor Selection

The system selects the vendor with the lowest landed line cost.

When landed costs are equal:

1. Domestic vendors are preferred over import vendors.
2. If origin is also equal, the vendor with the shorter lead time is preferred.

### 5.6 Domestic Procurement Charges

- GST: 18% of line value.
- Small-order charge: ₹250 when the domestic purchase order value is below ₹5,000.

### 5.7 Import Procurement Charges

- Basic Customs Duty: 10% of line value.
- IGST: 18% of line value plus customs duty.
- Freight: ₹400 per import vendor purchase order.

### 5.8 Rounding Rules

- Unit prices are maintained to 4 decimal places.
- Line totals are rounded to 2 decimal places.
- Per-unit landed cost is rounded to 2 decimal places.

### 5.9 No Eligible Vendor

If no vendor satisfies the eligibility requirements, the component receives the status `NO_SOURCE`.

The product is marked `INCOMPLETE` if any component has no eligible vendor.

## 6. Input Files

| File | Description |
|---|---|
| `parts.csv` | Contains component and part information |
| `boms.csv` | Contains product BOM information |
| `vendors.csv` | Contains vendor information |
| `vendor_offers.csv` | Contains vendor prices, pack sizes and price breaks |
| `commands.txt` | Contains data-loading and product-costing commands |

## 7. Command File

The application uses `commands.txt` to process product-costing requests.

Example:

```text
LOAD_PARTS|parts.csv
LOAD_BOMS|boms.csv
LOAD_VENDORS|vendors.csv|vendor_offers.csv
COST|PRD-A|1000|21
COST|PRD-B|250|7
COST|PRD-C|5000|30
COST|PRD-A|1|45
COST|PRD-C|100|7
```

Each COST command contains:

`COST | Product Code | Build Quantity | Need-by Days`

## 8. Output Files

### 8.1 costed_bom.csv

Contains component-level costing information, including:

- Required quantity
- Selected vendor
- Vendor origin
- Pack size
- Order quantity
- Overage
- Price break
- Unit price
- Line value
- Duty and tax
- Landed line cost
- Component status

### 8.2 po_summary.csv

Contains purchase-order-level information, including:

- Vendor code
- Origin
- Number of lines
- Purchase order value
- Small-order charge
- Duty
- Tax
- Freight
- Final purchase order total

### 8.3 product_cost.csv

Contains product-level information, including:

- Product code
- Build quantity
- Need-by days
- Total landed cost
- Per-unit landed cost
- Product status

## 9. How to Run the Project

### Prerequisites

- Windows operating system
- Python 3.10 or later
- Visual Studio Code (recommended)

### Step 1: Open the project folder

Open the project folder in Command Prompt or Visual Studio Code.

### Step 2: Run the application

From the project root directory, execute:

```bash
py src\main.py
```

### Step 3: Check generated reports

Open the `output` folder to view the generated CSV reports.

## 10. Running Automated Tests

The project uses Python's built-in `unittest` framework.

Run the following command from the project root directory:

```bash
py -m unittest discover -s tests -v
```

The test suite currently checks:

1. Exact price-break minimum eligibility.
2. Exact pack-size multiple calculation.
3. Domestic vendor preference when landed costs are equal.
4. Rejection of vendors that do not meet the delivery deadline.
5. Large pack-size handling for a build quantity of one.

**Current test result:** All 5 automated tests passed.

## 11. Error and Status Handling

- `NO_SOURCE`: No eligible vendor is available for the component.
- `INCOMPLETE`: At least one component in the product has no eligible vendor.
- `COMPLETE`: All required components have eligible vendors.

## 12. Conclusion

The BOM Costing and Procurement Engine automates material quantity calculations, vendor evaluation and procurement cost estimation.

By applying consistent business rules and generating structured CSV reports, the system helps make procurement decisions more systematic and transparent.

The project also includes automated tests to verify important quantity calculation and vendor-selection scenarios.
