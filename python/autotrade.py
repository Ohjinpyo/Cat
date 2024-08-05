import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
from datetime import datetime
import sys

NAME = sys.argv[1]
API_KEY = sys.argv[2]
API_SECRET = sys.argv[3]

SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'

USER = 'root'
PASSWORD = 'Cat2024!!'
HOST = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'backtest'

BALANCE = 1000000
PROFITRATIO = 0.05
LOSSRATIO = 0.02

def update_flags(df):
    if len(df) < 3:
        return df
    
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0
    
    if df['RSI_Hist'].iloc[-3] < 0 and df['RSI_Hist'].iloc[-2] > 0:
        df.at[df.index[-2], 'RSI_Flag'] = 1
    elif df['RSI_Hist'].iloc[-3] > 0 and df['RSI_Hist'].iloc[-2] < 0:
        df.at[df.index[-2], 'RSI_Flag'] = -1

    if df['MACD_hist'].iloc[-3] < 0 and df['MACD_hist'].iloc[-2] > 0:
        df.at[df.index[-2], 'MACD_Flag'] = 1
    elif df['MACD_hist'].iloc[-3] > 0 and df['MACD_hist'].iloc[-2] < 0:
        df.at[df.index[-2], 'MACD_Flag'] = -1

    if df['RSI_Hist'].iloc[-2] < 0 and df['RSI_Hist'].iloc[-1] > 0:
        df.at[df.index[-1], 'RSI_Flag'] = 1
    elif df['RSI_Hist'].iloc[-2] > 0 and df['RSI_Hist'].iloc[-1] < 0:
        df.at[df.index[-1], 'RSI_Flag'] = -1

    if df['MACD_hist'].iloc[-2] < 0 and df['MACD_hist'].iloc[-1] > 0:
        df.at[df.index[-1], 'MACD_Flag'] = 1
    elif df['MACD_hist'].iloc[-2] > 0 and df['MACD_hist'].iloc[-1] < 0:
        df.at[df.index[-1], 'MACD_Flag'] = -1

    return df

def create_table_if_not_exists():
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )
        cursor = connection.cursor()

        # 테이블 생성 쿼리
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INT AUTO_INCREMENT PRIMARY KEY,
            datetime VARCHAR(20) NOT NULL,
            position VARCHAR(10) NOT NULL,
            entryPrice FLOAT NOT NULL,
            exitPrice FLOAT NOT NULL,
            profit FLOAT
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


def insert_credentials_in_db(username, key, secret, symbol, timeframe):
    try:
        exchange = ccxt.binance({
        'apiKey': key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
         })
        
        # 파라미터들
        lookback = 50
        balance = BALANCE
        position = None 
        entry_price = 0
        trades_log = []
        
        # 반복문
        while True:
            # 플래그 확인(데이터베이스)
            connection = mysql.connector.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                database=DATABASE
            )
            cursor = connection.cursor()
            query = "SELECT trading FROM User WHERE username = %s"
            cursor.execute(query, (username,))
            all_rows = cursor.fetchall()
            flag = bool(all_rows[0][0])
            cursor.close()
            connection.close()

            if flag == False:
                break

            # 데이터 업데이트
            df = fetch_and_update_data(exchange, symbol, timeframe, lookback)
            df['RSI'] = ta.rsi(df['close'], length=14)
            df['RSI_Hist'] = df['RSI'] - ta.sma(df['RSI'], length=30)
            df[['MACD', 'MACD_signal', 'MACD_hist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 1, 2]]
            df = update_flags(df)
            print(df.tail())

            # 포지션
            if position is None:
                if (df['RSI_Flag'].iloc[-1] == 1 or df['RSI_Flag'].iloc[-2] == 1 or df['RSI_Flag'].iloc[-3] == 1) and \
                        (df['MACD_Flag'].iloc[-1] == 1 or df['MACD_Flag'].iloc[-2] == 1 or df['MACD_Flag'].iloc[-3] == 1):
                    position = 'long'
                    entry_price = df['close'].iloc[-1]
                    print(f"Long position {username} entered at {entry_price}")
                elif (df['RSI_Flag'].iloc[-1] == -1 or df['RSI_Flag'].iloc[-2] == -1 or df['RSI_Flag'].iloc[-3] == -1) and \
                        (df['MACD_Flag'].iloc[-1] == -1 or df['MACD_Flag'].iloc[-2] == -1 or df['MACD_Flag'].iloc[-3] == -1):
                    position = 'short'
                    entry_price = df['close'].iloc[-1]
                    print(f"Short position {username} entered at {entry_price}")
            else:
                if position == 'long':
                    if df['close'].iloc[-1] >= entry_price * (1 + PROFITRATIO) or df['close'].iloc[-1] <= entry_price * (1 - LOSSRATIO):
                        exit_price = df['close'].iloc[-1]
                        profit = (exit_price - entry_price) / entry_price  # 수익률 계산
                        balance += profit
                        connection = mysql.connector.connect(
                            user=USER,
                            password=PASSWORD,
                            host=HOST,
                            port=PORT,
                            database=DATABASE
                        )
                        cursor = connection.cursor()
                        query = f"INSERT INTO {username}livetrade (datetime, position, entryPrice, exitPrice, profit) VALUES (%s, %s, %s, %s, %s)"
                        val = (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), position, entry_price, exit_price, profit)
                        cursor.execute(query, val)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print(f"Long position exited at {exit_price} with profit {profit}")
                        position = None
                elif position == 'short':
                    if df['close'].iloc[-1] <= entry_price * (1 - PROFITRATIO) or df['close'].iloc[-1] >= entry_price * (1 + LOSSRATIO):
                        exit_price = df['close'].iloc[-1]
                        profit = (entry_price - exit_price) / entry_price  # 수익률 계산
                        balance += profit
                        connection = mysql.connector.connect(
                            user=USER,
                            password=PASSWORD,
                            host=HOST,
                            port=PORT,
                            database=DATABASE
                        )
                        cursor = connection.cursor()
                        query = f"INSERT INTO {username}livetrade (datetime, position, entryPrice, exitPrice, profit) VALUES (%s, %s, %s, %s, %s)"
                        val = (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), position, entry_price, exit_price, profit)
                        cursor.execute(query, val)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print(f"Short position exited at {exit_price} with profit {profit}")
                        position = None

            print('반복문도는중')
            time.sleep(30)

        
        # # 데이터베이스에 데이터 삽입
        # insert_query = """
        # INSERT INTO user_credentials (name, api_key, api_secret, updated_at, price)
        # VALUES (%s, %s, %s, %s, %s)
        # """
        # cursor.execute(insert_query, (name, API_KEY, API_SECRET, now, price))

        # # 변경 사항 커밋
        # connection.commit()

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
insert_credentials_in_db(NAME, API_KEY, API_SECRET, SYMBOL, TIMEFRAME)