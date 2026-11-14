# System Design Document
## BOM Costing and Procurement Engine

**Project Code:** ECE-047  
**Team ID:** E009  
**Team Members:** Dinesh G and Gagan Deep K  
**Section:** ECM A  
**Programming Language:** Python

---

## 1. Introduction

The BOM Costing and Procurement Engine is a Python-based application designed to calculate material requirements and procurement costs for manufacturing products.

The system processes input data from CSV files, evaluates vendor offers, calculates procurement charges and generates cost reports.

The application follows a command-file-driven approach and does not require a graphical user interface.

## 2. System Architecture

The application is divided into four major Python modules:

1. `main.py`
2. `data_loader.py`
3. `cost_engine.py`
4. `procurement.py`

Each module performs a specific responsibility.

## 3. Module Description

### 3.1 Main Module (`main.py`)

The main module controls the overall execution of the application.

Responsibilities:

- Reads the command file.
- Loads the required input data.
- Processes product-costing commands.
- Calls the procurement calculation functions.
- Generates the output CSV reports.

### 3.2 Data Loader Module (`data_loader.py`)

The data loader module reads the input CSV files.

Input files:

- `parts.csv`
- `boms.csv`
- `vendors.csv`
- `vendor_offers.csv`

It converts the CSV records into Python data structures that can be used by the other modules.

### 3.3 Cost Engine Module (`cost_engine.py`)

The cost engine contains the core quantity and vendor-selection calculations.

Responsibilities:

- Calculates required component quantities.
- Applies 2% attrition to passive components with R, C and L reference prefixes.
- Calculates order quantities based on vendor pack sizes.
- Calculates overage.
- Selects eligible price breaks.
- Filters vendors based on lead-time requirements.
- Compares landed costs.
- Applies the domestic and lead-time tie-breaking rules.

### 3.4 Procurement Module (`procurement.py`)

The procurement module handles component-level and product-level costing.

Responsibilities:

- Calculates component procurement costs.
- Calculates line values, duty and taxes.
- Groups component costs by vendor.
- Calculates purchase-order charges.
- Calculates total product landed cost.
- Determines product completion status.

## 4. System Data Flow

The application follows this sequence:

1. Read input CSV files.
2. Read commands from `commands.txt`.
3. Identify the product, build quantity and need-by days.
4. Retrieve the relevant BOM components.
5. Calculate required quantities.
6. Evaluate available vendor offers.
7. Select the best eligible vendor for each component.
8. Calculate component-level procurement costs.
9. Group selected components into vendor purchase orders.
10. Calculate purchase-order totals.
11. Calculate product-level landed cost.
12. Generate the three output CSV reports.

## 5. Calculation Design

### 5.1 Required Quantity Calculation

The required quantity is calculated as:

`Required Quantity = Quantity per Unit × Build Quantity`

For passive components with reference prefixes R, C and L, 2% attrition is applied.

The result is rounded up to the next whole number.

### 5.2 Order Quantity Calculation

The order quantity is rounded up to a multiple of the vendor pack size.

`Order Quantity = Ceiling(Required Quantity / Pack Size) × Pack Size`

`Overage = Order Quantity - Required Quantity`

### 5.3 Price Break Selection

The system checks the available price breaks for each vendor.

It selects the highest break minimum quantity that does not exceed the calculated order quantity.

If no price break is eligible, that vendor is excluded.

### 5.4 Vendor Selection

The system first excludes vendors whose lead time exceeds the need-by days.

It then calculates the landed line cost for each eligible vendor.

The vendor with the lowest landed line cost is selected.

Tie-breaking rules:

1. Domestic vendor is preferred when landed costs are equal.
2. Shorter lead time is preferred when origin is also equal.

## 6. Procurement Cost Design

### 6.1 Domestic Procurement

Domestic procurement includes:

- 18% GST on line value.
- ₹250 small-order charge when the purchase order value is below ₹5,000.

### 6.2 Import Procurement

Import procurement includes:

- 10% basic customs duty on line value.
- 18% IGST on line value plus customs duty.
- ₹400 freight per vendor purchase order.

### 6.3 Rounding

The system uses Python's `Decimal` type for financial calculations.

- Unit prices: 4 decimal places.
- Line totals: 2 decimal places.
- Per-unit landed cost: 2 decimal places.

## 7. Output Design

The application generates three CSV reports.

### 7.1 Costed BOM Report

File: `costed_bom.csv`

Contains component-level information, including required quantity, vendor selection, order quantity, overage, price break, unit price, taxes, duty, landed line cost and status.

### 7.2 Purchase Order Summary

File: `po_summary.csv`

Contains vendor-level purchase order information, including line count, purchase order value, applicable charges and final purchase order total.

### 7.3 Product Cost Report

File: `product_cost.csv`

Contains product-level information, including build quantity, need-by days, total landed cost, per-unit landed cost and product status.

## 8. Status Handling

The system uses the following statuses:

| Status | Meaning |
|---|---|
| `NO_SOURCE` | No eligible vendor is available for a component |
| `INCOMPLETE` | At least one component has no eligible vendor |
| `COMPLETE` | All required components have eligible vendors |

## 9. Testing Design

The project uses Python's built-in `unittest` framework.

The current automated test suite covers:

1. Exact price-break minimum eligibility.
2. Exact pack-size multiple calculation.
3. Domestic preference when landed costs are equal.
4. Vendor rejection when delivery deadlines cannot be met.
5. Large pack-size handling for a build quantity of one.

All five current automated tests have passed.

## 10. Conclusion

The system separates data loading, quantity calculations, vendor selection and procurement costing into individual modules.

This modular structure makes the application easier to understand, test and maintain.

The generated reports provide component-level, vendor-level and product-level procurement cost information.
