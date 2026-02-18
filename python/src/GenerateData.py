import joblib, os, json, sys
from pathlib import Path
from enum import Enum
from . import PullTransactions
from .MiscMethods import getFileLocations, isDate
from .NormalizeData import normalizePurchase

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

CLASSIFIERS_DIR = BASE_DIR / "classifiers"
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = (BASE_DIR / "ReportData").resolve()
REPORT_DIR.mkdir(parents=True, exist_ok=True)

class TransactionType(Enum):
    Income = 'income'
    Purchase = 'purchase'
    Transfer = 'transfer'

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

# Keep classifiers as a Class so it can be vectorized as soon as the
# script runs (manually run) or when the module is loaded (when being
# used by the rust frontend)
class Models(Enum):
    Transaction = joblib.load(str(CLASSIFIERS_DIR / "TransactionClassifier.joblib"))
    Income = joblib.load(str(CLASSIFIERS_DIR / "IncomeClassifier.joblib"))
    Purchase = joblib.load(str(CLASSIFIERS_DIR / "PurchaseClassifier.joblib"))
    Transfer = joblib.load(str(CLASSIFIERS_DIR / "TransferClassifier.joblib"))


def Run(monthYear: str, tags: list) -> bool:
    if not isDate(monthYear):
        print("Bad date given - exiting")
        exit(3)

    print(f'Running Generation for {monthYear}') 

    transactions = getTransactions()

    report = prepareReport(transactions)

    print("Finished Report")

    deleted = False
    pushed = False

    for t in tags:
        match t.lower():
            case '-delete': clearDataFiles(); deleted = True
            case '-push': pushData(report, monthYear); pushed = True
            case '-print': printOutput(report, transactions)
            case _: continue
    
    print(f"Deleted: {deleted}") 
    print(f"Pushed: {pushed}") 

    return True

def getTransactions():
    csvFileLocations = getFileLocations() # To-Do: refactor ('getfilelocations' is too broad)

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations] 

    rawTransactions = [t for bank in transactionsByBank for t in bank]

    groupedTransactions = groupTransactions(rawTransactions)

    return categorizeTransactions(groupedTransactions)  


def groupTransactions(transactions: list) -> list:
    transactionModel = Models.Transaction.value

    for t in transactions:
        t.group = transactionModel.predict([t.info])[0]

    del transactionModel

    return transactions

def categorizeTransactions(transactions: list) -> list:
    incomeModel = Models.Income.value
    purchaseModel = Models.Purchase.value
    transferModel = Models.Transfer.value

    for t in transactions:
        match (t.group):
            case TransactionType.Income.value: 
                t.category = incomeModel.predict([t.info])[0]
                
            case TransactionType.Purchase.value: 
                t.info = normalizePurchase(t.info)
                t.category = purchaseModel.predict([t.info])[0]

            case TransactionType.Transfer.value: t.category = transferModel.predict([t.info])[0]
            case _: continue

    del incomeModel; del purchaseModel; del transferModel

    return transactions

def prepareReport(transactions: list[PullTransactions.Transaction]) -> dict:
    output = {}

    output['Profit/Loss'] = getAcurateMonthTotal(transactions)

    # Transaction Groups
    for tranType, tran in getTransactionGroups(transactions): # To-Do: show totals for categories
        output[tranType.value.capitalize()] = {"Total": sum([t.value for t in tran])}

        for category in set([t.category for t in tran]):
            output[tranType.value.capitalize()][category] = sum([t.value for t in tran if t.category == category]) 

    return output

def getAcurateMonthTotal(transactions: list[PullTransactions.Transaction]):
    total = 0

    for tran in transactions:
        if not tran.group == 'transfer':
            total += tran.value
            continue

        if tran.category == TransferType.External.value:
            total += tran.value

    return total

def getTransactionGroups(transactions: list[PullTransactions.Transaction]) -> list:
    incomeTotal = [t for t in transactions if t.group == TransactionType.Income.value]

    purchaseTotal = [t for t in transactions if t.group == TransactionType.Purchase.value]

    transferTotal = [t for t in transactions if t.group == TransactionType.Transfer.value]

    return ((TransactionType.Income, incomeTotal), (TransactionType.Purchase, purchaseTotal), (TransactionType.Transfer, transferTotal))

def pushData(report, monthYear):
    filePath = str(BASE_DIR / "Data\\Months.json")

    if not os.path.exists(filePath): data = []
    else:
        with open(filePath, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except json.JSONDecodeError: data = []
    
    data[monthYear] = report

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    

def clearDataFiles():
    filePaths = [path[1] for path in getFileLocations()]
    
    for path in filePaths:
        os.remove(path)

def printOutput(report, transactions):
    print(report)
    
    for tran in transactions:
        print(tran)
    

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Month was not included")
        sys.exit(3)

    Run(sys.argv[1], sys.argv[2:])