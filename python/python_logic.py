from enum import Enum
from pathlib import Path
import joblib

from src import GenerateData # type: ignore

def sendReport(monthYear: str, *tags) -> bool:
    if GenerateData.Run(monthYear, tags): return True
    else: return False

def pullMonthData():
    pass


def pullUserData():
    pass