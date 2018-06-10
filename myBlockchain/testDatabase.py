import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS info (id INTEGER PRIMARY KEY, previous_hash text, proof int, timestamps float)"

cursor.execute(create_table)

# insert_query = "INSERT INTO info VALUES(?,?,?,?)"
# cursor.execute(insert_query, info)
#
# users = [
#     (1, "1", 100, 1527409046.720226)
# ]
#
# cursor.executemany(insert_query, users)
#
# select_query = "SELECT * FROM info"
# for row in cursor.execute(select_query):
#     print(row)
connection.commit()

connection.close()
