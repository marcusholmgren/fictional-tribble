from datetime import date
from decimal import Decimal
import pytest
from expense_tracker.models import Transaction
from expense_tracker.reports import (
    CategorySummaryReport,
    MonthlyTotalsReport,
    CategoryMonthlyReport,
    ReportRegistry,
)


@pytest.fixture
def sample_transactions():
    return [
        Transaction(date(2025, 1, 10), "Groceries", "Food", Decimal("100.00")),
        Transaction(date(2025, 1, 20), "Restaurant", "Food", Decimal("50.00")),
        Transaction(date(2025, 2, 5), "Internet", "Utilities", Decimal("80.00")),
    ]


def test_category_summary_report(sample_transactions):
    report = CategorySummaryReport()
    res = report.generate(sample_transactions)
    assert res.total_amount == Decimal("230.00")
    assert res.total_count == 3
    assert len(res.rows) == 2
    # Rows should be sorted alphabetically: Food, Utilities
    assert res.rows[0].key == "Food"
    assert res.rows[0].total == Decimal("150.00")
    assert res.rows[0].percentage == Decimal("65.2")


def test_monthly_totals_report(sample_transactions):
    report = MonthlyTotalsReport()
    res = report.generate(sample_transactions)
    assert res.total_amount == Decimal("230.00")
    assert len(res.rows) == 2
    assert res.rows[0].key == "2025-01"
    assert res.rows[0].total == Decimal("150.00")


def test_category_monthly_report(sample_transactions):
    report = CategoryMonthlyReport()
    res = report.generate(sample_transactions)
    assert len(res.rows) == 2


def test_report_registry():
    registry = ReportRegistry()
    gen = CategorySummaryReport()
    registry.register(gen)
    assert registry.get("category") == gen
    assert len(registry.list_reports()) == 1
