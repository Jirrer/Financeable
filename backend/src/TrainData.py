import pandas as pd
import joblib, enum
import sys, re, csv
from pathlib import Path
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE_DIR = Path(__file__).resolve().parents[2]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

class ClassifierType(enum.Enum):
    Transaction = 'Transaction'
    Income = 'Income'
    Purchase = 'Purchase'
    Transfer = 'Transfer'

TRAINING_DIR = BASE_DIR / "TrainingData"
CLASSIFIERS_DIR = BASE_DIR / "classifiers"

def buildAllModels():
    buildModel(ClassifierType.Transaction)
    buildModel(ClassifierType.Income)
    buildModel(ClassifierType.Purchase)
    buildModel(ClassifierType.Transfer)

def buildModel(classifierType: ClassifierType):
    print(f"\nBuilding Model - {classifierType.value}")

    transactionFileLocation = str(TRAINING_DIR / f"{classifierType.value}Data.csv")

    df = pd.read_csv(transactionFileLocation)

    transactions = df.iloc[:, 0].tolist()

    labels = df.iloc[:, 1].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        transactions, labels, test_size=0.2, random_state=42, stratify=labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2))),
        ("clf", LinearSVC(class_weight="balanced"))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    joblib.dump(model, str(CLASSIFIERS_DIR / f"{classifierType.value}Classifier.joblib"))

def updateModel(edits):
    dataToDelete = {}
    dataToAdd = {}

    for e in edits:
        oldMatch = re.search(r'\(([^)]+)\)', str(e[0]))
        newMatch = re.search(r'\(([^)]+)\)', str(e[1]))
        if not oldMatch or not newMatch:
            continue

        oldType = oldMatch.group(1)
        newType = newMatch.group(1)
        
        if oldType in dataToDelete:
            dataToDelete[oldType].append(e[0])
        else:
            dataToDelete[oldType] = [e[0]]

        if newType in dataToAdd:
            dataToAdd[newType].append(e[1])
        else:
            dataToAdd[newType] = [e[1]]
    
    deleteData(dataToDelete)

    addData(dataToAdd)

    buildAllModels()

def deleteData(data: dict):
    for classifier, entries in data.items():
        file_path = TRAINING_DIR / f"{classifier}Data.csv"
        if not file_path.exists():
            continue

        # Compare against normalized string values from data[classifier][n].
        targets = {str(entry).strip() for entry in entries}
        if not targets:
            continue

        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

        if not rows:
            continue

        header = rows[0]
        kept_rows = [header]

        for row in rows[1:]:
            if not row:
                continue

            row_value = str(row[0]).strip()
            if row_value in targets:
                continue

            kept_rows.append(row)

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(kept_rows)

def addData(data: dict):
    for classifier, entries in data.items():
        file_path = TRAINING_DIR / f"{classifier.capitalize()}Data.CSV"
        if not file_path.exists():
            file_path = TRAINING_DIR / f"{classifier.capitalize()}Data.csv"
        if not file_path.exists():
            continue

        rows_to_add = []
        for entry in entries:
            entry_text = str(entry)
            category_match = re.search(r"\|\s*category:\s*([^|]+)\|", entry_text, re.IGNORECASE)
            info_match = re.search(r"\|\s*Info:\s*(.+)$", entry_text, re.IGNORECASE)
            if not category_match or not info_match:
                continue

            category = category_match.group(1).strip()
            info = info_match.group(1).strip()
            if not info:
                continue

            rows_to_add.append([info, category])

        if not rows_to_add:
            continue

        needs_newline = False
        if file_path.exists():
            with open(file_path, "rb") as check_file:
                check_file.seek(0, 2)
                if check_file.tell() > 0:
                    check_file.seek(-1, 2)
                    needs_newline = check_file.read(1) not in (b"\n", b"\r")

        with open(file_path, "a", newline="", encoding="utf-8") as file:
            if needs_newline:
                file.write("\n")
            writer = csv.writer(file)
            writer.writerows(rows_to_add)

if __name__ == "__main__":
    buildAllModels()