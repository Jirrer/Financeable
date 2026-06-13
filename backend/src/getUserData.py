import sqlite3, os

from dotenv import load_dotenv

load_dotenv()

def run(userID: int) -> dict:
    allData = pullAllData(userID)
    
    output = {
        "NetWorth": calculateNetworth(allData),
        "Salary": findSalary(allData),
        "Emergency Fund": getEmergencyFund(allData)
    }


    return output

def pullAllData(userID: int):
    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        query = '''
            SELECT 'purchase' AS type, p.id, p.date, p.category, p.value, p.info
            FROM purchase p
            WHERE p.user_id = ?

            UNION ALL

            SELECT 'income' AS type, i.id, i.date, i.category, i.value, i.info
            FROM income i
            WHERE i.user_id = ?

            UNION ALL

            SELECT 'transfer' AS type, t.id, t.date, t.category, t.value, t.info
            FROM transfer t
            WHERE t.user_id = ?

            ORDER BY date DESC;
        '''

        return cursor.execute(query, (userID, userID, userID)).fetchall()

def calculateNetworth(allData: list[tuple]) -> dict:
    # cash = sum()
    # savings = sum()
    # retirement = sum()
    # losses = sum()
    networth = sum(x[4] for x in allData)

    return {
        "Networth": networth
    }

# To-Do: maybe figure out of there is more than one employer
def findSalary(allData: list[tuple]):
    validPayments = [x for x in allData if x[0] == 'income' and x[3] == 'payroll']

    byYearMonth = {}

    for payment in validPayments:
        yearMonth = payment[2][:-3]

        if yearMonth in byYearMonth:
            byYearMonth[yearMonth] += payment[4]
        
        else:
            byYearMonth[yearMonth] = payment[4]

    salaryTotal = 0.0

    foundMonths = 0

    for yearMonth in reversed(list(byYearMonth)):
        salaryTotal += byYearMonth[yearMonth]

        foundMonths += 1

        if foundMonths == 12:
            break

    return round((salaryTotal // foundMonths) * 12)


def getEmergencyFund(allData: list[tuple]) -> tuple[float, float]:
    validLosses = [x for x in allData if x[0] != 'income']

    byYearMonth = {}

    for transaction in validLosses:
        yearMonth = transaction[2][:-3]

        if yearMonth in byYearMonth:
            byYearMonth[yearMonth] += transaction[4]
        
        else:
            byYearMonth[yearMonth] = transaction[4]

    expensesTotal = 0.0

    foundMonths = 0

    for yearMonth in reversed(list(byYearMonth)):
        expensesTotal += byYearMonth[yearMonth]

        foundMonths += 1

        if foundMonths == 12:
            break


    livingExpense = round((abs(expensesTotal) // foundMonths))

    return round(abs(livingExpense * 3)), round(abs(livingExpense * 6))
    
if __name__ == "__main__":
    print(run(1))