import joblib, os, json, csv, sys
from enum import Enum
import PullTransactions

# To-Do: Refactor the word purchase to transaction where needed (and the letter p to t when needed)

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

    def getLossCategories(self, purchases: list):
        output = {}

        for purchase in purchases:
            if not float(purchase.value) < 0.0: continue

            if purchase.category in output:
                output[purchase.category] += float(purchase.value)
            else:
                output[purchase.category] = float(purchase.value)

        return output
    
    def getGainCategories(self, purchases: list):
        output = {}

        for purchase in purchases:
            if not float(purchase.value) > 0.0: continue

            if purchase.category in output:
                output[purchase.category] += float(purchase.value)
            else:
                output[purchase.category] = float(purchase.value)

        return output

def main():  
    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    rawTransactions = [t for bank in transactionsByBank for t in bank]

    groupedTransactions = groupTransactions(rawTransactions)

    categorizedTransactions = catTransactions(groupedTransactions)   

    report = prepareReport(categorizedTransactions)

    return report, categorizedTransactions

def getFileLocations() -> list[tuple[str, str]]:
    output = []

    pdfLocation = 'ReportData'

    pdfNames = [f for f in os.listdir(pdfLocation)]

    for file in pdfNames:
        if os.path.exists(f'{pdfLocation}\\{file}'):
            output.append((pullBankName(file), f'{pdfLocation}\\{file}'))

    return output

def pullBankName(fileName: str) -> str:
    output = []

    for letter in fileName:
        if letter == '#': return ''.join(output)

        output.append(letter)

    return "Error pulling bank name"


def groupTransactions(transactions: list) -> list:
    model = joblib.load('classifiers\\TransactionClassifier.joblib')

    for t in transactions:
        prediction = model.predict([t.info])

        if prediction[0] == TransactionType.Income.value: 
            t.group = prediction[0]

        elif prediction[0] == TransactionType.Purchase.value: 
            t.group = prediction[0]

        elif prediction[0] == TransactionType.Transfer.value: 
            t.group = prediction[0]

    del model

    return transactions

def catTransactions(transactions: list) -> list:
    incomeModel = joblib.load('classifiers\\IncomeClassifier.joblib')

    purchaseModel = joblib.load('classifiers\\PurchaseClassifier.joblib')

    transferModel = joblib.load('classifiers\\TransferClassifier.joblib')

    for t in transactions:
        match (t.group):
            case TransactionType.Income.value: t.category = incomeModel.predict([t.info])[0]
            case TransactionType.Purchase.value: t.category = purchaseModel.predict([t.info])[0]
            case TransactionType.Transfer.value: t.category = transferModel.predict([t.info])[0]
            case _: continue


    del incomeModel; del purchaseModel; del transferModel

    return transactions

def prepareReport(transactions: list[PullTransactions.Transaction]):
    output = {}

    output['Profit/Loss'] = getAcurateMonthTotal(transactions)

    for tranType, tran in getTransactionGroups(transactions): # To-Do: show totals for categories
        output[tranType.value.capitalize()] = {"Total": sum([t.value for t in tran])}

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
    filePath = 'data\\userInfo.json'

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # if file is empty
    else:
        data = []

    data[monthYear] = report

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(" * Pushed Data")

def clearDataFiles():
    filePaths = [path[1] for path in getFileLocations()]
    
    for path in filePaths:
        os.remove(path)

def printOutput(report, transactions):
    print(report)
    
    for tran in transactions:
        print(tran)
    
if __name__ == "__main__":
    if len(sys.argv) <= 1: print("Month was not included"); sys.exit(3)

    monthYear = sys.argv[1]

    report, transactions = main(); print(" * Script Ended")

    if len(sys.argv) >= 3:
        for tag in sys.argv[2:]:
            match tag.lower():
                case '-delete': clearDataFiles(); print(" * Cleared data CSV files")
                case '-push': pushData(report)
                case '-print': printOutput(report, transactions)
                case _: print(f"Tag '{tag}' is not recognized and was not ran")