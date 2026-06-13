import re

from enum import Enum
from dotenv import load_dotenv
from sqlalchemy import extract

from src.exceptions import *

from models import db, Purchase, Transfer, Income

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
    categories = {'income': Income, 'purchase': Purchase, 'transfer': Transfer}
    result = {}

    for category, model in categories.items():
        rows = model.query.filter(
            model.user_id == userID,
            extract('year', model.date) == date.year,
            extract('month', model.date) == date.month
        ).all()

        result[category] = tuple([
            Transaction(category, float(row.value), row.info, row.category)
            for row in rows
        ])

    return result

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