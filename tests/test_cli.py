from expense_tracker.cli import ExpenseTrackerApp
from expense_tracker.loaders import CSVTransactionLoader, JSONTransactionLoader


def test_cli_list_modes(capsys):
    app = ExpenseTrackerApp()
    exit_code = app.run(["-l"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Available Report Modes:" in captured.out
    assert "category" in captured.out


def test_cli_run_csv(tmp_path, capsys):
    csv_file = tmp_path / "expenses.csv"
    csv_file.write_text(
        "date,description,category,amount\n2025-01-01,Coffee,Food,5.00\n"
    )
    app = ExpenseTrackerApp()
    exit_code = app.run([str(csv_file), "-m", "category"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Summary by Category" in captured.out
    assert "$5.00" in captured.out


def test_cli_add_expense_new_file(tmp_path, capsys):
    csv_file = tmp_path / "new_expenses.csv"
    app = ExpenseTrackerApp()
    exit_code = app.run(
        [
            str(csv_file),
            "-a",
            "-d",
            "2025-05-10",
            "--description",
            "Groceries",
            "-c",
            "Food",
            "--amount",
            "45.50",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Successfully added expense" in captured.out

    loader = CSVTransactionLoader()
    txs = loader.load(str(csv_file))
    assert len(txs) == 1
    assert txs[0].description == "Groceries"


def test_cli_add_expense_existing_json_file(tmp_path, capsys):
    json_file = tmp_path / "expenses.json"
    app = ExpenseTrackerApp()
    # Add first expense
    app.run(
        [
            str(json_file),
            "-a",
            "-d",
            "2025-06-01",
            "--description",
            "Rent",
            "-c",
            "Housing",
            "--amount",
            "1200.00",
        ]
    )
    # Add second expense
    app.run(
        [
            str(json_file),
            "-a",
            "-d",
            "2025-06-02",
            "--description",
            "Power",
            "-c",
            "Utilities",
            "--amount",
            "80.00",
        ]
    )

    loader = JSONTransactionLoader()
    txs = loader.load(str(json_file))
    assert len(txs) == 2
    assert txs[0].description == "Rent"
    assert txs[1].description == "Power"


def test_cli_add_expense_invalid_amount(tmp_path, capsys):
    csv_file = tmp_path / "expenses.csv"
    app = ExpenseTrackerApp()
    exit_code = app.run(
        [
            str(csv_file),
            "-a",
            "--description",
            "Invalid",
            "-c",
            "Food",
            "--amount",
            "not_a_number",
        ]
    )
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Invalid amount" in captured.err


def test_cli_add_expense_invalid_date(tmp_path, capsys):
    csv_file = tmp_path / "expenses.csv"
    app = ExpenseTrackerApp()
    exit_code = app.run(
        [
            str(csv_file),
            "-a",
            "-d",
            "bad-date",
            "--description",
            "Invalid Date",
            "-c",
            "Food",
            "--amount",
            "10.00",
        ]
    )
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Invalid date format" in captured.err
