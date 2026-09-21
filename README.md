# Expense Tracker CLI

A lightweight, extensible command-line expense tracker application written in Python 3.12+.
Designed strictly adhering to **SOLID principles**, zero external runtime dependencies, and strict module size limits (<200 lines per module).

---

## Features

- **Multi-format Support**: Parse and write expense transactions in CSV and JSON formats out of the box.
- **Multiple Summary Reports**:
  - **`category`**: Aggregates totals and percentage shares by expense category.
  - **`monthly`**: Summarizes spending grouped by `YYYY-MM` month periods.
  - **`category_monthly`**: Breakdown of expenses by category and month.
- **Interactive Expense Entry**: Add new transactions directly to existing or new CSV/JSON files via CLI flags.
- **Formatted Terminal Output**: Render aligned ASCII tables or machine-readable JSON reports.
- **SOLID Architecture**: Protocol-based decoupled design allowing seamless extension of loaders, writers, report generators, and formatters without modifying existing core logic.

---

## Installation & Requirements

### Prerequisites
- **Python 3.12+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip` / `venv`

### Installation

#### Option 1: Using `uv` (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/expense-tracker.git
cd expense-tracker

# Install in editable mode
uv pip install -e .
```

#### Option 2: Standard `pip`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Usage Guide

Run the application using the installed `expense-tracker` CLI entry point or via `python -m expense_tracker`.

### 1. View Available Report Modes
List all registered summary report generators:
```bash
expense-tracker -l
# or
expense-tracker --list-modes
```
*Output:*
```text
Available Report Modes:
  - category: Summary by Category
  - monthly: Monthly Expense Totals
  - category_monthly: Breakdown by Category and Month
```

### 2. Generate Expense Reports
Specify the data file path (CSV or JSON) and optionally select the report mode with `-m` or `--mode`.

#### Category Summary (Default)
```bash
expense-tracker sample_data/sample.csv
```
*Output:*
```text
=== Summary by Category ===

Category   Count  Total Amount  Share (%)
-----------------------------------------
Food           3       $190.00      59.5%
Health         1        $45.00      14.1%
Utilities      1        $85.00      26.4%
-----------------------------------------
TOTAL          5       $320.00     100.0%
```

#### Monthly Totals Summary
```bash
expense-tracker sample_data/sample.json -m monthly
```
*Output:*
```text
=== Monthly Expense Totals ===

Month    Count  Total Amount  Share (%)
---------------------------------------
2025-01      3       $210.00      65.6%
2025-02      2       $110.00      34.4%
---------------------------------------
TOTAL        5       $320.00     100.0%
```

#### Detailed Category & Monthly Breakdown
```bash
expense-tracker sample_data/sample.csv -m category_monthly
```

---

### 3. Add a New Expense Transaction
Add new transactions to a CSV or JSON file using `-a` / `--add`. Missing files will be created automatically.

```bash
expense-tracker transactions.csv --add \
  --date 2025-03-01 \
  --description "Internet Bill" \
  --category Utilities \
  --amount 60.00
```

#### Options when adding expenses:
- `-d`, `--date`: Transaction date (`YYYY-MM-DD`). Optional; defaults to today's date if omitted.
- `--description`: Text description or payee (*required*).
- `-c`, `--category`: Expense category (*required*).
- `--amount`: Transaction amount in decimal numeric format (*required*).

---

## Supported File Formats

### CSV Format
CSV files must include a header row containing `date`, `description`, `category`, and `amount`.
```csv
date,description,category,amount
2025-01-10,Groceries,Food,120.50
2025-01-15,Coffee,Food,4.50
2025-01-20,Electricity,Utilities,85.00
```

### JSON Format
JSON files must contain an array of transaction objects with required key names:
```json
[
  {
    "date": "2025-01-10",
    "description": "Groceries",
    "category": "Food",
    "amount": 120.50
  },
  {
    "date": "2025-01-20",
    "description": "Electricity",
    "category": "Utilities",
    "amount": 85.00
  }
]
```

---

## Architecture & Code Structure

```text
src/expense_tracker/
├── __init__.py      # Package entry & version declaration
├── __main__.py      # Execution module (python -m expense_tracker)
├── cli.py           # CLI argument parsing and application controller
├── formatters.py    # Table & JSON report formatters
├── loaders.py       # CSV & JSON data file loaders
├── models.py        # Domain entities (Transaction, SummaryRow, ReportResult)
├── protocols.py     # Static protocols enforcing SOLID interfaces
├── reports.py       # Financial calculation strategy reports & registry
└── writers.py       # CSV & JSON data file writers
```

Refer to [ARCHITECTURE.md](ARCHITECTURE.md) for full architectural specifications, design pattern details, and step-by-step guides for extending the app with new loaders, reports, or formats.

---

## Development & Testing

### Running Tests
Run the pytest test suite:
```bash
pytest
```

### Module Line Count Verification
Maintainability is preserved by keeping all modules strictly under 200 lines of code:
```bash
wc -l src/expense_tracker/*.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
