import joblib, os, json, csv, sys
from enum import Enum
import PullTransactions

with open('supported_banks.json', 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

    # To-Do: Refactor the word purchase to transaction where needed 

class TransactionType(Enum):
    Income = 'income'
    Purchase = 'purchase'
    MISC = 'misc'

class PurchaseType(Enum):
    pass

class IncomeType(Enum):
    pass

class Month_Report:
    def __init__(self, date: str, loss: float, gain: float, profit: float, purchases: list):
        self.date = date
        self.loss = loss
        self.gain = gain
        self.profit_loss = profit
        self.loss_category = self.getLossCategories(purchases)
        self.gain_category = self.getGainCategories(purchases)

    def __repr__(self):
        output = f"""
        {self.date} Report {{
        \tDate: {self.date}
        \tLosses: {self.loss}
        \tGains: {self.gain}
        \tProfit: {self.profit_loss}
        \tLoss Categories: {self.loss_category}       
        \tGains Categories: {self.gain_category}                    
        }}
        """

        return output

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

def main(monthYear: str) -> Month_Report:  
    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    rawTransactions = [t for bank in transactionsByBank for t in bank]

    rawPurchases, rawIncomes = groupTransactions(rawTransactions)

    for x in rawPurchases:
        print(x)

    for y in rawIncomes:
        print(y)

    exit()

    # categorizedPurchases = categorizePurchases(rawPurchases, clf, vectorizer)

    # profit = sum([float(p.value) for p in categorizedPurchases])

    # loss = sum([float(p.value) for p in categorizedPurchases if float(p.value) < 0.0])

    # gain = sum([float(p.value) for p in categorizedPurchases if float(p.value) > 0.0])

    # monthReport = Month_Report(monthYear, loss, gain, profit, categorizedPurchases)

    # print(monthReport)

    # return monthReport

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


def groupTransactions(transactions: list) -> tuple[list, list]:
    purchases, incomes = [], []

    model = joblib.load('classifiers\\TransactionClassifier.joblib')

    for t in transactions:
        prediction = model.predict([t.info])

        if prediction[0] == TransactionType.Income.value: 
            t.group = prediction[0]
            incomes.append(t)

        elif prediction[0] == TransactionType.Purchase.value: 
            t.group = prediction[0]
            purchases.append(t)

    del transactions

    return purchases, incomes


# def categorizePurchases(purchases: list) -> list:
    # purchaseDescriptions = [purchase.info for purchase in purchases]

    # try:
    #     strsCategories = clf.predict(vectorizer.transform(purchaseDescriptions))
    
    # except ValueError as e:
    #     if "Found array with 0 sample(s)" in e.args[0]:
    #         print("Empty Data Folder - Script Ended Early")
    #         sys.exit(2)

    # for index in range(len(purchases)):
    #     purchases[index].category = strsCategories[index]

    # return purchases

def getMonthLoss(puchasesInput: list) -> float:
    total = 0.0

    for purchase in puchasesInput:
        if isFloat(purchase.value): total += float(purchase.value)
    
    return total

def getMonthGain(purchasesInput: list):
    total = 0.0
    
    for purchase in purchasesInput:
        if float(purchase.value) > 0:
            total += float(purchase.value)

    return total

def isFloat(string: str):
    try:
        float(string)
        return '.' in string
    
    except ValueError:
        return False

def pushData(report: Month_Report):
    filePath = 'data\\userInfo.json'

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # if file is empty
    else:
        data = []

    newMonth = {}
    
    newMonth["Losses"] = report.loss

    newMonth["Gains"] = report.gain

    newMonth["Profit/Loss"] = report.profit_loss

    newMonth["Loss_Categories"] = report.loss_category

    newMonth["Gain_Categories"] = report.gain_category

    data[report.date] = newMonth

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(" * Pushed Data")

def clearDataFiles():
    filePaths = [path[1] for path in getFileLocations()]
    
    for path in filePaths:
        os.remove(path)
    
if __name__ == "__main__":
    if len(sys.argv) <= 1: print("Month was not included"); sys.exit(3)

    month = sys.argv[1]


    scriptOutput = main(month); print(" * Script Ended")

    # if len(sys.argv) >= 3:
    #     for tag in sys.argv[2:]:
    #         match tag.lower():
    #             case '-delete': clearDataFiles(); print(" * Cleared data CSV files")
    #             case '-push': pushData(scriptOutput)
    #             case _: print(f"Tag '{tag}' is not recognized and was not ran")