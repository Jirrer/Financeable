from enum import Enum
from pathlib import Path
import json

from src import GenerateData, MiscMethods # type: ignore

def sendReport(monthYear: str, *tags) -> bool:
    if not MiscMethods.isDate(monthYear): return False

    if GenerateData.Run(monthYear, tags): return True
    else: return False

def pullMonthData(startDate: str, endDate: str):
    if not MiscMethods.isDate(startDate) or not MiscMethods.isDate(endDate):
        return json.dumps({"Error": "Bad Date(s) Given"})

    with open('data\\Months.json', 'r', newline='') as file:
        data = json.load(file)
        
        sortedData = MiscMethods.sortMonthJson(data)

        startSplice, endSplice = 0, 1
        for x in sortedData:
            print((x[0]), (endDate))
            if x[0] == startDate: print("found start")

            elif x[0] == endSplice: break

            endSplice += 1

        for x in sortedData[startSplice: endSplice]:
            print(x[0])

        return json.dumps(dict(sortedData[startSplice: endSplice]))

def pullUserData():
    pass