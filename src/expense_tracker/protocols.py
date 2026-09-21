"""Abstract protocols enforcing SOLID principles (DIP & ISP)."""

from typing import Protocol, runtime_checkable
from expense_tracker.models import Transaction, ReportResult


@runtime_checkable
class TransactionLoader(Protocol):
    """Protocol for loading transaction data from various sources/formats."""

    def can_load(self, filepath: str) -> bool:
        """Determines if this loader can parse the given file format."""
        ...

    def load(self, filepath: str) -> list[Transaction]:
        """Loads and parses transactions from a file path."""
        ...


@runtime_checkable
class ReportGenerator(Protocol):
    """Protocol for generating specific financial reports from transaction data."""

    @property
    def report_id(self) -> str:
        """Unique identifier for CLI mode selection."""
        ...

    @property
    def report_name(self) -> str:
        """Human-readable report description."""
        ...

    def generate(self, transactions: list[Transaction]) -> ReportResult:
        """Generates a summary report from a list of transactions."""
        ...


@runtime_checkable
class ReportFormatter(Protocol):
    """Protocol for rendering report results into formatted output strings."""

    def format(self, result: ReportResult) -> str:
        """Formats a ReportResult object into a presentable string representation."""
        ...


@runtime_checkable
class TransactionWriter(Protocol):
    """Protocol for writing/appending transaction data to file sources."""

    def can_write(self, filepath: str) -> bool:
        """Determines if this writer can write to the given file format."""
        ...

    def write(
        self, filepath: str, transactions: list[Transaction], append: bool = False
    ) -> None:
        """Writes or appends transactions to a file path."""
        ...
