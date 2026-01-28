import joblib, os, json, sys
from enum import Enum
from . import PullTransactions
from .MiscMethods import getFileLocations, isDate

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
    Transaction = joblib.load('classifiers\\TransactionClassifier.joblib')
    Income = joblib.load('classifiers\\IncomeClassifier.joblib')
    Purchase = joblib.load('classifiers\\PurchaseClassifier.joblib')
    Transfer = joblib.load('classifiers\\TransferClassifier.joblib')

monthYear = None

def main() -> list[dict, list]:  
    csvFileLocations = getFileLocations() # To-Do: refactor ('getfilelocations' is too broad)

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations] # To-Do: refactor ('getfilelocations' is too broad)

    rawTransactions = [t for bank in transactionsByBank for t in bank]

    groupedTransactions = groupTransactions(rawTransactions)

    categorizedTransactions = catTransactions(groupedTransactions)   

    report = prepareReport(categorizedTransactions)

    return report, categorizedTransactions


def groupTransactions(transactions: list) -> list:
    transactionModel = Models.Transaction.value

    for t in transactions:
        t.group = transactionModel.predict([t.info])[0]

    del transactionModel

    return transactions

def catTransactions(transactions: list) -> list:
    incomeModel = Models.Income.value
    purchaseModel = Models.Purchase.value
    transferModel = Models.Transfer.value

    for t in transactions:
        match (t.group):
            case TransactionType.Income.value: t.category = incomeModel.predict([t.info])[0]
            case TransactionType.Purchase.value: t.category = purchaseModel.predict([t.info])[0]
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

def getTransactionGroups(transactions: list[PullTransactions.Transaction]) -> list:
    incomeTotal = [t for t in transactions if t.group == TransactionType.Income.value]

    purchaseTotal = [t for t in transactions if t.group == TransactionType.Purchase.value]

    transferTotal = [t for t in transactions if t.group == TransactionType.Transfer.value]

    return ((TransactionType.Income, incomeTotal), (TransactionType.Purchase, purchaseTotal), (TransactionType.Transfer, transferTotal))

def getAcurateMonthTotal(transactions: list[PullTransactions.Transaction]):
    total = 0

    for tran in transactions:
        if not tran.group == 'transfer':
            total += tran.value
            continue

        if tran.category == TransferType.External.value:
            total += tran.value

    return total

def pushData(report):
    filePath = 'data\\Months.json'

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

def Run(monthYearInput: str, tags: list) -> bool:
    global monthYear
    monthYear = monthYearInput

    report, transactions = main()

    print("Finished Report")

    deleted = False
    pushed = False

    for t in tags:
        match t.lower():
            case '-delete': clearDataFiles(); deleted = True
            case '-push': pushData(report); pushed = True
            case '-print': printOutput(report, transactions)
            case _: continue

    print(f"Deleted: {deleted}") 
    print(f"Pushed: {pushed}") 

    return True
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        monthYear = sys.argv[1]

        if not isDate(monthYear):
            print("Bad date given - exiting")
            exit(3)
      
        print(f'Running Generation for {monthYear}')
        report, transactions = main(); print(" * Script Ended")

        for tag in sys.argv[2:]:
            match tag.lower():
                case '-delete': clearDataFiles(); print(" * Cleared data CSV files")
                case '-push': pushData(report); print(" * Pushed Data")
                case '-print': printOutput(report, transactions)
                case _: print(f"Tag '{tag}' is not recognized and was not ran")
    else:
        print("Month was not included"); sys.exit(3)