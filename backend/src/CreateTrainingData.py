import csv, joblib, sys, os, re
from pathlib import Path
from enum import Enum

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

from python.src.MiscMethods import getFileLocations
import python.src.PullTransactions as PullTransactions
from python.src.NormalizeData import normalizePurchase

class Models(Enum):
    Transaction = joblib.load("classifiers\\TransactionClassifier.joblib")
    Income = joblib.load("classifiers\\IncomeClassifier.joblib")
    Purchase = joblib.load("classifiers\\PurchaseClassifier.joblib")
    Transfer = joblib.load("classifiers\\TransferClassifier.joblib")

def findNewTransactionTypes():
    training_dir = BASE_DIR / "TrainingData"
    classifiers_dir = BASE_DIR / "classifiers"

    with open(str(training_dir / "TransactionData.csv"), 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader)

        currentDataPointsList = [(i, l) for i, l in reader]
        
        currentDataPoints = set(currentDataPointsList)

    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    transactions = [t for bank in transactionsByBank for t in bank]

    for t in transactions:
        print(t.info)

    model = joblib.load(str(classifiers_dir / "TransactionClassifier.joblib"))

    for t in transactions:
        t.group = model.predict([t.info])[0]

    incomes = [(t.info, t.group) for t in transactions if (t.info, t.group) not in currentDataPoints and t.group == 'income']

    purchases = [(t.info, t.group) for t in transactions if (t.info, t.group) not in currentDataPoints and t.group == 'purchase']

    transfers = [(t.info, t.group) for t in transactions if (t.info, t.group) not in currentDataPoints and t.group == 'transfer']

    seen = set()

    print("\n")
    for info, group in incomes: 
        if (info, group) not in seen:
            print(f'"{info}",{group}')
            seen.add((info, group))

    print("\n")
    for info, group in purchases: 
        if (info, group) not in seen:
            print(f'"{info}",{group}')
            seen.add((info, group))

    print("\n")
    for info, group in transfers: 
        if (info, group) not in seen:
            print(f'"{info}",{group}')
            seen.add((info, group))

    print(f'\nCurrent unique transactions: {len(currentDataPoints)}')
    print(f'Duplicates: {len(currentDataPointsList) != len(currentDataPoints)}')

def orderTrainingData():
    base_dir = Path(__file__).resolve().parents[2]
    training_dir = base_dir / "TrainingData"

    for fileName in os.listdir(str(training_dir)):
        fileContent = open(str(training_dir / fileName), "r", newline="")

        reader = csv.reader(fileContent)

        next(reader)

        outcome = {}
        for description, label in reader:
            if label in outcome: outcome[label].append(description)
            else: outcome[label] = [description]

        output = []
        for key in outcome:
            for value in outcome[key]:
                output.append(f'"{value}",{key}')

        with open(str(training_dir / fileName), "w", newline="") as file:
            file.write("Description, Label\n")

            for index in range(len(output)):
                if index == len(output) - 1: file.write(output[index])
                else: file.write(f"{output[index]}\n")


def splitRawTransactions(filePath):
    groups = {'income': [], 'transfer': [], 'purchase': []}

    with open(filePath, 'r', newline='') as file:
        for row in file:
            groups[Models.Transaction.value.predict([row])[0]].append(row.replace('\n', ''))

    for key in groups.keys():
        print(key)

        for val in groups[key]:
            print(val)

        print("\n\n")



def normalizePurchaseData(filePath: str):
    output = []

    with open (filePath, 'r', newline='') as file:
        for row in file:
            output.append(normalizePurchase(row))

    for x in output:
        print(x)





        
if __name__ == "__main__": 
    normalizePurchaseData('C:\\Projects\\financeable\\purchase_training_data.CSV')
    # splitRawTransactions('C:\\Projects\\financeable\\training_data.CSV')
    # findNewTransactionTypes()

    # if len(sys.argv) > 1 and sys.argv[1].lower() == "-order":
    #     orderTrainingData()