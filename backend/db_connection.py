import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3310)),  # Берем порт из .env
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"✅ Подключено к MySQL (порт {os.getenv('DB_PORT')})")
    
    def get_all_universities(self):
        with self.connection.cursor() as cursor:
            sql = """
                SELECT id, name, short_name, city, type, 
                       students_count, rating, programs_count
                FROM universities 
                ORDER BY rating DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    
    def get_university_by_id(self, univ_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM universities WHERE id = %s"
            cursor.execute(sql, (univ_id,))
            return cursor.fetchone()
    
    def get_programs_by_university(self, univ_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM programs WHERE university_id = %s"
            cursor.execute(sql, (univ_id,))
            return cursor.fetchall()