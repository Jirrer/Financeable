import csv, joblib
from src.MiscMethods import getFileLocations
import src.PullTransactions as PullTransactions

def findNewTransactionTypes():
    with open('TrainingData\\TransactionData.csv', 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader)

        currentDataPointsList = [(i, l) for i, l in reader]
        
        currentDataPoints = set(currentDataPointsList)

    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    transactions = [t for bank in transactionsByBank for t in bank]

    for t in transactions:
        print(t.info)

    model = joblib.load('classifiers\\TransactionClassifier.joblib')

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

if __name__ == "__main__": 
    findNewTransactionTypes()