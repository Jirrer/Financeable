import joblib
from GenerateData import getRawPurchases, getFileLocations, categorizePurchases, getRawLosses

def testModel():
    rawPurchases = getRawLosses(getRawPurchases(getFileLocations()))
    catPurchases = categorizePurchases(rawPurchases, joblib.load('data\\classifier.joblib'), joblib.load('data\\vectorizer.joblib'))

    max_len = max(len(p.category) for p in catPurchases)

    print("-" * max_len + "-|-" + "-" * 100)

    for purchase in catPurchases:
        print(f"{purchase.category:<{max_len}} | {purchase.info}")
    
