import sqlite3, os

from dotenv import load_dotenv

from src.exceptions import *

load_dotenv()

def run(userID, data):
    if not validUser(userID): 
        raise InvalidUser()

    if type(data) == dict: 
        runJson(userID, data)

    else:
        raise BadUploadType(f'Type ({type(data)}) is not allowed')
    
def validUser(potentialID: int) -> bool:
    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        if len(cursor.execute('SELECT id FROM user WHERE id = ?', str(potentialID)).fetchall()) == 1:
            return True

        else:
            return False

def runJson(userID: int, data: dict[dict]):
    transactionsByGroup = getTransactionsByGroup(data)

    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        for key, val in transactionsByGroup.items():
            query = f"""
            INSERT INTO {key} (user_id, value, date, info, category)
            VALUES ({userID}, ?, ?, ?, ?)
            """

            cursor.executemany(query, val)

        connection.commit()

def getTransactionsByGroup(data: dict[dict]) -> dict[list[tuple]]:
    output = {'income': [], 'purchase': [], 'transfer': []}

    for transaction in data.values():
        try:
            if transaction['group'].lower() not in output.keys():
                print('count not find group')
                continue

            output[transaction['group']].append((
                transaction['value'],
                transaction['date'],
                transaction['info'],
                transaction['category']
            ))

        except KeyError as e:
            print("could not find value")
            continue

    return output