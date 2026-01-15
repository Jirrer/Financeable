import pandas as pd
import joblib, enum
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class ClassifierType(enum.Enum):
    Transaction = 'Transaction'
    Income = 'Income'
    Purchase = 'Purchase'
    Transfer = 'Transfer'

def buildModel(classifierType:enum.Enum):
    print(f"\nBuilding Model - {classifierType.value}")

    transactionFileLocation = f'TrainingData\\{classifierType.value}Data.csv'

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

    joblib.dump(model, f"classifiers\\{classifierType.value}Classifier.joblib")

if __name__ == "__main__":
    buildModel(ClassifierType.Transaction)
    buildModel(ClassifierType.Income)
    buildModel(ClassifierType.Purchase)
    buildModel(ClassifierType.Transfer)