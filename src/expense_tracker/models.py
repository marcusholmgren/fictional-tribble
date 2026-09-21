"""Domain models for the expense tracker application."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    """Represents a single financial transaction.

    Attributes:
        date: Transaction date.
        description: Description or payee of transaction.
        category: Category of transaction (e.g., Food, Utilities).
        amount: Monetary value (Decimal for financial precision).
    """

    date: date
    description: str
    category: str
    amount: Decimal


@dataclass(frozen=True)
class SummaryRow:
    """Represents a single row in a generated report.

    Attributes:
        key: Unique grouping key or period label (e.g. 'Food', '2025-01').
        total: Aggregated decimal amount for this row.
        count: Number of transactions in this group.
        percentage: Optional percentage relative to overall total.
    """

    key: str
    total: Decimal
    count: int
    percentage: Decimal | None = None


@dataclass(frozen=True)
class ReportResult:
    """Represents the computed summary output of a report generation operation.

    Attributes:
        title: Display name/heading of the report.
        headers: Column title headers.
        rows: Computed summary rows.
        total_amount: Overall sum of transactions across all rows.
        total_count: Overall count of transactions evaluated.
    """

    title: str
    headers: list[str]
    rows: list[SummaryRow]
    total_amount: Decimal
    total_count: int
