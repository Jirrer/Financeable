import sqlite3, os, re

from enum import Enum
from dotenv import load_dotenv

from src.exceptions import *

load_dotenv()

class ReturnType(Enum):
    JSON = 1

class Transaction:
    def __init__(self, group: str, value: float, description:str, category: str):
        self.group = group
        self.value = value
        self.description = description
        self.category = category

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

            for x in output:
                print(output[x])
            return output

        if int(dateStart.month) < 12:
            dateStart.month = str(int(dateStart.month) + 1).zfill(2)
        else:
            dateStart.month = '01'
            dateStart.year = str(int(dateStart.year) + 1)  

def getTransactionsFromDB(userID, date: Date) -> dict[str, tuple[Transaction]]:
    categories = {'income': None, 'purchase': None, 'transfer': None}

    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        for category in categories.keys():
            databaseOutput = cursor.execute(
                f"SELECT * FROM {category} WHERE user_id = ? AND strftime('%Y-%m', date) = ?;", (userID, f'{date.year}-{date.month}')
                ).fetchall()  

            categories[category] = tuple([Transaction(category, float(output[4]), output[5], output[3]) for output in databaseOutput])

    return categories

def formatForJson(categories: dict[str, tuple[Transaction]]) -> dict:
    purchases = [purchase.value for purchase in categories['purchase']]
    incomes = [income.value for income in categories['income']]
    transfers = [transfer.value for transfer in categories['transfer']]

    output = {
        'profit': sum(purchases) + sum(incomes) + sum(transfers),
        'losses': sum(purchases) + sum([x for x in transfers if x < 0]),
        'gains': sum(incomes) + sum([x for x in transfers if x > 0]),
        'purchase': filterByCategory(categories['purchase']),
        'income': filterByCategory(categories['income']),
        'transfer': filterByCategory(categories['transfer'])
    }

    return output

def filterByCategory(arr: list[Transaction]) -> dict[str, float]:
    output = {}

    for row in arr:
        if row.category in output:
            output[row.category] += row.value
        else:
            output[row.category] = row.value

    return output