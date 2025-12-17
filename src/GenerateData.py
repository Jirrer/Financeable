import joblib, os, json, csv, sys

with open('supported_banks.json', 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

class Purchase:
    def __init__(self, purchaseValue, purchaseType, purchaseDate, purchaseInfo):
        self.value = purchaseValue
        self.category = purchaseType
        self.date = purchaseDate
        self.info = purchaseInfo

class Month_Report:
    def __init__(self, date: str, loss: float, gain: float, profit: float, purchases: list):
        self.date = date
        self.loss = loss
        self.gain = gain
        self.profit_loss = profit
        self.categories = self.getCategories(purchases)

    def getCategories(self, purchases: list):
        output = {}

        for purchase in purchases:
            if purchase.category in output:
                output[purchase.category] += float(purchase.value)
            else:
                output[purchase.category] = float(purchase.value)

def main(vectorizer, clf, monthYear: str):    
    csvFileLocations = getFileLocations()

    rawPurchases = getRawPurchases(csvFileLocations)

    # Only losses should be counted when created spending habbit charts
    rawGains, rawLosses = getRawGains(rawPurchases), getRawLosses(rawPurchases)

    categorizedPurchases = categorizePurchases(rawLosses, clf, vectorizer)

    monthLosses, monthGains = float(getMonthLoss(categorizedPurchases)), float(getMonthGain(rawGains))

    profit = monthGains + monthLosses

    monthReport = Month_Report(monthYear, monthLosses, monthGains, profit, categorizedPurchases)

    if pushData(monthReport):
        print(" * Ran Month Report")

def getFileLocations() -> list[tuple[str, str]]:
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

def getRawPurchases(csvFiles: list[tuple[int, str]]):
    purchases = []

    for bank, filePath in csvFiles:
        with open(filePath, 'r', newline='') as file:
            reader = csv.reader(file)

            if jsonData[bank]['header']:
                next(reader) 

            dateIndex, infoIndex, valueIndex = None, None, None

            bankFormat = jsonData[bank]['format']

            reversePayents = jsonData[bank]['reverseValues']

            # Every bank's csv reports will have different number and order of columns
            # These need to be stated in "supported_banks.json"
            for index in range(len(bankFormat)):
                if bankFormat[index] == 'date': dateIndex = index
                elif bankFormat[index] == 'info': infoIndex = index
                elif bankFormat[index] == 'value': valueIndex = index

            for row in reader:
                rowDate = row[dateIndex]
                rowInfo = row[infoIndex]

                if (reversePayents): # Some banks include a "-" for their purchases' values
                    rowValue = f'-{row[valueIndex]}'
                else:
                    rowValue = row[valueIndex]

                purchases.append((rowValue, rowDate, rowInfo))

    return purchases

def getRawLosses(rawPurchases):
    losses = []

    for purchaseTuple in rawPurchases:
        if float(purchaseTuple[0]) < 0:
            losses.append(Purchase(purchaseTuple[0], None, purchaseTuple[1], purchaseTuple[2]))

    return losses

def getRawGains(rawPurchases):
    gains = []

    for purchaseTuple in rawPurchases:
        if float(purchaseTuple[0]) >= 0:
            gains.append(Purchase(purchaseTuple[0], None, purchaseTuple[1], purchaseTuple[2]))

    return gains

def categorizePurchases(purchases: list, clf, vectorizer) -> list:
    purchaseDescriptions = [purchase.info for purchase in purchases]

    try:
        strsCategories = clf.predict(vectorizer.transform(purchaseDescriptions))
    
    except ValueError as e:
        if "Found array with 0 sample(s)" in e.args[0]:
            print("Empty Data Folder - Script Ended Early")
            sys.exit(2)

    for index in range(len(purchases)):
        purchases[index].category = strsCategories[index]

    return purchases

def getMonthLoss(puchasesInput: list) -> float:
    total = 0.0

    for purchase in puchasesInput:
        if isFloat(purchase.value): total += float(purchase.value)
    
    return total

def getMonthGain(purchasesInput: list):
    total = 0.0
    
    for purchase in purchasesInput:
        if float(purchase.value) > 0:
            total += float(purchase.value)

    return total

def isFloat(string: str):
    try:
        float(string)
        return '.' in string
    
    except ValueError:
        return False

def pushData(report: Month_Report):
    filePath = 'data\\userInfo.json'

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # if file is empty
    else:
        data = []

    newMonth = {}
    
    newMonth["Losses"] = report.loss

    newMonth["Gains"] = report.gain

    newMonth["Profit/Loss"] = report.profit_loss

    newMonth["Categories"] = report.categories

    data[report.date] = newMonth

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return True

def clearDataFiles():
    filePaths = [path[1] for path in getFileLocations()]
    
    for path in filePaths:
        os.remove(path)
    
if __name__ == "__main__":
    vectorizer = joblib.load('data\\vectorizer.joblib'); print(" * Loaded vectorizer")

    clf = joblib.load('data\\classifier.joblib'); print(" * Loaded clf")

    main(vectorizer, clf, "12/2025"); print(" * Script Ended")

    if len(sys.argv) >= 2:
        for tag in sys.argv[1:]:
            match tag.lower():
                case '-delete': clearDataFiles(); print(" * Cleared data CSV files")
                case _: print(f"Tag '{tag}' is not recognized and was not ran")