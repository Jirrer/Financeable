import src.uploadTransaction as uploadTransaction
from src.exceptions import *
import pytest

def test_run(seeded_db):
    dictData = {
            1: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'purchase',
                'category': 'misc'
            },

            2: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'purchase',
                'category': 'misc'
            },

            3: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'transfer',
                'category': 'misc'
            }
        }

    with pytest.raises(BadUploadType):
        uploadTransaction.run(1, list(dictData))

    with pytest.raises(InvalidUser):
        uploadTransaction.run(2, dictData)  

def test_valid_user(seeded_db):
    assert uploadTransaction.validUser(1) == True
    assert uploadTransaction.validUser(2) == False

def test_run_json(seeded_db):
    import sqlite3
    dictData = {
            1: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'purchase',
                'category': 'misc'
            },

            2: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'purchase',
                'category': 'misc'
            },

            3: {
                'value': 27.15,
                'date': '2026-05-19',
                'info': "test information",
                'group': 'transfer',
                'category': 'misc'
            }
        }

    # should not raise
    uploadTransaction.run(1, dictData)

    # verify rows inserted
    with sqlite3.connect(seeded_db) as conn:
        cur = conn.cursor()
        purchases = cur.execute('SELECT COUNT(*) FROM purchase WHERE user_id = ?', (1,)).fetchone()[0]
        transfers = cur.execute('SELECT COUNT(*) FROM transfer WHERE user_id = ?', (1,)).fetchone()[0]

    assert purchases == 2
    assert transfers == 1


def test_get_arrays_by_dict(seeded_db):
    dictData = {
        1: {
            'value': 10.0,
            'date': '2026-05-19',
            'info': 'i',
            'group': 'income',
            'category': 'salary'
        },
        2: {
            'value': 5.0,
            'date': '2026-05-19',
            'info': 'p',
            'group': 'purchase',
            'category': 'food'
        }
    }

    arrays = uploadTransaction.getTransactionsByGroup(dictData)

    assert 'income' in arrays and 'purchase' in arrays and 'transfer' in arrays
    assert isinstance(arrays['income'], list)
    assert isinstance(arrays['purchase'], list)
    assert arrays['income'][0] == (10.0, '2026-05-19', 'i', 'salary')
    assert arrays['purchase'][0] == (5.0, '2026-05-19', 'p', 'food')

