import src.getTransactions as getTransactinons
import src.NormalizeData as normalizeData


def test_run(mock_csv_file):
    assert type(getTransactinons.run(mock_csv_file, False, getTransactinons.ReturnType.JSON)) == dict 

def test_pull_transactions(mock_csv_file):
    good_response =  getTransactinons.pullTransactions(mock_csv_file, False)

    assert type(good_response) == list
    
    for transaction in good_response:
        assert type(transaction) == getTransactinons.Transaction
        assert transaction.category.lower() == 'uncategorized'
        assert transaction.group.lower() == 'ungrouped'
        assert normalizeData.isValidDate(transaction.date) == True
        assert type(transaction.value) == float

def test_group_transactions(mock_csv_file):
    transactions = getTransactinons.pullTransactions(mock_csv_file, False)

    good_response = getTransactinons.groupTransactions(transactions)

    for t in good_response:
        assert t.group.lower() != 'ungrouped'

def test_group_transactions(mock_csv_file):
    transactions = getTransactinons.pullTransactions(mock_csv_file, False)

    transactions = getTransactinons.groupTransactions(transactions)

    good_response = getTransactinons.categorizeTransactions(transactions)

    for t in good_response:
        assert t.category.lower() != 'uncategorized'

def test_return_transactions(mock_csv_file):
    transactions = getTransactinons.pullTransactions(mock_csv_file, False)

    transactions = getTransactinons.groupTransactions(transactions)

    transactions = getTransactinons.categorizeTransactions(transactions)

    good_json_response = getTransactinons.returnTransactions(transactions, getTransactinons.ReturnType.JSON)

    assert type(good_json_response) == dict

def test_return_json(mock_csv_file):
    transactions = getTransactinons.pullTransactions(mock_csv_file, False)

    transactions = getTransactinons.groupTransactions(transactions)

    transactions = getTransactinons.categorizeTransactions(transactions)
    
    assert type(getTransactinons.returnJson(transactions)) == dict
