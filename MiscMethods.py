import os
from datetime import datetime

def getFileLocations() -> list[tuple[str, str]]: # refactor
    output = []

    pdfLocation = 'ReportData'

    pdfNames = [f for f in os.listdir(pdfLocation)]

    for file in pdfNames:
        if os.path.exists(f'{pdfLocation}\\{file}'):
            output.append((pullBankName(file), f'{pdfLocation}\\{file}'))

    return output

def pullBankName(fileName: str) -> str:
    output = []

    for letter in fileName:
        if letter == '#': return ''.join(output)

        output.append(letter)

    return "Error pulling bank name"










def isDate(string: str):
    formats = ["%m-%d", "%m-%d-%Y", "%m-%d-%y", "%m/%d", "%m/%d/%Y", "%m/%d/%y"]
    for fmt in formats:
        try:
            datetime.strptime(string, fmt)
            return True
        except ValueError:
            continue
    return False

def isFloat(string: str):
    try:
        float(string)
        return '.' in string
    except ValueError:
        return False

def getThisMonth() -> str:
    now = datetime.now()
    month = now.month  
    year = now.year 

    return (f'{month}/{year}')

def labelToDate(label: str) -> str:
    year = label[0:4]
    month = label[5:7]

    return f'{month}/{year}'

def monthToWord(month: str):
    relation = {
        '01': 'Jan',
        '02': 'Feb',
        '03': 'Mar',
        '04': 'Apr',
        '05': 'May',
        '06': 'Jun',
        '07': 'Jul',
        '08': 'Aug',
        '09': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dev'  
    }

    return relation[month]