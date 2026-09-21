"""Command Line Interface orchestrator for the expense tracker app."""

import argparse
import sys
from expense_tracker.formatters import TableReportFormatter
from expense_tracker.loaders import CompositeTransactionLoader, DataLoadError
from expense_tracker.reports import ReportRegistry, create_default_registry


class ExpenseTrackerApp:
    """Application runner orchestrating file loading, report generation, and output display."""

    def __init__(
        self,
        loader: CompositeTransactionLoader | None = None,
        registry: ReportRegistry | None = None,
        formatter: TableReportFormatter | None = None,
    ) -> None:
        self.loader = loader or CompositeTransactionLoader()
        self.registry = registry or create_default_registry()
        self.formatter = formatter or TableReportFormatter()

    def run(self, args: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(
            prog="expense-tracker",
            description="CLI Expense Tracker Application following SOLID architecture principles.",
        )
        parser.add_argument(
            "filepath",
            type=str,
            nargs="?",
            default=None,
            help="Path to transaction file (CSV or JSON).",
        )

        available_modes = [rid for rid, _ in self.registry.list_reports()]
        parser.add_argument(
            "-m",
            "--mode",
            type=str,
            choices=available_modes,
            default="category",
            help=f"Report mode to display (default: 'category'). Options: {', '.join(available_modes)}",
        )

        parser.add_argument(
            "-l",
            "--list-modes",
            action="store_true",
            help="List all available report modes and exit.",
        )

        parsed_args = parser.parse_args(args)

        if parsed_args.list_modes:
            print("Available Report Modes:")
            for rid, name in self.registry.list_reports():
                print(f"  - {rid}: {name}")
            return 0

        if not parsed_args.filepath:
            parser.error("the following arguments are required: filepath")

        try:
            transactions = self.loader.load(parsed_args.filepath)
        except DataLoadError as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            return 1

        try:
            generator = self.registry.get(parsed_args.mode)
        except KeyError as e:
            print(f"Error selecting report mode: {e}", file=sys.stderr)
            return 1

        report_result = generator.generate(transactions)
        output = self.formatter.format(report_result)
        print(output)
        return 0


def main() -> None:
    """CLI entry point function."""
    app = ExpenseTrackerApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
