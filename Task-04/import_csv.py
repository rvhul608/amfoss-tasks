import pymysql
import csv

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="useridk"
)
cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS rvhul_db")
cursor.close()
connection.close()
try:
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="useridk",
        db="rvhul_db"
    )
    cur = mydb.cursor()
    data = """
    CREATE TABLE IF NOT EXISTS movies (
        Series_Title VARCHAR(255) PRIMARY KEY,
        Released_Year INT,
        Genre VARCHAR(255),
        IMDB_Rating FLOAT,
        Director VARCHAR(255),
        Star1 VARCHAR(255),
        Star2 VARCHAR(255),
        Star3 VARCHAR(255)
    )
    """
    cur.execute(data)
    print("Table created successfully.")

    with open("movies.csv", "r", encoding="utf-8") as file:
        csv_data = csv.reader(file)
        next(csv_data) 
        for row in csv_data:
            cur.execute(
                'INSERT IGNORE INTO movies(Series_Title, Released_Year, Genre, IMDB_Rating, Director, Star1, Star2, Star3) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)',
                row
            )
    cur.execute("SELECT * FROM movies")
    mydb.commit()
    print("CSV data imported successfully.")



except pymysql.MySQLError as e:
    print("MySQL Error:", e)
finally:
    if 'cur' in locals():
        cur.close()
    if 'mydb' in locals():
        mydb.close()

def export_movies_to_csv(filename="exported_movies.csv"):
    try:
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="useridk",
            db="rvhul_db"
        )
        cur = mydb.cursor()
        cur.execute("SELECT * FROM movies")
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"Data exported successfully to {filename}")
        return filename
    except pymysql.MySQLError as e:
        print("MySQL Error:", e)
    finally:
        if 'cur' in locals():
            cur.close()
        if 'mydb' in locals():
            mydb.close()
