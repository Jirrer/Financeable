import pytest
from unittest.mock import patch

from python.src.GenerateData import *


def test_Run():
    badMonthYearInputs = [102025, 11/2020, "MyDate"]
    goodMonthYearInputs = ["01_2025", "12/2025", "07-2016"]

    for monthYear in badMonthYearInputs:
        assert(Run(monthYear, []) == False)

    for monthYear in goodMonthYearInputs:
        assert(Run(monthYear, []) == True)

    # continue testing

def test_getTransactions():
    csvFileLocations_mock = [("testing", "TestingData\\testing#98342.CSV")]

    with patch("python.src.GenerateData.getFileLocations", return_value=csvFileLocations_mock):
        assert(type(getTransactions()) == list)
        
def test_groupTransactions():
    transcationsList_mock = [
        PullTransactions.Transaction(-100.00, '01/01/2025', "Debit card purchase at bar"),
        PullTransactions.Transaction(-21.27, '10/25/2026', "Subscription renewel")
        ]
    
    assert(type(groupTransactions(transcationsList_mock)) == list)
    assert all(isinstance(transaction, PullTransactions.Transaction) for transaction in groupTransactions(transcationsList_mock))
    assert all(transaction.group not in [None, TransactionType.Undefined.value] for transaction in groupTransactions(transcationsList_mock))

def test_categorizeTransactions():
    transcationsList_mock = [
        PullTransactions.Transaction(-100.00, '01/01/2025', "Debit card purchase at bar"),
        PullTransactions.Transaction(-21.27, '10/25/2026', "Subscription renewel")
        ]
    
    transcationsList_mock[0].group = TransactionType.Purchase.value
    transcationsList_mock[1].group = TransactionType.Purchase.value
    
    assert(type(categorizeTransactions(transcationsList_mock)) == list)
    assert all(isinstance(transaction, PullTransactions.Transaction) for transaction in categorizeTransactions(transcationsList_mock))
    assert all(transaction.category not in [None, TransactionType.Undefined.value] for transaction in categorizeTransactions(transcationsList_mock))

def test_prepareReport():
    pass

def test_getAcurateMonthTotal():
    pass

def test_getTransactionGroups():
    pass

def test_pushData():
    pass

def test_clearDataFiles():
    pass

def test_printOutput():
    pass

