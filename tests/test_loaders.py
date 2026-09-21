from datetime import date
from decimal import Decimal
import pytest
from expense_tracker.loaders import (
    CSVTransactionLoader,
    JSONTransactionLoader,
    CompositeTransactionLoader,
    DataLoadError,
)

def test_csv_loader_valid(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(
        "date,description,category,amount\n"
        "2025-01-15,Coffee,Food,4.50\n"
        "2025-01-16,Electricity,Utilities,75.20\n"
    )
    loader = CSVTransactionLoader()
    assert loader.can_load(str(csv_file)) is True
    txs = loader.load(str(csv_file))
    assert len(txs) == 2
    assert txs[0].date == date(2025, 1, 15)
    assert txs[0].category == "Food"
    assert txs[0].amount == Decimal("4.50")

def test_csv_loader_invalid_date(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("date,description,category,amount\ninvalid,Coffee,Food,4.50\n")
    loader = CSVTransactionLoader()
    with pytest.raises(DataLoadError, match="Invalid date format"):
        loader.load(str(csv_file))

def test_json_loader_valid(tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text(
        '[\n'
        '  {"date": "2025-02-01", "description": "Gym", "category": "Health", "amount": 50.00}\n'
        ']\n'
    )
    loader = JSONTransactionLoader()
    assert loader.can_load(str(json_file)) is True
    txs = loader.load(str(json_file))
    assert len(txs) == 1
    assert txs[0].category == "Health"
    assert txs[0].amount == Decimal("50.00")

def test_composite_loader(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("date,description,category,amount\n2025-01-01,Test,Cat,10.00\n")
    loader = CompositeTransactionLoader()
    txs = loader.load(str(csv_file))
    assert len(txs) == 1

def test_composite_loader_unsupported():
    loader = CompositeTransactionLoader()
    with pytest.raises(DataLoadError, match="Unsupported file format"):
        loader.load("unsupported.txt")
