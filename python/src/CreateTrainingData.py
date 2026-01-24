import csv, joblib, sys, os
from python.src.MiscMethods import getFileLocations
import python.src.PullTransactions as PullTransactions

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

def orderTrainingData():
    for fileName in os.listdir("TrainingData"):
        fileContent = open(f"TrainingData\\{fileName}", "r", newline="")

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

        with open(f"TrainingData\\{fileName}", "w", newline="") as file:
            file.write("Description, Label\n")

            for index in range(len(output)):
                if index == len(output) - 1: file.write(output[index])
                else: file.write(f"{output[index]}\n")
        
if __name__ == "__main__": 
    findNewTransactionTypes()

    if len(sys.argv) > 1 and sys.argv[1].lower() == "-order":
        orderTrainingData()