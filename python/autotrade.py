import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
import datetime
import sys
import devide_bakctest2

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
FEE = 0.02
RATIO = 0.3
LEV = 1

def update_flags(df):
    if len(df) < 3:
        return df
    
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0

    if df['RSI_Hist'].iloc[-4] < 0 and df['RSI_Hist'].iloc[-3] > 0:
        df.at[df.index[-3], 'RSI_Flag'] = 1
    elif df['RSI_Hist'].iloc[-4] > 0 and df['RSI_Hist'].iloc[-3] < 0:
        df.at[df.index[-3], 'RSI_Flag'] = -1

    if df['MACD_hist'].iloc[-4] < 0 and df['MACD_hist'].iloc[-3] > 0:
        df.at[df.index[-3], 'MACD_Flag'] = 1
    elif df['MACD_hist'].iloc[-4] > 0 and df['MACD_hist'].iloc[-3] < 0:
        df.at[df.index[-3], 'MACD_Flag'] = -1
    
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


def update_flags_backtest(df):
    if len(df) < 3:
        return df
    
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0
    for i in range(4, df.shape[0]):
        if df['RSI_Hist'].iloc[i - 4] < 0 and df['RSI_Hist'].iloc[i - 3] > 0:
            df.at[df.index[i - 3], 'RSI_Flag'] = 1
        elif df['RSI_Hist'].iloc[i-4] > 0 and df['RSI_Hist'].iloc[i - 3] < 0:
            df.at[df.index[i - 3], 'RSI_Flag'] = -1

        if df['MACD_hist'].iloc[i-4] < 0 and df['MACD_hist'].iloc[i - 3] > 0:
            df.at[df.index[i - 3], 'MACD_Flag'] = 1
        elif df['MACD_hist'].iloc[i-4] > 0 and df['MACD_hist'].iloc[i - 3] < 0:
            df.at[df.index[i - 3], 'MACD_Flag'] = -1
        
        if df['RSI_Hist'].iloc[i - 3] < 0 and df['RSI_Hist'].iloc[i - 2] > 0:
            df.at[df.index[i - 2], 'RSI_Flag'] = 1
        elif df['RSI_Hist'].iloc[i - 3] > 0 and df['RSI_Hist'].iloc[i - 2] < 0:
            df.at[df.index[i - 2], 'RSI_Flag'] = -1

        if df['MACD_hist'].iloc[i - 3] < 0 and df['MACD_hist'].iloc[i - 2] > 0:
            df.at[df.index[i - 2], 'MACD_Flag'] = 1
        elif df['MACD_hist'].iloc[i - 3] > 0 and df['MACD_hist'].iloc[i - 2] < 0:
            df.at[df.index[i - 2], 'MACD_Flag'] = -1

        if df['RSI_Hist'].iloc[i - 2] < 0 and df['RSI_Hist'].iloc[i - 1] > 0:
            df.at[df.index[i - 1], 'RSI_Flag'] = 1
        elif df['RSI_Hist'].iloc[i - 2] > 0 and df['RSI_Hist'].iloc[i - 1] < 0:
            df.at[df.index[i - 1], 'RSI_Flag'] = -1

        if df['MACD_hist'].iloc[i - 2] < 0 and df['MACD_hist'].iloc[i - 1] > 0:
            df.at[df.index[i - 1], 'MACD_Flag'] = 1
        elif df['MACD_hist'].iloc[i - 2] > 0 and df['MACD_hist'].iloc[i - 1] < 0:
            df.at[df.index[i - 1], 'MACD_Flag'] = -1

    return df


