from expense_tracker.cli import ExpenseTrackerApp

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
        "date,description,category,amount\n"
        "2025-01-01,Coffee,Food,5.00\n"
    )
    app = ExpenseTrackerApp()
    exit_code = app.run([str(csv_file), "-m", "category"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Summary by Category" in captured.out
    assert "$5.00" in captured.out
