"""import pandas as pd

# Create a dataframe from a dictionary
data = {'Name': ['John', 'Emma', 'Peter', 'Olivia'],
        'Age': [28, 24, 32, 29],
        'City': ['New York', 'London', 'Paris', 'Sydney']}
df = pd.DataFrame(data)

# Print the dataframe
print(df)

# Accessing columns
print(df['Name'])
print(df.Age)

# Accessing rows
print(df.loc[0])  # Access row by label
print(df.iloc[2])  # Access row by index

# Filtering rows
filtered_df = df[df['Age'] > 25]
print(filtered_df)

# Adding a new column
df['Profession'] = ['Engineer', 'Artist', 'Doctor', 'Writer']
print(df)

# Applying a function to a column
df['Age in 10 years'] = df['Age'].apply(lambda x: x + 10)
print(df)


import psycopg2
from sqlalchemy import create_engine
import pandas as pd

data = {'testtype': ["boom"],
        'time': [1],
        'volts': [1],
        'current': [1],
        'power': [1],
        'c_rate': [1],
        'cycle_number': [1],
        'date': ["2000-11-11"],
        'id': [2]}

current_date = date.today()
df = pd.DataFrame(data)

# Replace these with your database credentials
database = "Alor - DB"
user = "postgres"
password = "1234"
port = 5432
host = "localhost"

# Create a database connection
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

# Insert the DataFrame into the database table
df.to_sql('testdata', engine, index=False)
print("adfadfadfasdfasf") """

import threading

class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._result = None

    def run(self):
        if self._target is not None:
            self._result = self._target(*self._args)

    def result(self):
        return self._result

def testRunner(arg):
    # Perform some computation or task
    result = arg * 2

    # Return the result
    return result

Charge_Volt_start = 5

# Create the custom thread
thread_runner = MyThread(target=testRunner, args=(Charge_Volt_start,))
thread_runner.start()
thread_runner.join()

# Retrieve the return value
thread_result = thread_runner.result()
print("Thread result:", thread_result)