def create_table_if_not_exists(name):
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )

        # 커서 생성
        cursor = connection.cursor()

        create_table_query_user_livetrade = f"""
        CREATE TABLE IF NOT EXISTS {name}livetrade (
            id INT AUTO_INCREMENT PRIMARY KEY,
            datetime VARCHAR(20),
            position VARCHAR(10),
            entryPrice FLOAT,
            exitPrice FLOAT,
            profit FLOAT
        )
        """

        # 테이블 생성
        cursor.execute(create_table_query_user_livetrade)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def reboot_table_if_exists(name):
    try:
        # 있으면 초기화
        connection = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DATABASE
        )
        cursor = connection.cursor()
        query = f"DELETE FROM {name}livetrade"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()

        # 데이터베이스 연결
        connection = mysql.connector.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )

        # 커서 생성
        cursor = connection.cursor()

        create_table_query_user_livetrade = f"""
        CREATE TABLE IF NOT EXISTS {name}livetrade (
            id INT AUTO_INCREMENT PRIMARY KEY,
            datetime VARCHAR(20),
            position VARCHAR(10),
            entryPrice FLOAT,
            exitPrice FLOAT,
            profit FLOAT
        )
        """

        # 테이블 생성
        cursor.execute(create_table_query_user_livetrade)

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
        backtest_lookback = 960
        balance = BALANCE
        position = None 
        entry_price = 0
        trades_log = []
        timer_start = datetime.datetime.now()
        timer_end = timer_start + datetime.timedelta(days=1)
        backtest_df = fetch_and_update_data(exchange, symbol, timeframe, backtest_lookback)
        backtest_df['RSI'] = ta.rsi(backtest_df['close'], length=14)
        backtest_df['RSI_Hist'] = backtest_df['RSI'] - ta.sma(backtest_df['RSI'], length=30)
        backtest_df[['MACD', 'MACD_signal', 'MACD_hist']] = ta.macd(backtest_df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
        backtest_df = update_flags_backtest(backtest_df)
        profit_ratio, loss_ratio = devide_bakctest2.find_params(backtest_df, BALANCE, FEE, RATIO, LEV)
        print(profit_ratio, loss_ratio, flush=True)
        # 반복문
        while True:
            # 손익비 찾기
            if datetime.datetime.now() >= timer_end:
                timer_start = datetime.datetime.now()
                timer_end = timer_start + datetime.timedelta(days=1)
                backtest_df = fetch_and_update_data(exchange, symbol, timeframe, backtest_lookback)
                backtest_df = update_flags_backtest(backtest_df)
                profit_ratio, loss_ratio = devide_bakctest2.find_params(backtest_df, BALANCE, FEE, RATIO, LEV)

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
            df[['MACD', 'MACD_signal', 'MACD_hist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
            df = update_flags(df)

            # 포지션
            if position is None:
                if (df['RSI_Flag'].iloc[-1] == 1 or df['RSI_Flag'].iloc[-2] == 1 or df['RSI_Flag'].iloc[-3] == 1) and \
                        (df['MACD_Flag'].iloc[-1] == 1 or df['MACD_Flag'].iloc[-2] == 1 or df['MACD_Flag'].iloc[-3] == 1):
                    position = 'long'
                    entry_price = df['close'].iloc[-1]
                    print(f"Long position {username} entered at {entry_price}", flush=True)
                elif (df['RSI_Flag'].iloc[-1] == -1 or df['RSI_Flag'].iloc[-2] == -1 or df['RSI_Flag'].iloc[-3] == -1) and \
                        (df['MACD_Flag'].iloc[-1] == -1 or df['MACD_Flag'].iloc[-2] == -1 or df['MACD_Flag'].iloc[-3] == -1):
                    position = 'short'
                    entry_price = df['close'].iloc[-1]
                    print(f"Short position {username} entered at {entry_price}", flush=True)
            else:
                if position == 'long':
                    if df['close'].iloc[-1] >= entry_price * (1 + profit_ratio / 100) or df['close'].iloc[-1] <= entry_price * (1 - loss_ratio / 100):
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
                        print(f"Long position exited at {exit_price} with profit {profit}", flush=True)
                        position = None
                elif position == 'short':
                    if df['close'].iloc[-1] <= entry_price * (1 - profit_ratio / 100) or df['close'].iloc[-1] >= entry_price * (1 + locals / 100):
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
                        print(f"Short position exited at {exit_price} with profit {profit}", flush=True)
                        position = None

            if(position is None):
                p = 'None'
            else:
                p = position
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " " + p + ", " + str(entry_price), flush=True)
            time.sleep(60)

        
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
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms') + pd.Timedelta(hours=9)
    return df


if __name__ == "__main__":
    create_table_if_not_exists(NAME)
    reboot_table_if_exists(NAME)
    insert_credentials_in_db(NAME, API_KEY, API_SECRET, SYMBOL, TIMEFRAME)
