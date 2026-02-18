import pytest

from python.src.MiscMethods import *

monthDict = {
            "01/2025": {
            "Profit/Loss": -419.44999999999993,
            "Income": {
                "Total": 1011.78,
                "payroll": 1011.78
            },
            "Purchase": {
                "Total": -495.23,
                "food_drink": -109.16999999999999,
                "misc": -386.06
            },
            "Transfer": {
                "Total": -1252.98,
                "external": -936.0,
                "internal": -316.98
            }
        },
        "12/2025": {
            "Profit/Loss": 570.0600000000001,
            "Income": {
                "Total": 2297.34,
                "passive": 0.15,
                "payroll": 2297.19
            },
            "Purchase": {
                "Total": -791.2800000000002,
                "misc": -299.01,
                "gas": -67.87,
                "food_drink": -424.40000000000015
            },
            "Transfer": {
                "Total": -1252.98,
                "internal": -316.98,
                "external": -936.0
            }
        },
    }


def test_fillMonthYearGaps():
    

    newDict = list(fillMonthYearGaps(monthDict))

    expectedLen = 12 * (int(getThisMonthYear()[3:]) - int(newDict[0][3:])) + int(getThisMonthYear()[:2]) - int(newDict[0][:2]) + 1

    assert(len(fillMonthYearGaps(monthDict)) == expectedLen)

def test_sortMonthJson():
    sortedDictList = list(sortMonthJson(monthDict))

    lastDate = sortedDictList[0]
    for currentDate in sortedDictList[1:]:
        if int(lastDate[:2]) == 12:
            assert((int(currentDate[3:])) == int(lastDate[3:]) + 1)
        else:
            assert((int(currentDate[:2]) == int(lastDate[:2])) + 1)

        lastDate = currentDate
    

def test_getFileLocations():
    suportedBank = "fifth_third#980332"
    unsportedBank = "NotValidBank#32834"
    invalidBank = "NotFormated3892"

    assert(pullBankName(suportedBank) == 'fifth_third')
    assert(pullBankName(unsportedBank) == 'INVALID_BANK')
    assert(pullBankName(invalidBank) == 'INVALID_BANK')


def test_pullBankName(): #To-Do: mock the files found
    assert(pullBankName('fifth_third#89349243') == 'fifth_third')
    assert(pullBankName('american_express#938') == 'american_express')

    assert(pullBankName(1) == 'INVALID_BANK')
    assert(pullBankName(True) == 'INVALID_BANK')

    assert(pullBankName("fifth_third") == 'INVALID_BANK')
    assert(pullBankName("american_express") == 'INVALID_BANK')

def test_isDate():
    pass

def test_isFloat():
    pass

def test_getThisMonth():
    pass

def test_labelToDate():
    pass

def test_monthToWord():
    pass
