import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
import datetime
import sys
from tensorflow.keras.models import load_model
import joblib

# 데이터베이스에서 이름/api키 받아오기
NAME = 'ljhtest'
API_KEY = 'yz5twLkIxD7y3rGJuY04IA4PUJR0Upk9DS9jBD4oWZBg5kLJIDqIdOTLXPxvholU'
API_SECRET = 'LE8Gqnjg6ZhxBnyERuEUe5tSpEGE656gb3VjEzIWd2NaiR1v52pzedstugvZNjG0'

# 바이낸스 api를 사용하기 위한 심볼과 봉 시간 설정
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'

# 데이터베이스
USER = 'root'
PASSWORD = 'Cat2024!!'
HOST = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'backtest'

BALANCE = 100000000
FEE = 0.02
RATIO = 0.3
LEV = 10
# P_START = float(sys.argv[7])
# P_END = float(sys.argv[8])
# L_START = float(sys.argv[9])
# L_END = float(sys.argv[10])


# 데이터베이스가 없으면 만들기
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
            position VARCHAR(10),
            entryTime VARCHAR(20),
            entryPrice FLOAT,
            exitTime VARCHAR(20),
            exitPrice FLOAT,
            contract FLOAT,
            profit FLOAT,
            profitRate FLOAT,
            deposit FLOAT
        )
        """

        # 테이블 생성
        cursor.execute(create_table_query_user_livetrade)

    except mysql.connector.Error as err:
        pass
        #print(f"Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


#데이터베이스가 이미 있으면 초기화
def reboot_table_if_exists(name):
    try:
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
            position VARCHAR(10),
            entryTime VARCHAR(20),
            entryPrice FLOAT,
            exitTime VARCHAR(20),
            exitPrice FLOAT,
            contract FLOAT,
            profit FLOAT,
            profitRate FLOAT,
            deposit FLOAT
        )
        """

        # 테이블 생성
        cursor.execute(create_table_query_user_livetrade)

    except mysql.connector.Error as err:
        #print(f"Error: {err}")
        pass

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# 바이낸스에서 차트 데이터 받아오기
def fetch_candles(exchange, symbol, timeframe, limit):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except ccxt.NetworkError as e:
            #print(f"NetworkError: {e}, retrying... {attempt + 1}/{max_retries}")
            time.sleep(2)
    raise Exception(f"Failed to fetch OHLCV data after {max_retries} attempts")


# 받아온 차트 데이터 원하는 형태의 데이터프레임화
def fetch_and_update_data(exchange, symbol, timeframe, lookback):
    ohlcv = fetch_candles(exchange, symbol, timeframe, lookback)
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms') + pd.Timedelta(hours=9)
    df['MovingAverage'] = ta.sma(df['close'], length=30)
    return df

model_close = load_model("btc_close.h5")
scaler_features_close = joblib.load('scaler_features_close.pkl')
scaler_target_close = joblib.load('scaler_target_close.pkl')


