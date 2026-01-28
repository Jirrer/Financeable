from enum import Enum
from pathlib import Path
import json

from src import GenerateData # type: ignore
from src import MiscMethods # tpee:ignore

def sendReport(monthYear: str, *tags) -> bool:
    if not MiscMethods.isDate(monthYear): return False

    if GenerateData.Run(monthYear, tags): return True
    else: return False

def pullMonthYearData(**pullType) -> str | bool:    
    if "year" in pullType:
        with open('data\\Months.json', 'r', newline='') as file:
            data = json.load(file)

        return json.dumps({key: val for key, val in data.items() if int(key[3:]) == pullType["year"]})

    elif "range" in pullType:
        startDate, endDate = pullType["range"]

        with open('data\\Months.json', 'r', newline='') as file:
            data = json.load(file)

        if startDate not in data:
            data[startDate] = {}

        sortedData = MiscMethods.sortMonthJson(data)

        filledInData = MiscMethods.fillMonthYearGaps(sortedData)

        dataList = list(filledInData.items())

        startSplice, endSplice = 0, 0

        for index in range(len(dataList)):
            endSplice += 1

            if dataList[index][0] == startDate: startSplice = index
            if dataList[index][0] == endDate: break 

        return json.dumps(dict(dataList[startSplice:endSplice]))
    
    return False

def pullUserData():
    pass