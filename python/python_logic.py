import sys
from pathlib import Path

# python is already in path from Rust

from src import GenerateData # type: ignore

def runReport(monthYear: str, *tags) -> bool:
    if GenerateData.Run(monthYear, tags): return True
    else: return False


