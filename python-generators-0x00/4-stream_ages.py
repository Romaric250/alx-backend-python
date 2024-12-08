import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def connect_to_prodev():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def stream_user_ages():
    connection = connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row[0]
    cursor.close()
    connection.close()

def calculate_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    if count == 0:
        return 0
    return total_age / count

if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")

    