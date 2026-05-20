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
    pass


def test_get_arrays_by_dict(seeded_db):
    pass

