"""Formatters for rendering report results into formatted terminal output."""

from expense_tracker.models import ReportResult


class TableReportFormatter:
    """Formats report results into an aligned ASCII table."""

    def __init__(self, currency_symbol: str = "$") -> None:
        self.currency_symbol = currency_symbol

    def format(self, result: ReportResult) -> str:
        lines: list[str] = []
        lines.append(f"=== {result.title} ===")
        lines.append("")

        if not result.rows:
            lines.append("No transactions available.")
            return "\n".join(lines)

        # Prepare formatted table cell strings
        col_keys = [r.key for r in result.rows]
        col_counts = [str(r.count) for r in result.rows]
        col_totals = [f"{self.currency_symbol}{r.total:,.2f}" for r in result.rows]
        col_pcts = [f"{r.percentage}%" if r.percentage is not None else "-" for r in result.rows]

        # Calculate max column widths
        w_key = max(len(result.headers[0]), max(len(k) for k in col_keys))
        w_cnt = max(len(result.headers[1]), max(len(c) for c in col_counts))
        w_tot = max(len(result.headers[2]), max(len(t) for t in col_totals))
        w_pct = max(len(result.headers[3]), max(len(p) for p in col_pcts))

        # Format header line
        header_str = (
            f"{result.headers[0]:<{w_key}}  "
            f"{result.headers[1]:>{w_cnt}}  "
            f"{result.headers[2]:>{w_tot}}  "
            f"{result.headers[3]:>{w_pct}}"
        )
        separator = "-" * len(header_str)

        lines.append(header_str)
        lines.append(separator)

        # Format rows
        for key, cnt, tot, pct in zip(col_keys, col_counts, col_totals, col_pcts):
            lines.append(f"{key:<{w_key}}  {cnt:>{w_cnt}}  {tot:>{w_tot}}  {pct:>{w_pct}}")

        lines.append(separator)

        # Total summary row
        total_val_str = f"{self.currency_symbol}{result.total_amount:,.2f}"
        total_cnt_str = str(result.total_count)
        tot_label = "TOTAL"
        summary_line = (
            f"{tot_label:<{w_key}}  "
            f"{total_cnt_str:>{w_cnt}}  "
            f"{total_val_str:>{w_tot}}  "
            f"{'100.0%':>{w_pct}}"
        )
        lines.append(summary_line)

        return "\n".join(lines)


class JSONReportFormatter:
    """Formats report results into JSON string for structured export."""

    def format(self, result: ReportResult) -> str:
        import json

        data = {
            "title": result.title,
            "headers": result.headers,
            "rows": [
                {
                    "key": r.key,
                    "count": r.count,
                    "total": str(r.total),
                    "percentage": str(r.percentage) if r.percentage is not None else None,
                }
                for r in result.rows
            ],
            "total_amount": str(result.total_amount),
            "total_count": result.total_count,
        }
        return json.dumps(data, indent=2)
