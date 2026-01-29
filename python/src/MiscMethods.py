import os, operator
from datetime import datetime

def fillMonthYearGaps(data: dict) -> dict:
    try:
        monthYear = list((sortMonthJson(data).keys()))[0]  
    
    except IndexError as e:
        return {}

    while monthYear != getThisMonthYear():
        month, year = int(monthYear[:2]), int(monthYear[3:])

        if month == 12:
            nextMonth = "01"
            nextYear =  str(year + 1)

        elif month > 8:
            nextMonth = str(month + 1)
            nextYear = str(year)

        else:
            nextMonth = f"0{str(month + 1)}"
            nextYear = str(year)

        nextMonthYear = f"{nextMonth}/{nextYear}"

        if (nextMonthYear) not in data:
            data[nextMonthYear] = {}

        monthYear = nextMonthYear

    return sortMonthJson(data)

def sortMonthJson(data: dict) -> dict:
    sortedData = sorted(
        data.items(),
        key=lambda item: datetime(
            year=int(item[0][3:]),
            month=int(item[0][:2]),
            day=1
        ).timestamp()
    )

    return dict(sortedData)

def getFileLocations() -> list[tuple[str, str]]: #[(Bank Name, FileName)]
    fileNames = [f for f in os.listdir('ReportData')]

    output = [(pullBankName(file), f'ReportData\\{file}') for file in fileNames if os.path.exists(f'ReportData\\{file}')]

    return output

def pullBankName(fileName: str) -> str:
    if type(fileName) != str: return 'INVALID_BANK'

    for index in range(len(fileName)):
        if fileName[index] == '#': return ''.join(fileName[:index])

    return 'INVALID_BANK'

def isDate(string: str) -> bool:
    formats = ["%m/%Y", "%m-%d", "%m-%d-%Y", "%m-%d-%y", "%m/%d", "%m/%d/%Y", "%m/%d/%y"]
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

def getThisMonthYear() -> str:
    now = datetime.now()
    month = now.month  
    year = now.year 

    if month < 10: return (f'0{month}/{year}')
    else: return (f'{month}/{year}')

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