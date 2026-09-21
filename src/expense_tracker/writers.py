"""Data writers for serializing transaction data to external file formats."""

import csv
import json
from pathlib import Path
from expense_tracker.loaders import JSONTransactionLoader
from expense_tracker.models import Transaction


class DataWriteError(Exception):
    """Raised when an error occurs while writing transaction data."""


class CSVTransactionWriter:
    """Writer for CSV formatted transaction files."""

    def can_write(self, filepath: str) -> bool:
        """Check if file ends with .csv extension."""
        return Path(filepath).suffix.lower() == ".csv"

    def write(
        self, filepath: str, transactions: list[Transaction], append: bool = False
    ) -> None:
        """Write or append transactions to a CSV file."""
        path = Path(filepath)
        file_exists = path.exists() and path.stat().st_size > 0

        # If append mode is requested on an existing file, check if headers exist
        fieldnames = ["date", "description", "category", "amount"]
        write_header = not file_exists or not append

        mode = "a" if append and file_exists else "w"

        try:
            with path.open(mode, encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()

                for tx in transactions:
                    writer.writerow(
                        {
                            "date": tx.date.strftime("%Y-%m-%d"),
                            "description": tx.description,
                            "category": tx.category,
                            "amount": str(tx.amount),
                        }
                    )
        except Exception as e:
            raise DataWriteError(f"Failed to write CSV file '{filepath}': {e}") from e


class JSONTransactionWriter:
    """Writer for JSON formatted transaction files."""

    def can_write(self, filepath: str) -> bool:
        """Check if file ends with .json extension."""
        return Path(filepath).suffix.lower() == ".json"

    def write(
        self, filepath: str, transactions: list[Transaction], append: bool = False
    ) -> None:
        """Write or append transactions to a JSON file."""
        path = Path(filepath)
        existing_txs: list[Transaction] = []

        if append and path.exists() and path.stat().st_size > 0:
            loader = JSONTransactionLoader()
            try:
                existing_txs = loader.load(str(path))
            except Exception as e:
                raise DataWriteError(
                    f"Failed to load existing JSON file '{filepath}' for appending: {e}"
                ) from e

        all_txs = existing_txs + transactions if append else transactions

        json_data = [
            {
                "date": tx.date.strftime("%Y-%m-%d"),
                "description": tx.description,
                "category": tx.category,
                "amount": float(tx.amount),
            }
            for tx in all_txs
        ]

        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)
        except Exception as e:
            raise DataWriteError(f"Failed to write JSON file '{filepath}': {e}") from e


class CompositeTransactionWriter:
    """Composite writer selecting suitable writer based on file extension/type."""

    def __init__(self, writers: list | None = None) -> None:
        self._writers = writers or [CSVTransactionWriter(), JSONTransactionWriter()]

    def register_writer(self, writer) -> None:
        """Dynamically add a new file writer strategy."""
        self._writers.append(writer)

    def write(
        self, filepath: str, transactions: list[Transaction], append: bool = False
    ) -> None:
        """Delegates writing to the first matching writer."""
        for writer in self._writers:
            if writer.can_write(filepath):
                writer.write(filepath, transactions, append=append)
                return
        raise DataWriteError(f"Unsupported file format for writing: {filepath}")
