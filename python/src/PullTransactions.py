from enum import Enum
import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

class SupportedBanks(Enum):
    TESTING = 'testing'
    Fifth_Third = 'fifth_third'
    American_Express = 'american_express'
 
class Transaction:
    def __init__(self, transactionValue: float, tranasctionDate, transactionInfo):
        self.value = transactionValue
        self.date = tranasctionDate
        self.info = transactionInfo
        self.group = None
        self.category = None

    def __repr__(self):
        return f"({self.group}) value: {self.value} | category: {self.category} | Date: {self.date} | Info: {self.info}"

def run(bankType, fileName: str):
    match (bankType):
        case SupportedBanks.TESTING.value: return testing(fileName) 
        case SupportedBanks.Fifth_Third.value: return fifthThird(fileName)
        case SupportedBanks.American_Express.value: return americanExpress(fileName)
        case _: print(f"Could not find bank - '{bankType}'"); return []

def testing(fileName):
    output, format = [], ("date", "description", "amount")

    with open(fileName, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader) 

        dateIndex, infoIndex, valueIndex = None, None, None

        for index in range(len(format)):
            if format[index] == 'date': dateIndex = index
            elif format[index] == 'description': infoIndex = index
            elif format[index] == 'amount': valueIndex = index

        for row in reader:
            output.append(Transaction(float(row[valueIndex]), row[dateIndex], row[infoIndex]))
    
    return output

def fifthThird(fileName):
    output, format = [], ("date", "info", "check", "value")

    with open(fileName, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader) 

        dateIndex, infoIndex, valueIndex = None, None, None

        for index in range(len(format)):
            if format[index] == 'date': dateIndex = index
            elif format[index] == 'info': infoIndex = index
            elif format[index] == 'value': valueIndex = index

        for row in reader:
            output.append(Transaction(float(row[valueIndex]), row[dateIndex], row[infoIndex]))
    
    return output

def americanExpress(fileName):
    output, format = [], ('Date','Description','Amount')

    with open(fileName, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader) 

        dateIndex, infoIndex, valueIndex = None, None, None

        for index in range(len(format)):
            if format[index] == 'Date': dateIndex = index
            elif format[index] == 'Description': infoIndex = index
            elif format[index] == 'Amount': valueIndex = index

        for row in reader:
            if float(row[valueIndex]) > 0.00: output.append(Transaction(float(f'-{row[valueIndex]}'), row[dateIndex], row[infoIndex]))
            else: output.append(Transaction(float(row[valueIndex]), row[dateIndex], row[infoIndex]))
            
    return output