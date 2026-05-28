import sqlite3, os, re

from enum import Enum
from dotenv import load_dotenv

from src.exceptions import *

load_dotenv()

class ReturnType(Enum):
    JSON = 1

class Date:
    def __init__(self, inputStr: str):
        splitResult = re.split(r'[-/]', inputStr)
        
        if len(splitResult[0]) == 4 and len(splitResult[1]) == 2:
            self.year, self.month = splitResult[0], splitResult[1]

        elif len(splitResult[0]) == 2 and len(splitResult[1]) == 4:
            self.month, self.year = splitResult[0], splitResult[1]

        else:
            raise BadDateInput
        
    def __lt__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        
        if self.year != other.year:
            return int(self.year) < int(other.year)
        
        else:
            return int(self.month) < int(other.month)
        
    def ___gt__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        
        if self.year != other.year:
            return int(self.year) > int(other.year)
        
        else:
            return int(self.month) > int(other.month)
        
    def __eq__(self, value):
        if not isinstance(value, Date):
            raise NotImplemented

        return int(self.month) == int(value.month) and int(self.year) == int(value.year)


def run(userID: int, dateStartInput: str, dateEndInput: str, returnType: ReturnType) -> dict:
    dateStart = Date(dateStartInput)
    dateEnd = Date(dateEndInput)

    try:
        match returnType.upper():
            case ReturnType.JSON.name: returnType = ReturnType.JSON
            case _: returnType = ReturnType.JSON

    except AttributeError:
        returnType = ReturnType.JSON

    output = {}

    while True:
        output[f'{dateStart.month}/{dateStart.year}'] = getDatabaseOutput(userID, dateStart)

        match returnType:
            case ReturnType.JSON: 
                output[f'{dateStart.month}/{dateStart.year}'] = returnJson(output[f'{dateStart.month}/{dateStart.year}'])

        if dateStart == dateEnd:
            return output

        if int(dateStart.month) < 12:
            dateStart.month = str(int(dateStart.month) + 1)
        else:
            dateStart.month = '01'
            dateStart.year = str(int(dateStart.year) + 1)  

def getDatabaseOutput(userID, date: Date):
    categories = {'income': None, 'purchase': None, 'transfer': None}

    with sqlite3.connect(os.getenv('Database_Location')) as connection:
        cursor = connection.cursor()

        for category in categories.keys():
            categories[category] = cursor.execute(
                f"SELECT * FROM {category} WHERE user_id = ? AND strftime('%Y-%m', date) = ?;", (userID, f'{date.year}-{date.month}')
                ).fetchall()    

    return categories

def returnJson(categories: dict) -> dict:
    print(categories)
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

if __name__ == "__main__":
    test = run(1, Date('04/2026'), Date('04/2026'), None)

    for x in test:
        print(test[x])