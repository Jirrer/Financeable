import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

transactionFileLocation = 'TrainingData\\TransactionTypeTraining.csv'

df = pd.read_csv(transactionFileLocation)




transactions = df.iloc[:, 0].tolist()

labels = df.iloc[:, 1].tolist()

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    transactions, labels, test_size=0.2, random_state=42
)

# Create a TF-IDF + Logistic Regression classifier
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=200))
])

# Train
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
print(classification_report(y_test, preds))

# DATABASE_LOCATION = 'data\\Financeable.db'
# VECTORIZER_LOCATION = 'data\\vectorizer.joblib'
# CLASSIFIER_LOCATION = 'data\\classifier.joblib'
# TRAINING_DATA_LOCATION = 'data\\Training_Data.csv'

# def main(tag: str):
#     if tag.lower() == "-w":
#         clearOldData()

#     elif tag.lower() == "-a":
#         pass

#     else:
#         print("Error, invalid tag")
#         return
    
#     connection = sqlite3.connect(DATABASE_LOCATION)

#     cursor = connection.cursor()

#     oldText, oldLabels = pullFromDatabase(cursor)

#     newText, newLabels = createNewData(oldText, oldLabels)

#     try:
#         vectorizer = TfidfVectorizer()
#         X = vectorizer.fit_transform(newText)

#         clf = MultinomialNB()
#         clf.fit(X, newLabels)

#         joblib.dump(vectorizer, VECTORIZER_LOCATION)
#         joblib.dump(clf, CLASSIFIER_LOCATION)

#         cursor.executemany("INSERT INTO ML_data (text, label) VALUES (?, ?)", list(zip(newText, newLabels)))

#         print("Model trained and saved successfully!")
    
#     except ValueError:
#         print("Error, number of labels do not match number of texts")

#     connection.commit()
#     connection.close()


# def clearOldData():
#     connection = sqlite3.connect(DATABASE_LOCATION)

#     curser = connection.cursor()

#     curser.execute("DELETE FROM ML_data")
#     curser.execute("DELETE FROM sqlite_sequence WHERE name='ML_data'")

#     connection.commit()

#     curser.execute("VACUUM")

#     connection.close()

#     print("Data Reset.")

# def pullFromDatabase(cursor) -> tuple:
#     cursor.execute("SELECT text, label FROM ML_data")

#     rows = cursor.fetchall()

#     try:
#         textOutput, labelOutput = zip(*rows)

#         textOutput = list(textOutput)
#         labelOutput = list(labelOutput)

#         return (textOutput, labelOutput)
    
#     except ValueError:
#         return ([], [])
    
# def createNewData(oldText: list, oldLabels: list) -> tuple:
#     newText, newLabels = [], []
#     with open(TRAINING_DATA_LOCATION, 'r', newline='') as file:
#         reader = csv.reader(file)

#         for row in reader:
#             newLabels.append(row[0])

#             newText.append(''.join(row[1:]))


#     newText.extend(oldText), newLabels.extend(oldLabels)

#     return (newText, newLabels)

# if __name__ == "__main__":
#     if len(sys.argv) != 2: print("Error, did not include tag")
#     else: main(tag = sys.argv[1])