from datetime import date
from decimal import Decimal
import pytest
from expense_tracker.loaders import CSVTransactionLoader, JSONTransactionLoader
from expense_tracker.models import Transaction
from expense_tracker.writers import (
    CSVTransactionWriter,
    JSONTransactionWriter,
    CompositeTransactionWriter,
    DataWriteError,
)


def test_csv_writer_create_new_file(tmp_path):
    csv_file = tmp_path / "new_data.csv"
    writer = CSVTransactionWriter()
    txs = [
        Transaction(date(2025, 3, 1), "Lunch", "Food", Decimal("12.50")),
        Transaction(date(2025, 3, 2), "Bus", "Transport", Decimal("2.75")),
    ]
    assert writer.can_write(str(csv_file)) is True
    writer.write(str(csv_file), txs, append=False)

    loader = CSVTransactionLoader()
    loaded_txs = loader.load(str(csv_file))
    assert len(loaded_txs) == 2
    assert loaded_txs[0].description == "Lunch"
    assert loaded_txs[0].amount == Decimal("12.50")
    assert loaded_txs[1].description == "Bus"


def test_csv_writer_append_to_existing_file(tmp_path):
    csv_file = tmp_path / "existing_data.csv"
    writer = CSVTransactionWriter()
    loader = CSVTransactionLoader()

    # Create original file
    initial_txs = [Transaction(date(2025, 1, 1), "Coffee", "Food", Decimal("4.00"))]
    writer.write(str(csv_file), initial_txs, append=False)

    # Append new transaction
    new_txs = [Transaction(date(2025, 1, 2), "Tea", "Food", Decimal("3.50"))]
    writer.write(str(csv_file), new_txs, append=True)

    all_txs = loader.load(str(csv_file))
    assert len(all_txs) == 2
    assert all_txs[0].description == "Coffee"
    assert all_txs[1].description == "Tea"


def test_json_writer_create_new_file(tmp_path):
    json_file = tmp_path / "new_data.json"
    writer = JSONTransactionWriter()
    txs = [Transaction(date(2025, 4, 1), "Movie", "Entertainment", Decimal("15.00"))]

    assert writer.can_write(str(json_file)) is True
    writer.write(str(json_file), txs, append=False)

    loader = JSONTransactionLoader()
    loaded_txs = loader.load(str(json_file))
    assert len(loaded_txs) == 1
    assert loaded_txs[0].category == "Entertainment"
    assert loaded_txs[0].amount == Decimal("15.00")


def test_json_writer_append_to_existing_file(tmp_path):
    json_file = tmp_path / "existing_data.json"
    writer = JSONTransactionWriter()
    loader = JSONTransactionLoader()

    initial_txs = [Transaction(date(2025, 1, 1), "Book", "Education", Decimal("20.00"))]
    writer.write(str(json_file), initial_txs, append=False)

    new_txs = [Transaction(date(2025, 1, 2), "Pen", "Education", Decimal("2.00"))]
    writer.write(str(json_file), new_txs, append=True)

    all_txs = loader.load(str(json_file))
    assert len(all_txs) == 2
    assert all_txs[0].description == "Book"
    assert all_txs[1].description == "Pen"


def test_composite_writer(tmp_path):
    csv_file = tmp_path / "test.csv"
    json_file = tmp_path / "test.json"
    writer = CompositeTransactionWriter()

    txs = [Transaction(date(2025, 5, 1), "Item", "Cat", Decimal("10.00"))]

    writer.write(str(csv_file), txs)
    writer.write(str(json_file), txs)

    assert CSVTransactionLoader().load(str(csv_file))[0].description == "Item"
    assert JSONTransactionLoader().load(str(json_file))[0].description == "Item"


def test_composite_writer_unsupported():
    writer = CompositeTransactionWriter()
    with pytest.raises(DataWriteError, match="Unsupported file format"):
        writer.write("file.unsupported", [])


def test_json_writer_append_corrupted_file(tmp_path):
    json_file = tmp_path / "corrupt.json"
    json_file.write_text("invalid json content")

    writer = JSONTransactionWriter()
    txs = [Transaction(date(2025, 1, 1), "Item", "Cat", Decimal("10.00"))]

    with pytest.raises(DataWriteError, match="Failed to load existing JSON file"):
        writer.write(str(json_file), txs, append=True)


def test_large_dataset_performance(tmp_path):
    csv_file = tmp_path / "large.csv"
    writer = CSVTransactionWriter()
    loader = CSVTransactionLoader()

    large_txs = [
        Transaction(date(2025, 1, 1), f"Item {i}", "Bulk", Decimal("1.00"))
        for i in range(10000)
    ]

    writer.write(str(csv_file), large_txs)
    loaded_txs = loader.load(str(csv_file))
    assert len(loaded_txs) == 10000
