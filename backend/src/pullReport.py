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

    return returnJson(categories)

def getDate(possibleDate: str):
    return possibleDate


def returnJson(categories: dict) -> dict:
    output = {}

    count = 1

    for category in categories.values():
        for value in category:
            output[count] = {
                'test'
            }

            count += 1



    print(output)
    return output


if __name__ == "__main__":
    run(userID=1, inputType='month', date='2026-05', returnType='json')