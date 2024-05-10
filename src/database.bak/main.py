import psycopg2

connection = psycopg2.connect(
    user="postgres",
    password="",
    # host="localhost",
    port="5432", # default port
    database="mydatabase"
)

cursor = connection.cursor()

# cmd = """
# SELECT column_name, data_type
# FROM information_schema.columns
# WHERE table_name = 'employees';
# """

cmd = """
SELECT * FROM employees;
"""

cursor.execute(cmd)

# response = cursor.fetchall()
response = cursor.fetchone() # tuple[Any]


print(response[1])

cursor.close()
connection.close()

