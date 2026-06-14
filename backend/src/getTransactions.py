import csv, io, joblib, os, pandas as pd, logging

from enum import Enum, auto
from werkzeug.datastructures import FileStorage
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

import src.NormalizeData as NormalizeData
import src.exceptions as exceptions
from models import TESTING_MODEL

class ClassifierType(Enum):
    Transaction = auto()
    Income = auto()
    Purchase = auto()

class TransactionType(Enum):
    Income = 'income'
    Purchase = 'purchase'
    Transfer = 'transfer'
    Undefined = 'Undefined'

class PurchaseType(Enum):
    Misc = 'misc'
    Food_Drink = 'food_drink'
    Gas = 'gas'

class IncomeType(Enum):
    Payroll = 'payroll'
    Passive = 'passive'

class TransferType(Enum):
    Transfer = 'transfer'
 
class Transaction:
    def __init__(self, transactionValue: float, tranasctionDate, transactionInfo):
        self.value = transactionValue
        self.date = tranasctionDate
        self.info = transactionInfo
        self.group = 'Ungrouped'
        self.category = 'Uncategorized'

    def __repr__(self):
        return f"({self.group}) value: {self.value} | category: {self.category} | Date: {self.date} | Info: {self.info}"
    
class ReturnType(Enum):
    JSON = auto()

load_dotenv()

def buildDevModel(classifierType: ClassifierType):
    match classifierType:
        case ClassifierType.Transaction: trainingData = TESTING_MODEL().transaction
        case ClassifierType.Income: trainingData = TESTING_MODEL().income
        case ClassifierType.Purchase: trainingData = TESTING_MODEL().purchase
        case _: raise NotImplemented

    df = pd.DataFrame(trainingData[1:], columns=trainingData[0])

    transactions = df.iloc[:, 0].tolist()

    labels = df.iloc[:, 1].tolist()

    stratify_labels = labels if df.iloc[:, 1].value_counts().min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        transactions, labels, test_size=0.2, random_state=42, stratify=stratify_labels
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2))),
        ("clf", LinearSVC(class_weight="balanced"))
    ])

    model.fit(X_train, y_train)

    return model

def createClassifier(classifierType: ClassifierType):
    if os.getenv('ENVIRONMENT_TYPE') == 'DEV':
        logging.warning(f"Development environment - building {classifierType.name} classifier example")

        match classifierType:
            case ClassifierType.Transaction: return buildDevModel(ClassifierType.Transaction)
            case ClassifierType.Purchase: return buildDevModel(ClassifierType.Purchase)
            case ClassifierType.Income: return buildDevModel(ClassifierType.Income)
            case _: raise NotImplemented
    elif os.getenv('ENVIRONMENT_TYPE') == 'PROD':
        match classifierType:
                case ClassifierType.Transaction: return joblib.load(os.getenv('TRANSACTION_CLASSIFIER'))
                case ClassifierType.Purchase: return joblib.load(os.getenv('PURCHASE_CLASSIFIER'))
                case ClassifierType.Income: return joblib.load(os.getenv('INCOME_CLASSIFIER'))     
                case _: raise NotImplemented
            
    else:
        raise NotImplemented('Invalid value inside of .env file')


Transaction_Model = createClassifier(ClassifierType.Transaction)
Income_Model = createClassifier(ClassifierType.Income)
Purchase_Model = createClassifier(ClassifierType.Purchase)

def run(csvFile: FileStorage, returnType: ReturnType) -> bool:
    transactions = pullTransactions(csvFile)

    transactions = groupTransactions(transactions)

    transactions = categorizeTransactions(transactions)

    return returnTransactions(transactions, returnType)

def pullTransactions(file: FileStorage) -> list[Transaction]:
    dateExamples = {'date'}
    descriptionExamples = {'description'}
    amountExamples = {'amount'}

    dateIndex = -1
    descriptionIndex = -1
    amountIndex = -1

    stream = io.StringIO(file.stream.read().decode("utf-8"), newline="")
    
    reader = csv.reader(stream)
    
    firstRow = next(reader)

    for index in range(len(firstRow)):
        if firstRow[index].lower() in dateExamples: dateIndex = index
        elif firstRow[index].lower() in descriptionExamples: descriptionIndex = index
        elif firstRow[index].lower() in amountExamples: amountIndex = index 

    if dateIndex == -1 or descriptionIndex == -1 or amountIndex == -1:
        raise exceptions.MissingHeader

    transactions = []

    for row in reader:
        if not NormalizeData.isValidDate(row[dateIndex]):
            raise exceptions.BadDateInput

        transactions.append(Transaction(float(row[amountIndex]), NormalizeData.formatDate(row[dateIndex]), row[descriptionIndex]))   

    file.close()

    return transactions

def groupTransactions(transactions: list[Transaction]) -> list[Transaction]:
    for t in transactions:
        t.group = Transaction_Model.predict([t.info])[0]

        match t.group:
            case TransactionType.Income.value: t.value = abs(t.value)
            case TransactionType.Purchase.value: t.value = -abs(t.value)
            case TransactionType.Transfer.value: continue
            case TransactionType.Undefined.value: raise exceptions.BadTransactionType 

    return transactions

def categorizeTransactions(transactions: list[Transaction]) -> list[Transaction]:
    for t in transactions:
        match (t.group):
            case TransactionType.Income.value: 
                t.category = Income_Model.predict([t.info])[0]
                
            case TransactionType.Purchase.value: 
                t.info = NormalizeData.normalizePurchase(t.info)
                t.category = Purchase_Model.predict([t.info])[0]

            case TransactionType.Transfer.value: 
                t.category = TransferType.Transfer.value

            case _: 
                t.category = TransactionType.Undefined.value

    return transactions    

def returnTransactions(transactions: list, returnType: ReturnType):
    match (returnType):
        case returnType.JSON: return returnJson(transactions)
        case _: raise ValueError

def returnJson(transactions: list[Transaction]) -> dict:
    jsonOutput = {}

    for index in range(len(transactions)):
        jsonOutput[index + 1] = {
            'value': transactions[index].value,
            'date': transactions[index].date,
            'info': transactions[index].info,
            'group': transactions[index].group,
            'category': transactions[index].category
        }

    return jsonOutput