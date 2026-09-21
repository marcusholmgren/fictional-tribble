"""Command Line Interface orchestrator for the expense tracker app."""

import argparse
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from expense_tracker.formatters import TableReportFormatter
from expense_tracker.loaders import CompositeTransactionLoader, DataLoadError
from expense_tracker.models import Transaction
from expense_tracker.reports import ReportRegistry, create_default_registry
from expense_tracker.writers import CompositeTransactionWriter, DataWriteError


class ExpenseTrackerApp:
    """Application runner orchestrating file loading, writing, report generation, and display."""

    def __init__(
        self,
        loader: CompositeTransactionLoader | None = None,
        writer: CompositeTransactionWriter | None = None,
        registry: ReportRegistry | None = None,
        formatter: TableReportFormatter | None = None,
    ) -> None:
        self.loader = loader or CompositeTransactionLoader()
        self.writer = writer or CompositeTransactionWriter()
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

        parser.add_argument(
            "-a",
            "--add",
            action="store_true",
            help="Add a new expense transaction to the file.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=str,
            help="Transaction date (YYYY-MM-DD). Defaults to today if adding expense.",
        )
        parser.add_argument(
            "--description",
            type=str,
            help="Transaction description.",
        )
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            help="Transaction category.",
        )
        parser.add_argument(
            "--amount",
            type=str,
            help="Transaction amount.",
        )

        parsed_args = parser.parse_args(args)

        if parsed_args.list_modes:
            print("Available Report Modes:")
            for rid, name in self.registry.list_reports():
                print(f"  - {rid}: {name}")
            return 0

        if not parsed_args.filepath:
            parser.error("the following arguments are required: filepath")

        if parsed_args.add:
            if not parsed_args.description:
                parser.error("--description is required when adding an expense.")
            if not parsed_args.category:
                parser.error("--category is required when adding an expense.")
            if not parsed_args.amount:
                parser.error("--amount is required when adding an expense.")

            date_str = parsed_args.date
            if not date_str:
                dt_obj = datetime.now().date()
            else:
                try:
                    dt_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    print(
                        f"Error: Invalid date format '{date_str}'. Expected YYYY-MM-DD.",
                        file=sys.stderr,
                    )
                    return 1

            try:
                amt_dec = Decimal(parsed_args.amount)
            except (InvalidOperation, TypeError):
                print(
                    f"Error: Invalid amount '{parsed_args.amount}'. Must be a valid number.",
                    file=sys.stderr,
                )
                return 1

            new_tx = Transaction(
                date=dt_obj,
                description=parsed_args.description.strip(),
                category=parsed_args.category.strip(),
                amount=amt_dec,
            )

            try:
                self.writer.write(parsed_args.filepath, [new_tx], append=True)
                print(f"Successfully added expense to '{parsed_args.filepath}'.")
                return 0
            except DataWriteError as e:
                print(f"Error writing file: {e}", file=sys.stderr)
                return 1

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
