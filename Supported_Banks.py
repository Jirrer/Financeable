from enum import Enum
import csv

class Purchase:
    def __init__(self, purchaseValue, purchaseType, purchaseDate, purchaseInfo):
        self.value = purchaseValue
        self.category = purchaseType
        self.date = purchaseDate
        self.info = purchaseInfo

    def __repr__(self):
        return f"value: {self.value} | category: {self.category} | Date: {self.date} | Info: {self.info}"

def run(bankType, fileName: str):
    match (bankType) :
        case "fifth_third": return fifthThird(fileName)
        case "american_express": return americanExpress(fileName)
        case _: return []


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
            output.append(Purchase(row[valueIndex], None, row[dateIndex], row[infoIndex]))
    
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
            if float(row[valueIndex]) > 0.00: output.append(Purchase(f'-{row[valueIndex]}', None, row[dateIndex], row[infoIndex]))

            else: output.append(Purchase(str(abs(float(row[valueIndex]))), None, row[dateIndex], "AMERICAN EXPRESS CREDIT CARD PAYMENT"))

    
    return output