import asyncio
import ccxt.pro as ccxtpro
import os
import pandas as pd
import talib
from dotenv import load_dotenv
import datetime
from aiohttp import ClientTimeout
import mysql.connector
import sys

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
# API_KEY = os.getenv("API_KEY")
# SECRET_KEY = os.getenv("SECRET_KEY")
name = sys.argv[1]
API_KEY = sys.argv[2]
API_SECRET = sys.argv[3]

symbol = "BTC/USDT"
timeframe = '15m'

initial_balance = 1000000  # 초기 자본
take_profit_ratio = 0.05  # 익절 비율
stop_loss_ratio = 0.02  # 손절 비율

async def fetch_candles(exchange, symbol, timeframe, limit):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except asyncio.TimeoutError:
            print(f"TimeoutError: retrying... {attempt + 1}/{max_retries}")
            await asyncio.sleep(2)
        except ccxtpro.NetworkError as e:
            print(f"NetworkError: {e}, retrying... {attempt + 1}/{max_retries}")
            await asyncio.sleep(2)
    raise Exception(f"Failed to fetch OHLCV data after {max_retries} attempts")

def calculate_indicators(df):
    # RSI 계산
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)

    # RSI의 MACD 계산
    #rsi_macd, rsi_signal, rsi_hist = talib.MACD(df['RSI'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['RSI_Hist'] =  talib.SMA(df['RSI'], timeperiod=9)
    
    # MACD 계산
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    return df

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

async def fetch_and_update_data(exchange, symbol, timeframe, lookback):
    ohlcv = await fetch_candles(exchange, symbol, timeframe, lookback)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') + pd.Timedelta(hours=9)
    df = calculate_indicators(df)
    return df

async def main(userName, API_KEY, API_SECRET):
    # 15분 데이터 초기 불러오기
    exchange = ccxtpro.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
    })

    # MySQL 데이터베이스 연결 설정
    user = 'root'
    password = 'Cat2024!!'
    host = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com:3306'
    port = '3306'
    database = 'backtest'

    # 데이터베이스 연결
    connection = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

    # 커서 생성
    cursor = connection.cursor()

    create_table_query_trades = """
    CREATE TABLE IF NOT EXISTS trades (
        id INT AUTO_INCREMENT PRIMARY KEY,
        datetime DATETIME,
        position VARCHAR(10),
        entry_price FLOAT,
        exit_price FLOAT,
        profit FLOAT
    )
    """

    create_table_query_user = """
    CREATE TABLE IF NOT EXISTS user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        apikey VARCHAR(255),
        apisecret VARCHAR(255),
        password VARCHAR(255),
        username VARCHAR(255),
        flag INT
    )
    """

    # 테이블 생성
    cursor.execute(create_table_query_trades)
    cursor.execute(create_table_query_user)

    # 커넥션 및 커서 종료
    cursor.close()
    connection.close()

    balance = initial_balance
    position = None
    entry_price = 0
    trades_log = []

    flag = True

    while flag:
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()

        # flag 값 조회
        query = "SELECT trading FROM User WHERE username = %s"
        cursor.execute(query, (userName,))
        all_rows = cursor.fetchall()

        flag = all_rows[0][0]


        lookback = 50  # 초기 lookback 값 설정
        df = await fetch_and_update_data(exchange, symbol, timeframe, lookback)  # 883ms정도 걸림
        df = update_flags(df)

        await asyncio.sleep(10)  # 10초

        # 충분한 데이터가 쌓일 때까지 기다림
        if len(df) >= 14:  # RSI를 계산하는 데 필요한 최소 데이터 수 14
            df = calculate_indicators(df)
            df = update_flags(df)
            print(df.tail())

            # 포지션 관리 로직
            if position is None:
                if (df['RSI_Flag'].iloc[-1] == 1 or df['RSI_Flag'].iloc[-2] == 1 or df['RSI_Flag'].iloc[-3] == 1) and \
                        (df['MACD_Flag'].iloc[-1] == 1 or df['MACD_Flag'].iloc[-2] == 1 or df['MACD_Flag'].iloc[-3] == 1):
                    position = 'long'
                    entry_price = df['close'].iloc[-1]
                    print(f"Long position entered at {entry_price}")
                elif (df['RSI_Flag'].iloc[-1] == -1 or df['RSI_Flag'].iloc[-2] == -1 or df['RSI_Flag'].iloc[-3] == -1) and \
                        (df['MACD_Flag'].iloc[-1] == -1 or df['MACD_Flag'].iloc[-2] == -1 or df['MACD_Flag'].iloc[-3] == -1):
                    position = 'short'
                    entry_price = df['close'].iloc[-1]
                    print(f"Short position entered at {entry_price}")
            else:
                if position == 'long':
                    if df['close'].iloc[-1] >= entry_price * (1 + take_profit_ratio) or df['close'].iloc[-1] <= entry_price * (1 - stop_loss_ratio):
                        exit_price = df['close'].iloc[-1]
                        profit = (exit_price - entry_price) / entry_price  # 수익률 계산
                        balance += profit
                        connection = mysql.connector.connect(
                            user=user,
                            password=password,
                            host=host,
                            port=port,
                            database=database
                        )
                        cursor = connection.cursor()
                        query = "INSERT INTO trades (datetime, position, entry_price, exit_price, profit) VALUES (%s, %s, %s, %s, %s)"
                        val = (datetime.datetime.now(), position, entry_price, exit_price, profit)
                        cursor.execute(query, val)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print(f"Long position exited at {exit_price} with profit {profit}")
                        position = None
                elif position == 'short':
                    if df['close'].iloc[-1] <= entry_price * (1 - take_profit_ratio) or df['close'].iloc[-1] >= entry_price * (1 + stop_loss_ratio):
                        exit_price = df['close'].iloc[-1]
                        profit = (entry_price - exit_price) / entry_price  # 수익률 계산
                        balance += profit
                        connection = mysql.connector.connect(
                            user=user,
                            password=password,
                            host=host,
                            port=port,
                            database=database
                        )
                        cursor = connection.cursor()
                        query = "INSERT INTO trades (datetime, position, entry_price, exit_price, profit) VALUES (%s, %s, %s, %s, %s)"
                        val = (datetime.datetime.now(), position, entry_price, exit_price, profit)
                        cursor.execute(query, val)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print(f"Short position exited at {exit_price} with profit {profit}")
                        position = None

    # 결과 로그 데이터프레임 생성
    if trades_log:
        trades_df = pd.DataFrame(trades_log)
        trades_df['cumulative_profit'] = trades_df['profit'].cumsum()
        trades_df['win'] = trades_df['profit'] > 0
        win_rate = trades_df['win'].mean()
        total_profit = trades_df['profit'].sum()

        print(f"Final Balance: {balance}")
        print(f"Total Profit: {total_profit}")
        print(f"Win Rate: {win_rate}")

        # 데이터베이스에 저장된 값 초기화
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()
        query = "DELETE FROM trades"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()

    await exchange.close()

def run_trading_bot(name, API_KEY, API_SECRET):
    stop_event = asyncio.Event()

    def stop_bot():
        input("종료하려면 Enter 키를 누르세요...")
        stop_event.set()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, stop_bot)
    # loop.run_until_complete(main(stop_event))
    main(name, API_KEY, API_SECRET)


run_trading_bot(name, API_KEY, API_SECRET)
