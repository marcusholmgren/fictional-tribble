from decimal import Decimal
from expense_tracker.models import ReportResult, SummaryRow
from expense_tracker.formatters import TableReportFormatter, JSONReportFormatter

def test_table_formatter():
    rows = [
        SummaryRow(key="Food", total=Decimal("150.00"), count=2, percentage=Decimal("65.2")),
        SummaryRow(key="Utilities", total=Decimal("80.00"), count=1, percentage=Decimal("34.8")),
    ]
    result = ReportResult(
        title="Summary by Category",
        headers=["Category", "Count", "Total Amount", "Share (%)"],
        rows=rows,
        total_amount=Decimal("230.00"),
        total_count=3,
    )
    formatter = TableReportFormatter(currency_symbol="$")
    output = formatter.format(result)
    assert "=== Summary by Category ===" in output
    assert "Food" in output
    assert "$150.00" in output
    assert "TOTAL" in output

def test_json_formatter():
    rows = [SummaryRow(key="Food", total=Decimal("100.00"), count=1, percentage=Decimal("100.0"))]
    result = ReportResult(
        title="Summary",
        headers=["Cat", "Cnt", "Tot", "Pct"],
        rows=rows,
        total_amount=Decimal("100.00"),
        total_count=1,
    )
    formatter = JSONReportFormatter()
    output = formatter.format(result)
    assert '"title": "Summary"' in output
    assert '"total": "100.00"' in output
