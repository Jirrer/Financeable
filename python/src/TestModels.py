import joblib
from python.src.MiscMethods import getFileLocations
import python.src.PullTransactions as PullTransactions

def testTransactionType():
    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    rawTransactions = [t for bank in transactionsByBank for t in bank]
    
    model = joblib.load('classifiers\\TransactionClassifier.joblib')

    for transaction in rawTransactions:
        print(f"{transaction.info}: {model.predict([transaction.info])}")

  
if __name__ == "__main__":
    testTransactionType()