from enum import Enum
from pathlib import Path
from pathlib import Path
import src.NormalizeData
from werkzeug.datastructures import FileStorage
import csv, sys, io, joblib, sys

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

CLASSIFIERS_DIR = BASE_DIR / "models\\classifiers"

# To-Do: change how models are loaded (so i can use pytest)

class TransactionType(Enum):
    Income = 'income'
    Purchase = 'purchase'
    Transfer = 'transfer'
    Undefined = 'Undefined'

class PurchaseType(Enum):
    Misc = 'misc'
    Food_Drink = 'food_drink'
    Gas = 'gas'

class IncomeType(Enum):
    Payroll = 'payroll'
    Passive = 'passive'

class TransferType(Enum):
    Internal = 'internal'
    External = 'external'

class Models(Enum):
    Transaction = joblib.load(str(CLASSIFIERS_DIR / "TransactionClassifier.joblib"))
    Income = joblib.load(str(CLASSIFIERS_DIR / "IncomeClassifier.joblib"))
    Purchase = joblib.load(str(CLASSIFIERS_DIR / "PurchaseClassifier.joblib"))
    # Transfer = joblib.load(str(CLASSIFIERS_DIR / "TransferClassifier.joblib"))
 
class Transaction:
    def __init__(self, transactionValue: float, tranasctionDate, transactionInfo):
        self.value = transactionValue
        self.date = tranasctionDate
        self.info = transactionInfo
        self.group = 'Ungrouped'
        self.category = 'Uncategorized'

    def __repr__(self):
        return f"({self.group}) value: {self.value} | category: {self.category} | Date: {self.date} | Info: {self.info}"
    
class ReturnType(Enum):
    JSON = 1,

def run(csvFile: FileStorage, returnType: ReturnType, internalTransfers: set) -> bool:
    transactions = pullTransactions(csvFile)

    transactions = groupTransactions(transactions)

    transactions = categorizeTransactions(transactions, internalTransfers)

    return returnTransactions(transactions, returnType)

def pullTransactions(file: FileStorage) -> list[Transaction]:
    dateExamples = {'date'}
    descriptionExamples = {'description'}
    amountExamples = {'amount'}

    dateIndex = -1
    descriptionIndex = -1
    amountIndex = -1

    stream = io.StringIO(file.stream.read().decode("utf-8"), newline="")
    
    reader = csv.reader(stream)
    
    firstRow = next(reader)

    for index in range(len(firstRow)):
        if firstRow[index].lower() in dateExamples: dateIndex = index
        elif firstRow[index].lower() in descriptionExamples: descriptionIndex = index
        elif firstRow[index].lower() in amountExamples: amountIndex = index 

    transactions = []

    for row in reader:
        if not src.NormalizeData.isValidDate(row[dateIndex]):
            raise ValueError #To-Do: create custom exception and handle it

        transactions.append(Transaction(float(row[amountIndex]), row[dateIndex], row[descriptionIndex]))   

    file.close()

    return transactions

def groupTransactions(transactions: list) -> list[Transaction]:
    transactionModel = Models.Transaction.value

    for t in transactions:
        t.group = transactionModel.predict([t.info])[0]

    del transactionModel

    return transactions

def categorizeTransactions(transactions: list[Transaction], internalTranfers: set) -> list[Transaction]:
    incomeModel = Models.Income.value
    purchaseModel = Models.Purchase.value

    for t in transactions:
        match (t.group):
            case TransactionType.Income.value: 
                t.category = incomeModel.predict([t.info])[0]
                
            case TransactionType.Purchase.value: 
                t.info = src.NormalizeData.normalizePurchase(t.info)
                t.category = purchaseModel.predict([t.info])[0]

            case TransactionType.Transfer.value: 
                if t.info in internalTranfers:
                    t.category = 'internal'
                
                else:
                    t.category = 'external'

            case _: 
                t.category = TransactionType.Undefined.value

    del incomeModel; del purchaseModel

    return transactions    

def returnTransactions(transactions: list, returnType: ReturnType):
    match (returnType):
        case returnType.JSON: return returnJson(transactions)
        case _: raise ValueError

def returnJson(transactions: list[Transaction]) -> dict:
    jsonOutput = {}

    for index in range(len(transactions)):
        jsonOutput[index + 1] = {
            'value': transactions[index].value,
            'date': transactions[index].date,
            'info': transactions[index].info,
            'group': transactions[index].group,
            'category': transactions[index].category
        }

    return jsonOutput