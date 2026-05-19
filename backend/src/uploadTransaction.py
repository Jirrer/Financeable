import sqlite3, os
from dotenv import load_dotenv

load_dotenv()

def run(userID, data):
    if not validUser(userID): 
        print("Invalid User")

        return False # add custom exceptions

    if type(data) == dict: 
        runJson(userID, data)

    else:
        raise KeyError
    
def validUser(potentialID: int) -> bool:
    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()

        if len(cursor.execute('SELECT id FROM user WHERE id = ?', str(potentialID)).fetchall()) == 1:
            return True

        else:
            return False

def runJson(userID: int, dict: dict[dict]):
    arraysByDict = getArraysByDict(dict)

    with sqlite3.connect(os.getenv('DATABASE_LOCATION')) as connection:
        cursor = connection.cursor()


        for key, val in arraysByDict.items():
            query = f"""
            INSERT INTO {key} (user_id, date, category, value, info)
            VALUES ({userID}, ?, ?, ?, ?)
            """

            cursor.executemany(query, val)

            for x in val:
                print(f"added {key} - {x}")

        connection.commit()

def getArraysByDict(dictInput: dict[dict]) -> dict[list[tuple]]:
    output = {'income': [], 'purchase': [], 'transfer': []}

    for data in dictInput.values():
        try:
            if data['group'].lower() not in output.keys():
                print('count not find group')
                continue

            output[data['group']].append((
                data['value'],
                data['date'],
                data['info'],
                data['category']
            ))

        except KeyError as e:
            print("could not find value")
            continue

    return output