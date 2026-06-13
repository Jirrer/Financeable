import src.pullReport as pullReport
import backend.app as app_module

import app as app_module

def test_run():
    # To-Do
    pass


def test_get_transaction_from_database(seeded_db):
    with app_module.app.app_context():
        valid_output = pullReport.getTransactionsFromDB(1, pullReport.Date('05-2026'))

    assert type(valid_output) == dict
    assert isinstance(valid_output['income'], tuple) and all(isinstance(item, pullReport.Transaction) for item in valid_output['income'])
    assert isinstance(valid_output['purchase'], tuple) and all(isinstance(item, pullReport.Transaction) for item in valid_output['purchase'])
    assert isinstance(valid_output['transfer'], tuple) and all(isinstance(item, pullReport.Transaction) for item in valid_output['transfer'])


def test_format_for_json():
    valid_input = {
        'purchase': (
            pullReport.Transaction('purchase', -17.54, 'temp description', 'food_drink'),
            pullReport.Transaction('purchase', -12.65, 'temp description', 'food_drink'),
            pullReport.Transaction('purchase', -1.56, 'temp description', 'food_drink'),
            pullReport.Transaction('purchase', -5.11, 'temp description', 'shopping'),
            pullReport.Transaction('purchase', -535.45, 'temp description', 'misc'),
        ),
        'transfer': (
            pullReport.Transaction('transfer', -100.23, 'temp description', 'transfer'),
            pullReport.Transaction('transfer', 12.00, 'temp description', 'transfer'),
        ),
        'income': (
            pullReport.Transaction('income', 32.32, 'temp description', 'interest'),
            pullReport.Transaction('income', 3.87, 'temp description', 'payroll'),
            pullReport.Transaction('income', 43.87, 'temp description', 'payroll'),
        )
    }

    valid_output = pullReport.formatForJson(valid_input)

    assert isinstance(valid_output['profit'], float)
    assert isinstance(valid_output['losses'], float)
    assert isinstance(valid_output['gains'], float)
    assert isinstance(valid_output['purchase'], dict)
    assert isinstance(valid_output['income'], dict)
    assert isinstance(valid_output['transfer'], dict)
    assert isinstance(valid_output['income'], dict) and all(isinstance(key, str) and isinstance(value, float) for key, value in valid_output['income'].items())
    assert isinstance(valid_output['purchase'], dict) and all(isinstance(key, str) and isinstance(value, float) for key, value in valid_output['purchase'].items())
    assert isinstance(valid_output['transfer'], dict) and all(isinstance(key, str) and isinstance(value, float) for key, value in valid_output['transfer'].items())


def test_filter_by_category():
    valid_input = [
        pullReport.Transaction('purchase', -17.54, 'temp description', 'food_drink'),
        pullReport.Transaction('purchase', -100.23, 'temp description', 'misc'),
        pullReport.Transaction('purchase', -32.32, 'temp description', 'gas'),
        pullReport.Transaction('purchase', -12.65, 'temp description', 'food_drink'),
        pullReport.Transaction('purchase', -12.00, 'temp description', 'shopping'),
        pullReport.Transaction('purchase', -5.11, 'temp description', 'shopping'),
        pullReport.Transaction('purchase', -1.56, 'temp description', 'food_drink'),
        pullReport.Transaction('purchase', -3.87, 'temp description', 'food_drink'),
        pullReport.Transaction('purchase', -535.45, 'temp description', 'misc'),
        pullReport.Transaction('purchase', -43.87, 'temp description', 'food_drink'),
    ]

    valid_output = pullReport.filterByCategory(valid_input)

    assert type(valid_output) == dict
    for key, val in valid_output.items():
        assert type(key) == str
        assert type(val) == float