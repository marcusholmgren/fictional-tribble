"""Data loaders for parsing transaction data from external file formats."""

import csv
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from expense_tracker.models import Transaction


class DataLoadError(Exception):
    """Raised when an error occurs while parsing input transaction data."""


class CSVTransactionLoader:
    """Loader for CSV formatted transaction files."""

    def can_load(self, filepath: str) -> bool:
        """Check if file ends with .csv extension."""
        return Path(filepath).suffix.lower() == ".csv"

    def load(self, filepath: str) -> list[Transaction]:
        """Load transactions from CSV file."""
        path = Path(filepath)
        if not path.exists():
            raise DataLoadError(f"File not found: {filepath}")

        transactions: list[Transaction] = []
        try:
            with path.open("r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    return transactions

                # Normalize field names to lower case
                field_map = {fn.strip().lower(): fn for fn in reader.fieldnames}
                required = {"date", "description", "category", "amount"}
                missing = required - set(field_map.keys())
                if missing:
                    raise DataLoadError(
                        f"CSV missing required columns: {', '.join(sorted(missing))}"
                    )

                for row_idx, row in enumerate(reader, start=2):
                    dt_str = row[field_map["date"]].strip()
                    desc = row[field_map["description"]].strip()
                    cat = row[field_map["category"]].strip()
                    amt_str = row[field_map["amount"]].strip()

                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
                    except ValueError as e:
                        raise DataLoadError(
                            f"Row {row_idx}: Invalid date format '{dt_str}'. Expected YYYY-MM-DD."
                        ) from e

                    try:
                        amt = Decimal(amt_str)
                    except (InvalidOperation, TypeError) as e:
                        raise DataLoadError(
                            f"Row {row_idx}: Invalid amount format '{amt_str}'."
                        ) from e

                    transactions.append(
                        Transaction(date=dt, description=desc, category=cat, amount=amt)
                    )
        except Exception as e:
            if isinstance(e, DataLoadError):
                raise
            raise DataLoadError(f"Failed to parse CSV file '{filepath}': {e}") from e

        return transactions


class JSONTransactionLoader:
    """Loader for JSON formatted transaction files."""

    def can_load(self, filepath: str) -> bool:
        """Check if file ends with .json extension."""
        return Path(filepath).suffix.lower() == ".json"

    def load(self, filepath: str) -> list[Transaction]:
        """Load transactions from JSON file."""
        path = Path(filepath)
        if not path.exists():
            raise DataLoadError(f"File not found: {filepath}")

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise DataLoadError("JSON root element must be a list of transactions.")

            transactions: list[Transaction] = []
            for idx, item in enumerate(data, start=1):
                if not isinstance(item, dict):
                    raise DataLoadError(f"Item {idx} in JSON is not a dictionary.")

                required = {"date", "description", "category", "amount"}
                missing = required - set(item.keys())
                if missing:
                    raise DataLoadError(
                        f"Item {idx} missing keys: {', '.join(sorted(missing))}"
                    )

                dt_str = str(item["date"]).strip()
                desc = str(item["description"]).strip()
                cat = str(item["category"]).strip()
                amt_val = item["amount"]

                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
                except ValueError as e:
                    raise DataLoadError(
                        f"Item {idx}: Invalid date format '{dt_str}'. Expected YYYY-MM-DD."
                    ) from e

                try:
                    amt = Decimal(str(amt_val))
                except (InvalidOperation, TypeError) as e:
                    raise DataLoadError(
                        f"Item {idx}: Invalid amount '{amt_val}'."
                    ) from e

                transactions.append(
                    Transaction(date=dt, description=desc, category=cat, amount=amt)
                )

            return transactions
        except Exception as e:
            if isinstance(e, DataLoadError):
                raise
            raise DataLoadError(f"Failed to parse JSON file '{filepath}': {e}") from e


class CompositeTransactionLoader:
    """Composite loader selecting suitable loader based on file extension/type."""

    def __init__(self, loaders: list | None = None) -> None:
        self._loaders = loaders or [CSVTransactionLoader(), JSONTransactionLoader()]

    def register_loader(self, loader) -> None:
        """Dynamically add a new file loader strategy."""
        self._loaders.append(loader)

    def load(self, filepath: str) -> list[Transaction]:
        """Delegates loading to the first matching loader."""
        for loader in self._loaders:
            if loader.can_load(filepath):
                return loader.load(filepath)
        raise DataLoadError(f"Unsupported file format for file: {filepath}")
