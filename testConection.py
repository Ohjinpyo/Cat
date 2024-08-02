import sys
import time
import mysql.connector
from datetime import datetime

# 명령줄 인자로부터 변수 받아오기
name = sys.argv[1]
API_KEY = sys.argv[2]
API_SECRET = sys.argv[3]

# MySQL 데이터베이스 연결 설정
user = 'root'
password = 'Cat2024!!'
host = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
port = '3306'
database = 'backtest'

def create_table_if_not_exists():
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()

        # 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            api_key VARCHAR(255) NOT NULL,
            api_secret VARCHAR(255) NOT NULL,
            updated_at DATETIME NOT NULL
        );
        """

        # 테이블 생성
        cursor.execute(create_table_query)
        connection.commit()

        print("Table `user_credentials` is ready.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_credentials_in_db():
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()

        # 현재 시간 가져오기
        now = datetime.now()

        # 데이터베이스에 데이터 삽입
        insert_query = """
        INSERT INTO user_credentials (name, api_key, api_secret, updated_at)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, API_KEY, API_SECRET, now))

        # 변경 사항 커밋
        connection.commit()

        print(f"Inserted new credentials for {name} at {now}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 테이블이 존재하지 않으면 생성
create_table_if_not_exists()

# 30초마다 삽입하는 무한 루프
while True:
    insert_credentials_in_db()
    time.sleep(30)
