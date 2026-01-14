import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def buildTransactionModel():
    transactionFileLocation = 'TrainingData\\TransactionTypeTraining.csv'

    df = pd.read_csv(transactionFileLocation)

    transactions = df.iloc[:, 0].tolist()

    labels = df.iloc[:, 1].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        transactions, labels, test_size=0.2, random_state=42, stratify=labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("rf", RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    joblib.dump(model, "classifiers\\TransactionClassifier.joblib")





if __name__ == "__main__":
    pass
