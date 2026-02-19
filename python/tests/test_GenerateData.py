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
    csvFileLocations_mock = [("fifth_third", "TestingData\\fifth_third#87323.CSV")]

    with patch("python.src.GenerateData.getFileLocations", return_value=csvFileLocations_mock):
        assert(type(getTransactions()) == list)
        
def test_groupTransactions():
    pass

def test_categorizeTransactions():
    pass

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

