import json, sys, os
from pathlib import Path

# To-Do: erorr handle when json data is not formated (breaks frontend)

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

### Accepted Types ###
# year = YYYY
# range = ["MM/YYYY", "MM/YYYY"]

def pullMonthYearData(**pullType) -> str | bool:    
    if "year" in pullType:
        with open(str(DATA_DIR / "Months.json"), 'r', newline='') as file:
            data = json.load(file)

        sortedData = MiscMethods.sortMonthJson(data)

        fillGaps = MiscMethods.fillMonthYearGaps(sortedData)

        output = {key: val for key, val in fillGaps.items() if int(key[3:]) == pullType["year"]}

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

        output = dict(dataList[startSplice:endSplice])
    
    if not output:
        return False
    
    return organizeOutput(output)

def organizeOutput(output: dict) -> dict:
    newOutput = {'profits': [], 'categories': []}

    for key, val in output.items():
        try: newOutput["profits"].append((key, val['Profit/Loss']))
        except KeyError: newOutput["profits"].append((key, {}))

        try: newOutput["categories"].append((key, output[key]["Purchase"]))
        except KeyError: newOutput["categories"].append((key, {}))

    return newOutput

def pullSumbittedFiles():
    fileLocation = f'{BASE_DIR}\\ReportData'

    return [f for f in os.listdir(fileLocation)]    


def pullUserData():
    pass

if __name__ == "__main__":
    # print((pullMonthYearData(range = ["01/2025", "12/2025"])))
    print(pullSumbittedFiles())