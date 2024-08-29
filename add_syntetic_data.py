import os
import random
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_USERNAME = os.getenv('DJANGO_USER')
DB_PASSWORD = os.getenv('DJANGO_PASSWORD')
DB_HOST = os.getenv('DJANGO_HOST')
DB_PORT = os.getenv('DJANGO_PORT')
DB_NAME = os.getenv('DJANGO_NAME')
DB_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# DATABASE CONNECTION
ENGINE = create_engine(DB_URL)
N_RECORDS = 1000

# Add synthetic data
QUERY = """
INSERT INTO plates_platepaid (arrived_at, paid_at, cost, plate_code)
VALUES
    {data}
"""

data = []

for _ in range(N_RECORDS):

    # Generating random data
    year = 2024
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)

    arrived_at = datetime(year, month, day, hour, minutes, seconds)
    
    # adding random time at parking
    hour += random.randint(0, 12)
    minutes += random.randint(0, 59)
    seconds += random.randint(0, 59)

    # validating data
    while hour >= 24 or minutes >= 60 or seconds >= 60:

        if hour >= 24:
            hour -= 24
            day += 1

        if minutes >= 60:
            hour += 1
            minutes -= 60
        
        if seconds >= 60:
            minutes += 1
            seconds -= 60


    paid_at = datetime(year, month, day, hour, minutes, seconds)

    # Counting cost
    time_at_parking = paid_at - arrived_at
    cost = round((time_at_parking.seconds // 60) * 0.05, 2)

    # Generating random plate code
    plate_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=7))

    record = f'(\'{arrived_at}\', \'{paid_at}\', {cost}, \'{plate_code}\'),'

    data.append(record)

converted_data = ' '.join(data)[:-1]
converted_data += ';'


# Pushing data into the database
with ENGINE.connect() as conn:
    conn.execute(text(QUERY.format(data=converted_data)))
    conn.commit()


