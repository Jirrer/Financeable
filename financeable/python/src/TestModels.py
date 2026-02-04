import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

import joblib
from python.src.MiscMethods import getFileLocations
import python.src.PullTransactions as PullTransactions

def testTransactionType():
    csvFileLocations = getFileLocations()

    transactionsByBank = [PullTransactions.run(c[0], c[1]) for c in csvFileLocations]

    rawTransactions = [t for bank in transactionsByBank for t in bank]
    
    model = joblib.load(str(BASE_DIR / "classifiers" / "TransactionClassifier.joblib"))

    for transaction in rawTransactions:
        print(f"{transaction.info}: {model.predict([transaction.info])}")

  
if __name__ == "__main__":
    testTransactionType()