import pymysql

try:
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="tcs@2007",
        database="kinship"
    )

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM child_master")
    result = cursor.fetchone()

    print("Total Children:", result[0])

except Exception as e:
    print("Database Error:", e)