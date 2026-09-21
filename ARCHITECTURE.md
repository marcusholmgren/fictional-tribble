# CLI Expense Tracker - Architecture & Design Specification

## Overview
The CLI Expense Tracker is a command-line tool written in Python 3.12+ (managed with `uv`) designed to process financial transaction data from file sources (such as CSV and JSON) and present formatted analytical reports.

The codebase strictly adheres to **SOLID principles**, strict **complexity constraints (<200 lines per module)**, and uses **standard library components only** without external dependencies.

---

## 1. Core Workflow
The user workflow follows three sequential steps:
1. **Load transactions**: Parsed from file input (CSV, JSON, etc.).
2. **Select report mode**: Aggregated by category, month, or category-monthly breakdown.
3. **View summary**: Rendered as an aligned terminal table or structured JSON.

```
[ Input File (CSV/JSON) ]
          │
          ▼
 [ TransactionLoader ] ──► List[Transaction]
                                  │
                                  ▼
 [ ReportGenerator ]   ──► ReportResult
                                  │
                                  ▼
 [ ReportFormatter ]   ──► Formatted Terminal Output
```

---

## 2. SOLID Principles Implementation

### Single Responsibility Principle (SRP)
Each module and class has exactly one reason to change:
- `expense_tracker.models`: Domain data structures (`Transaction`, `ReportResult`, `SummaryRow`).
- `expense_tracker.loaders`: File parsing logic (`CSVTransactionLoader`, `JSONTransactionLoader`, `CompositeTransactionLoader`).
- `expense_tracker.reports`: Financial aggregation strategies (`CategorySummaryReport`, `MonthlyTotalsReport`, `CategoryMonthlyReport`).
- `expense_tracker.formatters`: Display formatting (`TableReportFormatter`, `JSONReportFormatter`).
- `expense_tracker.cli`: Command-line argument parsing and execution orchestration.

### Open/Closed Principle (OCP)
The application is open for extension but closed for modification:
- **Adding new Data Formats**: Implement `TransactionLoader` protocol and register with `CompositeTransactionLoader` without altering existing loaders.
- **Adding new Report Modes**: Implement `ReportGenerator` protocol and register with `ReportRegistry` without changing existing report calculations.
- **Adding new Output Formats**: Implement `ReportFormatter` protocol (e.g. Markdown or HTML) without changing aggregation or loading logic.

### Liskov Substitution Principle (LSP)
All loaders implement the `TransactionLoader` protocol and can be interchanged seamlessly. All report generators implement the `ReportGenerator` protocol and return standardized `ReportResult` instances.

### Interface Segregation Principle (ISP)
Interfaces in `expense_tracker.protocols` are small and focused (`TransactionLoader`, `ReportGenerator`, `ReportFormatter`). Clients only depend on methods they actually consume.

### Dependency Inversion Principle (DIP)
High-level workflow modules (`ExpenseTrackerApp`) depend on abstractions defined in `protocols.py` rather than concrete implementations. Concrete classes are injected during initialization or factory creation.

---

## 3. Module Line Count Verification

| Module | Purpose | Line Count Constraint |
| :--- | :--- | :--- |
| `src/expense_tracker/models.py` | Data transfer & domain objects | < 200 lines |
| `src/expense_tracker/protocols.py` | Abstract protocols / interfaces | < 200 lines |
| `src/expense_tracker/loaders.py` | CSV & JSON parser strategies | < 200 lines |
| `src/expense_tracker/reports.py` | Aggregation algorithms & registry | < 200 lines |
| `src/expense_tracker/formatters.py` | Table & JSON rendering | < 200 lines |
| `src/expense_tracker/cli.py` | CLI controller and entry point | < 200 lines |

---

## 4. How to Extend

### Adding a New Data Loader (e.g., XML loader)
1. Create a class implementing `TransactionLoader`:
   ```python
   class XMLTransactionLoader:
       def can_load(self, filepath: str) -> bool:
           return filepath.endswith('.xml')
       def load(self, filepath: str) -> list[Transaction]:
           # parse XML
           ...
   ```
2. Register it with `CompositeTransactionLoader.register_loader(XMLTransactionLoader())`.

### Adding a New Report Mode (e.g., Daily breakdown)
1. Create a class implementing `ReportGenerator`:
   ```python
   class DailyTotalsReport:
       @property
       def report_id(self) -> str: return "daily"
       @property
       def report_name(self) -> str: return "Daily Expense Totals"
       def generate(self, transactions: list[Transaction]) -> ReportResult:
           ...
   ```
2. Register it with `registry.register(DailyTotalsReport())`.
