from enum import Enum
import csv

class TransactionType(Enum):
    Income = 1
    Purchase = 2
    MISC = 3

class PurchaseType(Enum):
    pass

class IncomeType(Enum):
    pass
 
class Transaction:
    def __init__(self, transactionValue: float, tranasctionDate, transactionInfo):
        self.value = transactionValue
        self.date = tranasctionDate
        self.info = transactionInfo
        self.group = None
        self.category = None

    def __repr__(self):
        return f"('{self.group}') value: {self.value} | category: {self.category} | Date: {self.date} | Info: {self.info}"

def run(bankType, fileName: str):
    match (bankType) :
        case "fifth_third": return fifthThird(fileName)
        case "american_express": return americanExpress(fileName)
        case _: print(f"Could not find bank - '{bankType}'"); return []


def fifthThird(fileName):
    output, format = [], ("date", "info", "check", "value")

    with open(fileName, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader) 

        dateIndex, infoIndex, valueIndex = None, None, None

        for index in range(len(format)):
            if format[index] == 'date': dateIndex = index
            elif format[index] == 'info': infoIndex = index
            elif format[index] == 'value': valueIndex = index

        for row in reader:
            output.append(Transaction(row[valueIndex], row[dateIndex], row[infoIndex]))
    
    return output

def americanExpress(fileName):
    output, format = [], ("Date","Description","Amount","Extended Details","Appears On Your Statement As","Address","City/State","Zip Code","Country","Reference","Category")

    with open(fileName, 'r', newline='') as file:
        reader = csv.reader(file)

        next(reader) 

        dateIndex, infoIndex, valueIndex = None, None, None

        for index in range(len(format)):
            if format[index] == 'Date': dateIndex = index
            elif format[index] == 'Category': infoIndex = index
            elif format[index] == 'Amount': valueIndex = index

        for row in reader:
            if float(row[valueIndex]) > 0.00: output.append(Transaction(f'-{row[valueIndex]}', None, row[dateIndex], row[infoIndex]))

            else: output.append(Transaction(str(abs(float(row[valueIndex]))), row[dateIndex], "AMERICAN EXPRESS CREDIT CARD PAYMENT"))

    
    return output