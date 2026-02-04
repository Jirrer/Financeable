import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

VENV_SITE_PACKAGES = BASE_DIR / "env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

from src import GenerateData # type: ignore
from src import MiscMethods # type:ignore

DATA_DIR = BASE_DIR / "data"

def sendReport(monthYear: str, *tags) -> bool:
    if not MiscMethods.isDate(monthYear): return False

    if GenerateData.Run(monthYear, tags): return True
    else: return False

def pullMonthYearData(**pullType) -> str | bool:    
    if "year" in pullType:
        with open(str(DATA_DIR / "Months.json"), 'r', newline='') as file:
            data = json.load(file)

        sortedData = MiscMethods.sortMonthJson(data)

        fillGaps = MiscMethods.fillMonthYearGaps(sortedData)

        filtedOutYear = {key: val for key, val in fillGaps.items() if int(key[3:]) == pullType["year"]}

        return json.dumps(filtedOutYear)

    elif "range" in pullType:
        startDate, endDate = pullType["range"]

        with open(str(DATA_DIR / "Months.json"), 'r', newline='') as file:
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