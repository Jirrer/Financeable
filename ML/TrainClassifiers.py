import os, sqlite3, joblib

from pathlib import Path
from enum import Enum, auto
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC
from collections import Counter

load_dotenv()

class Transaction:
    def __init__(self, group, description, category):
        self.group = group
        self.description = description
        self.category = category

    def __repr__(self):
        return f'{self.group} - {self.category} - {self.description}'

class ClassifierType(Enum):
    TRANSACTION = auto()
    INCOME = auto()
    PURCHASE = auto()
    TRANSFER = auto()

class Transaction_Thresholds(Enum):
    MIN_F1          = 0.95  
    MIN_SUPPORT     = 10    
    MIN_ACCURACY    = 0.97
    MIN_WEIGHTED_F1 = 0.97
    MIN_MACRO_F1    = 0.90 

class Income_Thresholds(Enum):
    MIN_F1          = 0.95  
    MIN_SUPPORT     = 10    
    MIN_ACCURACY    = 0.97
    MIN_WEIGHTED_F1 = 0.97
    MIN_MACRO_F1    = 0.90 

class Purchase_Thresholds(Enum):
    MIN_F1          = 0.95  
    MIN_SUPPORT     = 10    
    MIN_ACCURACY    = 0.97
    MIN_WEIGHTED_F1 = 0.97
    MIN_MACRO_F1    = 0.90 

def run():
    print("running")

    purchases = tuple(pullTableFromDb(ClassifierType.PURCHASE))
    incomes = tuple(pullTableFromDb(ClassifierType.INCOME))
    transfers = tuple(pullTableFromDb(ClassifierType.TRANSFER))

    transactions = []
    for p in purchases:
        transactions.append(Transaction('transaction', p.description, 'purchase'))

    for i in incomes:
        transactions.append(Transaction('transaction', i.description, 'income')) 

    for t in transfers:
        transactions.append(Transaction('transaction', i.description, 'transfer')) 

    print('Training - Transactions'); trainModel(ClassifierType.TRANSACTION, transactions)
    print('Training - Purchases'); trainModel(ClassifierType.PURCHASE, purchases)
    print('Training - Incomes'); trainModel(ClassifierType.INCOME, incomes)

def pullTableFromDb(classifierType: ClassifierType) -> tuple[Transaction]:
    match classifierType:
        case ClassifierType.INCOME: table = 'income'
        case ClassifierType.PURCHASE: table = 'purchase'
        case _: raise ValueError

    with sqlite3.connect(database_location) as connection:
        cursor = connection.cursor()

        return (Transaction(table, row[0], row[1]) for row in cursor.execute(F'SELECT info, category FROM {table}').fetchall())
    
def trainModel(classifierType: ClassifierType, data: tuple[Transaction]) -> Pipeline:
    info, labels = [], []

    for t in data:
        if not t.category or not t.description:
            continue

        info.append(t.description)
        labels.append(t.category)

    counts = Counter(labels)
    min_count = min(counts.values()) if counts else 0
    stratify_labels = labels if min_count >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        info, labels, test_size=0.2, random_state=42, stratify=stratify_labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2))),
        ("clf", LinearSVC(class_weight="balanced"))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    match classifierType:
        case ClassifierType.TRANSACTION: 
            if testModel(Transaction_Thresholds, y_test, predictions):
                saveModel(os.getenv('TRANSACTION_CLASSIFIER'), model)

        case ClassifierType.PURCHASE:
            if testModel(Purchase_Thresholds, y_test, predictions): 
                saveModel(os.getenv('PURCHASE_CLASSIFIER'), model)

        case ClassifierType.INCOME: 
            if testModel(Income_Thresholds, y_test, predictions):
                saveModel(os.getenv('INCOME_CLASSIFIER'), model)

        case _: raise ValueError

def testModel(threshholds: Transaction_Thresholds, y_test, predictions):
    report = classification_report(y_test, predictions, output_dict=True)

    MIN_F1          = threshholds.MIN_F1.value
    MIN_SUPPORT     = threshholds.MIN_SUPPORT.value
    MIN_ACCURACY    = threshholds.MIN_ACCURACY.value
    MIN_WEIGHTED_F1 = threshholds.MIN_WEIGHTED_F1.value

    failures = []

    skip_keys = {"accuracy", "macro avg", "weighted avg"}
    for cls, metrics in report.items():
        if cls in skip_keys:
            continue
        if metrics["support"] < MIN_SUPPORT:
            continue
        if metrics["f1-score"] < MIN_F1:
            failures.append(f"  {cls}: F1 = {metrics['f1-score']:.2f} (threshold {MIN_F1})")

    if report["accuracy"] < MIN_ACCURACY:
        failures.append(f"  accuracy: {report['accuracy']:.2f} (threshold {MIN_ACCURACY})")

    if report["weighted avg"]["f1-score"] < MIN_WEIGHTED_F1:
        failures.append(f"  weighted F1: {report['weighted avg']['f1-score']:.2f} (threshold {MIN_WEIGHTED_F1})")

    print(classification_report(y_test, predictions))

    if failures:
        print("FAIL — metrics below threshold:")
        for f in failures:
            print(f)
        return False

    print("PASS — all metrics within threshold")
    return True

def saveModel(filePath: str, model: Pipeline):
    Path(filePath).unlink(missing_ok=True)

    print('saving to', filePath)

    joblib.dump(model, filePath)

if __name__ == "__main__":
    database_location = os.getenv('DATABASE_LOCATION')

    if not database_location:
        exit(1)

    run()