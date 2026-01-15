import os
from datetime import datetime

def getFileLocations() -> list[tuple[str, str]]: #[(Bank Name, FileName)]
    fileNames = [f for f in os.listdir('ReportData')]

    output = [(pullBankName(file), f'ReportData\\{file}') for file in fileNames if os.path.exists(f'ReportData\\{file}')]

    return output

def pullBankName(fileName: str) -> str:
    if type(fileName) != str: return 'INVALID_BANK'

    for index in range(len(fileName)):
        if fileName[index] == '#': return ''.join(fileName[:index])

    return 'INVALID_BANK'

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