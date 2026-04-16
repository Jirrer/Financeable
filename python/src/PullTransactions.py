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
    flipValues = False

    match (bankType):
        case SupportedBanks.Fifth_Third.value: flipValues = False; 
        case SupportedBanks.American_Express.value: flipValues = True
        case _: print(f"Could not find bank - '{bankType}'"); return []


    return getValues(fileName, flipValues)

def getValues(fileName: str, flipValues: bool) -> list:
    dateExamples = {'date'}
    descriptionExamples = {'description'}
    amountExamples = {'amount'}

    dateIndex = -1
    descriptionIndex = -1
    amountIndex = -1

    file = open(fileName, 'r')
    
    reader = csv.reader(file)

    firstRow = next(reader)

    for index in range(len(firstRow)):
        if firstRow[index].lower() in dateExamples: dateIndex = index
        elif firstRow[index].lower() in descriptionExamples: descriptionIndex = index
        elif firstRow[index].lower() in amountExamples: amountIndex = index 

    output = []

    for row in reader:
        if flipValues == False:
            output.append(Transaction(float(row[amountIndex]), row[dateIndex], row[descriptionIndex]))   

        elif flipValues == True:
            if float(row[amountIndex]) > 0.00: output.append(Transaction(float(f'-{row[amountIndex]}'), row[dateIndex], row[descriptionIndex]))
            else: output.append(Transaction(float(row[amountIndex].replace('-','')), row[dateIndex], row[descriptionIndex]))
        
    file.close()

    return output