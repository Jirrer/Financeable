from enum import Enum
from exceptions import *
import sqlite3, os
from dotenv import load_dotenv

load_dotenv()

class InputType(Enum):
    MONTH = 1

class ReturnType(Enum):
    JSON = 1

def run(**data):
    if not data: return None

    if not data['userID']: raise KeyError

    if not data['inputType']: raise KeyError

    match data['inputType'].upper():
        case InputType.MONTH.name: getMonthReport(data)
        case _ : raise KeyError

def getMonthReport(data: dict):
    if not data['date']: raise KeyError

    date = getDate(data['date'])
    
    categories = {'income': None, 'purchase': None, 'transfer': None}

    with sqlite3.connect(os.getenv('Database_Location')) as connection:
        cursor = connection.cursor()

        for category in categories.keys():
            categories[category] = cursor.execute(
                f"SELECT * FROM {category} WHERE user_id = ? AND strftime('%Y-%m', date) = ?;", (data['userID'], date)
                ).fetchall()


    try:
        match data['returnType'].upper():
            case ReturnType.JSON.name: returnType = ReturnType.JSON
            case _: returnType = ReturnType.JSON

    except KeyError:
        returnType = ReturnType.JSON

    match returnType:
        case ReturnType.JSON: return returnJson(categories)

def getDate(possibleDate: str):
    return possibleDate

def returnJson(categories: dict) -> dict:
    purchases = [x[4] for x in categories['purchase']]
    incomes = [x[4] for x in categories['income']]
    external_transfers = [x[4] for x in categories['transfer'] if x[3].lower() == 'external']

    output = {
        'profit': sum(purchases) + sum(incomes) + sum(external_transfers),
        'losses': sum(purchases) + sum([x for x in external_transfers if x < 0]),
        'gains': sum(incomes) + sum([x for x in external_transfers if x > 0]),
        'purchase': getCategories(categories['purchase']),
        'income': getCategories(categories['income']),
        'transfer': getCategories(categories['transfer'])
    }
    
    return output

def getCategories(arr: list) -> dict:
    output = {}

    for row in arr:
        category = row[3]

        value = row[4]

        if category in output:
            output[category] += value
        else:
            output[category] = value

    return output