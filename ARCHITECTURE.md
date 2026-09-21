# CLI Expense Tracker - Architecture & Design Specification

## Overview
The CLI Expense Tracker is a command-line tool written in Python 3.12+ (managed with `uv`) designed to process financial transaction data from file sources (such as CSV and JSON), execute transactions additions, and present formatted analytical reports.

The codebase strictly adheres to **SOLID principles**, strict **complexity constraints (<200 lines per module)**, and uses **standard library components only** without external runtime dependencies.

---

## 1. Core Workflow
The system supports two primary operational workflows:

### A. Report Generation Workflow
1. **Load transactions**: Parsed from file input (CSV or JSON) via `CompositeTransactionLoader`.
2. **Select report strategy**: Aggregated by category, month, or category-monthly breakdown via `ReportRegistry`.
3. **Render summary**: Formatted as an aligned terminal ASCII table or structured JSON string.

```text
[ Input File (CSV/JSON) ]
          │
          ▼
 [ TransactionLoader ] ──► List[Transaction]
                                  │
                                  ▼
 [ ReportGenerator ]   ──► ReportResult
                                  │
                                  ▼
 [ ReportFormatter ]   ──► Formatted Output (Table/JSON)
```

### B. Transaction Write/Append Workflow
1. **Parse CLI Input**: Validates date (`YYYY-MM-DD`), description, category, and numeric amount.
2. **Instantiate Domain Model**: Constructs immutable `Transaction` dataclass instance.
3. **Persist Transaction**: Append to target file via `CompositeTransactionWriter` using standard format serialization.

```text
[ CLI Input Args ] ──► Transaction Model ──► [ TransactionWriter ] ──► [ Output File (CSV/JSON) ]
```

---

## 2. SOLID Principles Implementation

### Single Responsibility Principle (SRP)
Each module and class has exactly one reason to change:
- `expense_tracker.models`: Immutable domain data structures (`Transaction`, `ReportResult`, `SummaryRow`).
- `expense_tracker.loaders`: File parsing strategies (`CSVTransactionLoader`, `JSONTransactionLoader`, `CompositeTransactionLoader`).
- `expense_tracker.writers`: File writing strategies (`CSVTransactionWriter`, `JSONTransactionWriter`, `CompositeTransactionWriter`).
- `expense_tracker.reports`: Financial aggregation strategies (`CategorySummaryReport`, `MonthlyTotalsReport`, `CategoryMonthlyReport`).
- `expense_tracker.formatters`: Display formatting (`TableReportFormatter`, `JSONReportFormatter`).
- `expense_tracker.cli`: Command-line argument parsing and execution orchestration (`ExpenseTrackerApp`).

### Open/Closed Principle (OCP)
The application is open for extension but closed for modification:
- **Adding Data Formats**: Implement `TransactionLoader` / `TransactionWriter` protocols and register with `CompositeTransactionLoader` / `CompositeTransactionWriter` without modifying existing loaders or writers.
- **Adding Report Modes**: Implement `ReportGenerator` protocol and register with `ReportRegistry` without changing existing report calculations.
- **Adding Output Formats**: Implement `ReportFormatter` protocol (e.g. Markdown or HTML) without altering aggregation or loading logic.

### Liskov Substitution Principle (LSP)
All loaders implement the `TransactionLoader` protocol and can be interchanged seamlessly. All report generators implement the `ReportGenerator` protocol and return standardized `ReportResult` instances.

### Interface Segregation Principle (ISP)
Interfaces in `expense_tracker.protocols` are small and focused (`TransactionLoader`, `TransactionWriter`, `ReportGenerator`, `ReportFormatter`). Clients only depend on methods they actually consume.

### Dependency Inversion Principle (DIP)
High-level workflow modules (`ExpenseTrackerApp`) depend on abstractions defined in `protocols.py` rather than concrete implementations. Concrete classes are injected during initialization or factory creation.

---

## 3. Module Line Count Limits

| Module | Purpose | Line Count Constraint | Status |
| :--- | :--- | :--- | :--- |
| `src/expense_tracker/models.py` | Data transfer & domain objects | < 200 lines | Compliant |
| `src/expense_tracker/protocols.py` | Abstract protocols / interfaces | < 200 lines | Compliant |
| `src/expense_tracker/loaders.py` | CSV & JSON parser strategies | < 200 lines | Compliant |
| `src/expense_tracker/writers.py` | CSV & JSON writer strategies | < 200 lines | Compliant |
| `src/expense_tracker/reports.py` | Aggregation algorithms & registry | < 200 lines | Compliant |
| `src/expense_tracker/formatters.py` | Table & JSON rendering | < 200 lines | Compliant |
| `src/expense_tracker/cli.py` | CLI controller and entry point | < 200 lines | Compliant |

---

## 4. How to Extend the Codebase

### Adding a New Data Loader (e.g., XML loader)
1. Create a class implementing `TransactionLoader`:
   ```python
   from expense_tracker.models import Transaction

   class XMLTransactionLoader:
       def can_load(self, filepath: str) -> bool:
           return filepath.endswith('.xml')

       def load(self, filepath: str) -> list[Transaction]:
           # Parse XML transactions
           ...
   ```
2. Register it with `CompositeTransactionLoader`:
   ```python
   loader = CompositeTransactionLoader()
   loader.register_loader(XMLTransactionLoader())
   ```

### Adding a New Data Writer (e.g., XML writer)
1. Create a class implementing `TransactionWriter`:
   ```python
   from expense_tracker.models import Transaction

   class XMLTransactionWriter:
       def can_write(self, filepath: str) -> bool:
           return filepath.endswith('.xml')

       def write(self, filepath: str, transactions: list[Transaction], append: bool = False) -> None:
           # Write or append XML transactions
           ...
   ```
2. Register it with `CompositeTransactionWriter`:
   ```python
   writer = CompositeTransactionWriter()
   writer.register_writer(XMLTransactionWriter())
   ```

### Adding a New Report Mode (e.g., Daily breakdown)
1. Create a class implementing `ReportGenerator`:
   ```python
   from expense_tracker.models import ReportResult, Transaction

   class DailyTotalsReport:
       @property
       def report_id(self) -> str:
           return "daily"

       @property
       def report_name(self) -> str:
           return "Daily Expense Totals"

       def generate(self, transactions: list[Transaction]) -> ReportResult:
           # Compute daily aggregations
           ...
   ```
2. Register it with `ReportRegistry`:
   ```python
   registry.register(DailyTotalsReport())
   ```
