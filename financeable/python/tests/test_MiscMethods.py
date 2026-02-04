import pytest

from src.MiscMethods import *

def test_getFileLocations():
    pass

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
