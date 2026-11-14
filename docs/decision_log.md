# Decision Log
## BOM Costing and Procurement Engine

**Project Code:** ECE-047  
**Team ID:** E009  
**Programming Language:** Python

---

## 1. Purpose

This decision log records the important technical and business-rule decisions made during the development of the BOM Costing and Procurement Engine.

It explains the selected technologies, calculation methods and vendor-selection approach.

## 2. Technical Decisions

### Decision 1: Use Python

**Decision:** Python was selected as the programming language.

**Reason:**
- Python has a simple and readable syntax.
- It provides built-in CSV processing support.
- It supports modular programming.
- It provides the `Decimal` module for financial calculations.
- It includes the `unittest` framework for automated testing.

### Decision 2: Use CSV Files for Data Storage

**Decision:** CSV files were selected for input and output data.

**Reason:**
- CSV files are easy to read and maintain.
- They can be processed using Python's built-in CSV module.
- They provide a simple format for exchanging structured data.

### Decision 3: Use a Modular Architecture

**Decision:** The application was divided into separate Python modules.

**Reason:**
- Each module has a specific responsibility.
- Code is easier to understand and maintain.
- Individual functions can be tested independently.
- Changes to one module can be made without unnecessarily changing the entire application.

### Decision 4: Use Decimal for Financial Calculations

**Decision:** Python's `Decimal` type was selected for financial calculations.

**Reason:**

Floating-point calculations can introduce small precision differences. Decimal provides more suitable precision for prices, taxes and procurement totals.

### Decision 5: Use Automated Unit Testing

**Decision:** Python's built-in `unittest` framework was selected.

**Reason:**
- It does not require an additional testing library.
- It helps verify individual calculation functions.
- It helps identify errors during development.
- It supports repeatable test execution.

## 3. Business Rule Decisions

### Decision 6: Apply 2% Attrition to Passive Components

**Decision:** Apply 2% attrition to components with reference prefixes R, C and L.

**Reason:**

This accounts for additional material requirements during manufacturing.

### Decision 7: Round Order Quantities to Pack Sizes

**Decision:** Order quantities must be multiples of the vendor's pack size.

**Reason:**

Vendors supply components in specified pack quantities. The system therefore rounds the required quantity upward to the next valid pack multiple.

### Decision 8: Enforce Vendor Lead-Time Requirements

**Decision:** Exclude vendors whose lead time exceeds the requested need-by days.

**Reason:**

A vendor that cannot meet the required delivery time should not be selected.

### Decision 9: Select the Highest Eligible Price Break

**Decision:** Select the largest price-break minimum quantity that is less than or equal to the order quantity.

**Reason:**

This ensures the selected price corresponds to an eligible vendor quantity tier.

### Decision 10: Prefer Domestic Vendors in Equal-Cost Situations

**Decision:** Prefer a domestic vendor when domestic and import landed line costs are equal.

**Reason:**

This follows the specified vendor-selection priority.

### Decision 11: Prefer Shorter Lead Time as the Next Tie-Breaker

**Decision:** When landed cost and origin are equal, select the vendor with the shorter lead time.

**Reason:**

This prioritizes faster procurement when the cost and origin are otherwise equal.

### Decision 12: Apply Import and Domestic Charges Separately

**Decision:** Calculate domestic GST and small-order charges separately from import customs duty, IGST and freight.

**Reason:**

Domestic and import procurement follow different charging rules. Separating these calculations helps maintain clarity and accuracy.

## 4. Error and Status Decisions

### Decision 13: Use NO_SOURCE for Ineligible Components

**Decision:** Assign `NO_SOURCE` when no vendor satisfies the eligibility requirements.

**Reason:**

This clearly identifies components that cannot be procured using the available offers and delivery constraints.

### Decision 14: Mark Products as INCOMPLETE

**Decision:** Mark a product as `INCOMPLETE` if any required component has `NO_SOURCE`.

**Reason:**

A product cannot be considered fully procured when one or more required components have no eligible vendor.

## 5. Testing Decisions

The following five test cases were selected to verify important edge conditions:

| Test Case | Purpose |
|---|---|
| Exact price-break minimum | Verify that the minimum quantity is eligible |
| Exact pack-size multiple | Verify that no unnecessary overage is added |
| Equal landed cost | Verify domestic vendor preference |
| Delivery deadline failure | Verify that late vendors are excluded |
| Build quantity of one | Verify large pack-size handling |

**Test execution command:**

```bash
py -m unittest discover -s tests -v
```

**Current result:** 5 tests passed successfully.

## 6. Conclusion

The decisions documented above establish a consistent approach to data processing, procurement calculations, vendor selection and automated testing.

These decisions help make the application modular, understandable and easier to maintain.
