import sqlite3, os, re

from enum import Enum
from dotenv import load_dotenv

from src.exceptions import *

load_dotenv()

#To-Do: build tests

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

        self.month = str(int(self.month)).zfill(2)
        
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

    except AttributeError: # Defaults to JSON
        returnType = ReturnType.JSON

    output = {}

    # Essentially a 'do-while' to ensure the loop still runs when startDate and endDate are the same
    while True: 
        output[f'{dateStart.month}/{dateStart.year}'] = getTransactionsFromDB(userID, dateStart)

        match returnType:
            case ReturnType.JSON: 
                output[f'{dateStart.month}/{dateStart.year}'] = formatForJson(output[f'{dateStart.month}/{dateStart.year}'])

        if dateStart == dateEnd:
            return output

        if int(dateStart.month) < 12:
            dateStart.month = str(int(dateStart.month) + 1).zfill(2)
        else:
            dateStart.month = '01'
            dateStart.year = str(int(dateStart.year) + 1)  

def getTransactionsFromDB(userID, date: Date) -> dict:
    categories = {'income': None, 'purchase': None, 'transfer': None}

    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        for category in categories.keys():
            categories[category] = cursor.execute(
                f"SELECT * FROM {category} WHERE user_id = ? AND strftime('%Y-%m', date) = ?;", (userID, f'{date.year}-{date.month}')
                ).fetchall()    

    return categories

def formatForJson(categories: dict) -> dict:
    purchases = [x[4] for x in categories['purchase']]
    incomes = [x[4] for x in categories['income']]
    external_transfers = [x[4] for x in categories['transfer'] if x[3].lower() == 'external']

    output = {
        'profit': sum(purchases) + sum(incomes) + sum(external_transfers),
        'losses': sum(purchases) + sum([x for x in external_transfers if x < 0]),
        'gains': sum(incomes) + sum([x for x in external_transfers if x > 0]),
        'purchase': filterByCategory(categories['purchase']),
        'income': filterByCategory(categories['income']),
        'transfer': filterByCategory(categories['transfer'])
    }
    
    return output

def filterByCategory(arr: list) -> dict:
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