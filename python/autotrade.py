import ccxt
import pandas as pd
import time
import mysql.connector
from datetime import datetime

name = 'ojp'
API_KEY = 'U9sPbEF13MsG74sLS02i4DzQkaW9l4DHs5a9VVxPJ6ZppvhELRGYzBun1Ep8ioLw'
API_SECRET = 'TDr0yZ2KuCPoGu3s2c2UgXZ8zksS7YLR2K8e2u9SrdlW7MupwbjL5NfSDvCiMFB6'

symbol = 'BTC/USDT'
timeframe = '15m'

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
            updated_at DATETIME NOT NULL,
            price FLOAT
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

        exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
         })
        lookback = 50
        df = fetch_and_update_data(exchange, symbol, timeframe, lookback)

        # 데이터베이스에 데이터 삽입
        insert_query = """
        INSERT INTO user_credentials (name, api_key, api_secret, updated_at, price)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (name, API_KEY, API_SECRET, now, df['close'].iloc[-1]))

        # 변경 사항 커밋
        connection.commit()

        print(f"Inserted new credentials for {name} at {now}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def fetch_candles(exchange, symbol, timeframe, limit):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except ccxt.NetworkError as e:
            print(f"NetworkError: {e}, retrying... {attempt + 1}/{max_retries}")
            time.sleep(2)
    raise Exception(f"Failed to fetch OHLCV data after {max_retries} attempts")


def fetch_and_update_data(exchange, symbol, timeframe, lookback):
    ohlcv = fetch_candles(exchange, symbol, timeframe, lookback)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') + pd.Timedelta(hours=9)
    return df



create_table_if_not_exists()


    # 30초마다 삽입하는 무한 루프
while True:
    insert_credentials_in_db()
    time.sleep(30)
