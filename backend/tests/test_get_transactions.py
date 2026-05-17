import src.getTransactions as getTransactinons


def test_run(mock_csv_file):
    assert type(getTransactinons.run(mock_csv_file, False, getTransactinons.ReturnType.JSON)) == dict 