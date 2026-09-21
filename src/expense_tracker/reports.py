"""Report generators for computing aggregated expense financial metrics."""

from collections import defaultdict
from decimal import Decimal
from expense_tracker.models import ReportResult, SummaryRow, Transaction


class CategorySummaryReport:
    """Generates an expense summary aggregated by category (OCP compliant)."""

    @property
    def report_id(self) -> str:
        return "category"

    @property
    def report_name(self) -> str:
        return "Summary by Category"

    def generate(self, transactions: list[Transaction]) -> ReportResult:
        """Aggregate transactions by category and compute totals and percentage share."""
        if not transactions:
            return ReportResult(
                title=self.report_name,
                headers=["Category", "Count", "Total Amount", "Share (%)"],
                rows=[],
                total_amount=Decimal("0.00"),
                total_count=0,
            )

        cat_totals: dict[str, Decimal] = defaultdict(Decimal)
        cat_counts: dict[str, int] = defaultdict(int)
        overall_total = Decimal("0.00")
        overall_count = len(transactions)

        # Accumulate amounts and counts per category
        for tx in transactions:
            cat_totals[tx.category] += tx.amount
            cat_counts[tx.category] += 1
            overall_total += tx.amount

        rows: list[SummaryRow] = []
        # Sort categories alphabetically for consistent ordering
        for cat in sorted(cat_totals.keys()):
            tot = cat_totals[cat]
            cnt = cat_counts[cat]
            # Quantize percentage share to 0.1 for precise financial display
            pct = (
                (tot / overall_total * Decimal("100.0")).quantize(Decimal("0.1"))
                if overall_total != Decimal("0")
                else Decimal("0.0")
            )
            rows.append(SummaryRow(key=cat, total=tot, count=cnt, percentage=pct))

        return ReportResult(
            title=self.report_name,
            headers=["Category", "Count", "Total Amount", "Share (%)"],
            rows=rows,
            total_amount=overall_total,
            total_count=overall_count,
        )


class MonthlyTotalsReport:
    """Generates an expense summary aggregated by YYYY-MM period."""

    @property
    def report_id(self) -> str:
        return "monthly"

    @property
    def report_name(self) -> str:
        return "Monthly Expense Totals"

    def generate(self, transactions: list[Transaction]) -> ReportResult:
        """Aggregate transactions by YYYY-MM month period."""
        if not transactions:
            return ReportResult(
                title=self.report_name,
                headers=["Month", "Count", "Total Amount", "Share (%)"],
                rows=[],
                total_amount=Decimal("0.00"),
                total_count=0,
            )

        month_totals: dict[str, Decimal] = defaultdict(Decimal)
        month_counts: dict[str, int] = defaultdict(int)
        overall_total = Decimal("0.00")
        overall_count = len(transactions)

        # Group transactions by YYYY-MM formatted date key
        for tx in transactions:
            month_key = tx.date.strftime("%Y-%m")
            month_totals[month_key] += tx.amount
            month_counts[month_key] += 1
            overall_total += tx.amount

        rows: list[SummaryRow] = []
        # Sort chronologically by YYYY-MM month string
        for month_key in sorted(month_totals.keys()):
            tot = month_totals[month_key]
            cnt = month_counts[month_key]
            pct = (
                (tot / overall_total * Decimal("100.0")).quantize(Decimal("0.1"))
                if overall_total != Decimal("0")
                else Decimal("0.0")
            )
            rows.append(SummaryRow(key=month_key, total=tot, count=cnt, percentage=pct))

        return ReportResult(
            title=self.report_name,
            headers=["Month", "Count", "Total Amount", "Share (%)"],
            rows=rows,
            total_amount=overall_total,
            total_count=overall_count,
        )


class CategoryMonthlyReport:
    """Generates a detailed summary by Category and Month."""

    @property
    def report_id(self) -> str:
        return "category_monthly"

    @property
    def report_name(self) -> str:
        return "Breakdown by Category and Month"

    def generate(self, transactions: list[Transaction]) -> ReportResult:
        """Aggregate transactions by combined Category and YYYY-MM month key."""
        if not transactions:
            return ReportResult(
                title=self.report_name,
                headers=["Category / Month", "Count", "Total Amount", "Share (%)"],
                rows=[],
                total_amount=Decimal("0.00"),
                total_count=0,
            )

        group_totals: dict[str, Decimal] = defaultdict(Decimal)
        group_counts: dict[str, int] = defaultdict(int)
        overall_total = Decimal("0.00")
        overall_count = len(transactions)

        for tx in transactions:
            key = f"{tx.category} ({tx.date.strftime('%Y-%m')})"
            group_totals[key] += tx.amount
            group_counts[key] += 1
            overall_total += tx.amount

        rows: list[SummaryRow] = []
        for key in sorted(group_totals.keys()):
            tot = group_totals[key]
            cnt = group_counts[key]
            pct = (
                (tot / overall_total * Decimal("100.0")).quantize(Decimal("0.1"))
                if overall_total != Decimal("0")
                else Decimal("0.0")
            )
            rows.append(SummaryRow(key=key, total=tot, count=cnt, percentage=pct))

        return ReportResult(
            title=self.report_name,
            headers=["Category (Month)", "Count", "Total Amount", "Share (%)"],
            rows=rows,
            total_amount=overall_total,
            total_count=overall_count,
        )


class ReportRegistry:
    """Registry allowing dynamically adding report generator implementations (OCP)."""

    def __init__(self) -> None:
        self._reports: dict[str, object] = {}

    def register(self, generator) -> None:
        """Register a report generator strategy instance."""
        self._reports[generator.report_id] = generator

    def get(self, report_id: str):
        """Retrieve a registered report generator strategy by report_id."""
        if report_id not in self._reports:
            raise KeyError(f"Unknown report mode '{report_id}'.")
        return self._reports[report_id]

    def list_reports(self) -> list[tuple[str, str]]:
        """List all available report IDs and descriptive report names."""
        return [(rid, gen.report_name) for rid, gen in self._reports.items()]


def create_default_registry() -> ReportRegistry:
    """Factory helper creating a ReportRegistry populated with built-in reports."""
    registry = ReportRegistry()
    registry.register(CategorySummaryReport())
    registry.register(MonthlyTotalsReport())
    registry.register(CategoryMonthlyReport())
    return registry