# 메인 함수
def auto_trade2(username, key, secret, symbol, timeframe):
    #변수
    position = None
    time_keep= 900 # 900초==15분 포지션 유지 
    position_time = 0 #포지션 유지한 시간 유지시간이 time_keep보다 같거나 커지면 포지션 청산
    sleep_time = 10
    persent = 0.0005
    deposit = BALANCE
    ratio = RATIO
    lev=LEV
    fee = FEE
    username = NAME
    try:
        exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
            })
        
        while True:
            start = time.time()

            df = fetch_and_update_data(exchange, SYMBOL, TIMEFRAME, 60)
            df['Rsi'] = ta.rsi(df['close'], length=14)
            df[['Macd', 'MacdSignal', 'MacdHist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
            df['MovingAverage'] = ta.sma(df['close'], length=30)
            df['Rsi_avg'] = df['Rsi'] - ta.sma(df['Rsi'], length=30)

            #############
            features_close_prev = df[['Rsi', 'Macd', 'open', 'high', 'low', 'MacdSignal', 'MacdHist', 'MovingAverage']].values[-11:-1]

            scaled_features_close_prev = scaler_features_close.transform(features_close_prev)
            # LSTM 입력 형태로 데이터 변환
            X_recent_seq_close_prev = scaled_features_close_prev.reshape((1, 10, scaled_features_close_prev.shape[1]))

            # 예측
            y_pred_close_prev = model_close.predict(X_recent_seq_close_prev)
            y_pred_close_prev = scaler_target_close.inverse_transform(y_pred_close_prev)

            #############
            features_close_current = df[['Rsi', 'Macd', 'open', 'high', 'low', 'MacdSignal', 'MacdHist', 'MovingAverage']].values[-10:]

            scaled_features_close_current = scaler_features_close.transform(features_close_current)
            # LSTM 입력 형태로 데이터 변환
            X_recent_seq_close = scaled_features_close_current.reshape((1, 10, scaled_features_close_current.shape[1]))

            # 예측
            y_pred_close_current = model_close.predict(X_recent_seq_close)
            y_pred_close_current = scaler_target_close.inverse_transform(y_pred_close_current)
            ############
            #결과 출력


            print(f'Predicted close: {y_pred_close_prev[0][0]}')
            print(f'Predicted close: {y_pred_close_current[0][0]}')

            close_diff = (y_pred_close_prev[0][0]-y_pred_close_current[0][0])/df['close'].iloc[-2]
            print(close_diff)

            end=time.time()
            position_time = end-start

            if close_diff <= -1*persent:
                if position == None:
                    position = 'short'
                    entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry_price = df['close'].iloc[-1]
                    contract = deposit * ratio * lev / entry_price

            elif close_diff >= persent:
                if position == None:
                    position = 'long'
                    entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry_price = df['close'].iloc[-1]
                    contract = deposit * ratio * lev / entry_price

            if position_time >= time_keep:
                #청산

                if position == 'long':
                        exit_price = df['close'].iloc[-1]
                        exit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # 수익률 계산
                        profit = (exit_price - entry_price) * (1 - fee / 100) * contract
                        profit_rate = profit / (entry_price * contract)
                        profit_rate = round(profit_rate)
                        deposit += profit

                        connection = mysql.connector.connect(
                            user=USER,
                            password=PASSWORD,
                            host=HOST,
                            port=PORT,
                            database=DATABASE
                        )
                        cursor = connection.cursor()
                        query = f"INSERT INTO {username}livetrade (position, entryTime, entryPrice, exitTime, exitPrice, contract, profit, profitRate, deposit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (position, entry_time, entry_price, exit_time, exit_price, contract, profit, profit_rate, deposit)
                        cursor.execute(query, val)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        # 포지션 청산 문구 출력
                        #print(f"{exit_time} : Long position exited at {exit_price} with profit {profit}", flush=True)
                        position = None
                        entry_price = 0
                        exit_price = 0
                elif position == 'short':
                    exit_price = df['close'].iloc[-1]
                    exit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # 수익률 계산
                    profit = (entry_price - exit_price) * (1 - fee / 100) * contract
                    profit_rate = profit / (entry_price * contract)
                    profit_rate = round(profit_rate)
                    deposit += profit

                    connection = mysql.connector.connect(
                        user=USER,
                        password=PASSWORD,
                        host=HOST,
                        port=PORT,
                        database=DATABASE
                    )
                    cursor = connection.cursor()
                    query = f"INSERT INTO {username}livetrade (position, entryTime, entryPrice, exitTime, exitPrice, contract, profit, profitRate, deposit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (position, entry_time, entry_price, exit_time, exit_price, contract, profit, profit_rate, deposit)
                    cursor.execute(query, val)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    # 포지션 청산 문구 출력
                    #print(f"{exit_time} : Long position exited at {exit_price} with profit {profit}", flush=True)
                    position = None
                    entry_price = 0
                    exit_price = 0
            
            
            time.sleep(sleep_time)


    except mysql.connector.Error as err:
        #print(f"Error: {err}")
        pass

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    create_table_if_not_exists(NAME)
    reboot_table_if_exists(NAME)
    auto_trade2(NAME, API_KEY, API_SECRET, SYMBOL, TIMEFRAME)