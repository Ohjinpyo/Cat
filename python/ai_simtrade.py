import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
import datetime
import sys
import devide_bakctest2
from ai import ai_test

# 데이터베이스에서 이름/api키 받아오기
NAME = sys.argv[1]
API_KEY = sys.argv[2]
API_SECRET = sys.argv[3]

# 바이낸스 api를 사용하기 위한 심볼과 봉 시간 설정
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'

# 데이터베이스
USER = 'root'
PASSWORD = 'Cat2024!!'
HOST = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'backtest'

# 투자 파라미터
# BALANCE = 1000000
# FEE = 0.02
# RATIO = 0.3
# LEV = 1

BALANCE = int(sys.argv[4])
FEE = 0.02
RATIO = float(sys.argv[5])
LEV = int(sys.argv[6])
P_START = float(sys.argv[7])
P_END = float(sys.argv[8])
L_START = float(sys.argv[9])
L_END = float(sys.argv[10])

# 거래 플래그 업데이트하는 함수
def update_flags(df):
    if len(df) < 3:
        return df
    
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0

    # RSI, MACD의 부호가 바뀌면 플래그를 찍음(음->양 1, 양->음 -1)
    if df['Rsi_avg'].iloc[-4] < 0 and df['Rsi_avg'].iloc[-3] > 0:
        df.at[df.index[-3], 'RSI_Flag'] = 1
    elif df['Rsi_avg'].iloc[-4] > 0 and df['Rsi_avg'].iloc[-3] < 0:
        df.at[df.index[-3], 'RSI_Flag'] = -1

    if df['MacdHist'].iloc[-4] < 0 and df['MacdHist'].iloc[-3] > 0:
        df.at[df.index[-3], 'MACD_Flag'] = 1
    elif df['MacdHist'].iloc[-4] > 0 and df['MacdHist'].iloc[-3] < 0:
        df.at[df.index[-3], 'MACD_Flag'] = -1
    
    if df['Rsi_avg'].iloc[-3] < 0 and df['Rsi_avg'].iloc[-2] > 0:
        df.at[df.index[-2], 'RSI_Flag'] = 1
    elif df['Rsi_avg'].iloc[-3] > 0 and df['Rsi_avg'].iloc[-2] < 0:
        df.at[df.index[-2], 'RSI_Flag'] = -1

    if df['MacdHist'].iloc[-3] < 0 and df['MacdHist'].iloc[-2] > 0:
        df.at[df.index[-2], 'MACD_Flag'] = 1
    elif df['MacdHist'].iloc[-3] > 0 and df['MacdHist'].iloc[-2] < 0:
        df.at[df.index[-2], 'MACD_Flag'] = -1

    if df['Rsi_avg'].iloc[-2] < 0 and df['Rsi_avg'].iloc[-1] > 0:
        df.at[df.index[-1], 'RSI_Flag'] = 1
    elif df['Rsi_avg'].iloc[-2] > 0 and df['Rsi_avg'].iloc[-1] < 0:
        df.at[df.index[-1], 'RSI_Flag'] = -1

    if df['MacdHist'].iloc[-2] < 0 and df['MacdHist'].iloc[-1] > 0:
        df.at[df.index[-1], 'MACD_Flag'] = 1
    elif df['MacdHist'].iloc[-2] > 0 and df['MacdHist'].iloc[-1] < 0:
        df.at[df.index[-1], 'MACD_Flag'] = -1

    return df


# 거래 플래그 업데이트하는 함수(백테스트용)
def update_flags_backtest(df):
    if len(df) < 3:
        return df
    
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0

    # 백테스트용이라 마지막3개만 찍는게 아니라 반복문돌려서 전부 찍음
    for i in range(4, df.shape[0]):
        # RSI, MACD의 부호가 바뀌면 플래그를 찍음(음->양 1, 양->음 -1)
        if df['Rsi_avg'].iloc[i - 4] < 0 and df['Rsi_avg'].iloc[i - 3] > 0:
            df.at[df.index[i - 3], 'RSI_Flag'] = 1
        elif df['Rsi_avg'].iloc[i-4] > 0 and df['Rsi_avg'].iloc[i - 3] < 0:
            df.at[df.index[i - 3], 'RSI_Flag'] = -1

        if df['MacdHist'].iloc[i-4] < 0 and df['MacdHist'].iloc[i - 3] > 0:
            df.at[df.index[i - 3], 'MACD_Flag'] = 1
        elif df['MacdHist'].iloc[i-4] > 0 and df['MacdHist'].iloc[i - 3] < 0:
            df.at[df.index[i - 3], 'MACD_Flag'] = -1
        
        if df['Rsi_avg'].iloc[i - 3] < 0 and df['Rsi_avg'].iloc[i - 2] > 0:
            df.at[df.index[i - 2], 'RSI_Flag'] = 1
        elif df['Rsi_avg'].iloc[i - 3] > 0 and df['Rsi_avg'].iloc[i - 2] < 0:
            df.at[df.index[i - 2], 'RSI_Flag'] = -1

        if df['MacdHist'].iloc[i - 3] < 0 and df['MacdHist'].iloc[i - 2] > 0:
            df.at[df.index[i - 2], 'MACD_Flag'] = 1
        elif df['MacdHist'].iloc[i - 3] > 0 and df['MacdHist'].iloc[i - 2] < 0:
            df.at[df.index[i - 2], 'MACD_Flag'] = -1

        if df['Rsi_avg'].iloc[i - 2] < 0 and df['Rsi_avg'].iloc[i - 1] > 0:
            df.at[df.index[i - 1], 'RSI_Flag'] = 1
        elif df['Rsi_avg'].iloc[i - 2] > 0 and df['Rsi_avg'].iloc[i - 1] < 0:
            df.at[df.index[i - 1], 'RSI_Flag'] = -1

        if df['MacdHist'].iloc[i - 2] < 0 and df['MacdHist'].iloc[i - 1] > 0:
            df.at[df.index[i - 1], 'MACD_Flag'] = 1
        elif df['MacdHist'].iloc[i - 2] > 0 and df['MacdHist'].iloc[i - 1] < 0:
            df.at[df.index[i - 1], 'MACD_Flag'] = -1

    return df


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
        CREATE TABLE IF NOT EXISTS {name}aisimtrade (
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
        query = f"DELETE FROM {name}aisimtrade"
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
        CREATE TABLE IF NOT EXISTS {name}aisimtrade (
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


# 메인 함수
def auto_trade(username, key, secret, symbol, timeframe):
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
        
        # 모델 로드를 위한 데이터프레임
        df = fetch_and_update_data(exchange, symbol, timeframe, 60)
        df['Rsi'] = ta.rsi(df['close'], length=14)
        df[['Macd', 'MacdSignal', 'MacdHist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
        df['MovingAverage'] = ta.sma(df['close'], length=30)
        df['Rsi_avg'] = df['Rsi'] - ta.sma(df['Rsi'], length=30)
        df = df.dropna()
        
        # 모델 최초 로드
        model1, model2, model3 = ai_test.set_model_macd()
        model4, model5, model6 = ai_test.set_model_rsi()
        # #print(ai_test.get_predict(model1, model2, model3, model4, model5, model6, df))

        # 파라미터들
        lookback = 60
        backtest_lookback = 960
        deposit = BALANCE
        ratio = RATIO
        lev = LEV
        fee = FEE
        position = None 
        entry_price = 0
        timer_start = datetime.datetime.now()
        timer_end = timer_start + datetime.timedelta(days=1)

        # 최초의 손익비 찾기
        backtest_df = fetch_and_update_data(exchange, symbol, timeframe, backtest_lookback)
        backtest_df['Rsi'] = ta.rsi(backtest_df['close'], length=14)
        backtest_df['Rsi_avg'] = backtest_df['Rsi'] - ta.sma(backtest_df['Rsi'], length=30)
        backtest_df[['Macd', 'MacdSignal', 'MacdHist']] = ta.macd(backtest_df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
        backtest_df = update_flags_backtest(backtest_df)
        profit_ratio, loss_ratio = devide_bakctest2.find_params(backtest_df, BALANCE, fee, ratio, lev, P_START, P_END, L_START, L_END)
        # 손익비 출력
        #print(profit_ratio, loss_ratio, flush=True)

        # 반복문
        while True:
            # 24시간이 지나면 손익비 최신화
            if datetime.datetime.now() >= timer_end:
                timer_start = datetime.datetime.now()
                timer_end = timer_start + datetime.timedelta(days=1)
                backtest_df = fetch_and_update_data(exchange, symbol, timeframe, backtest_lookback)
                backtest_df['Rsi'] = ta.rsi(backtest_df['close'], length=14)
                backtest_df['Rsi_avg'] = backtest_df['Rsi'] - ta.sma(backtest_df['Rsi'], length=30)
                backtest_df[['Macd', 'MacdSignal', 'MacdHist']] = ta.macd(backtest_df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
                backtest_df = update_flags_backtest(backtest_df)
                profit_ratio, loss_ratio = devide_bakctest2.find_params(backtest_df, BALANCE, fee, ratio, lev, P_START, P_END, L_START, L_END)
                #print(profit_ratio, loss_ratio, flush=True)

            # 거래 상태 플래그 확인(데이터베이스)
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

            # 거래 상태 플래그가 False면 거래 중단
            if flag == False:
                break

            # 데이터 업데이트
            df = fetch_and_update_data(exchange, symbol, timeframe, lookback)
            df['Rsi'] = ta.rsi(df['close'], length=14)
            df[['Macd', 'MacdSignal', 'MacdHist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
            df['MovingAverage'] = ta.sma(df['close'], length=30)
            df['Rsi_avg'] = df['Rsi'] - ta.sma(df['Rsi'], length=30)
            macd_hist, rsi_hist = ai_test.get_predict(model1, model2, model3, model4, model5, model6, df)
            predict = pd.DataFrame({'MacdHist':[macd_hist[0][0]], 'Rsi_avg':[rsi_hist[0][0]]})
            df = pd.concat([df, predict])
            df = update_flags(df)
            # 데이터프레임 출력
            #print(df.tail(), flush=True)

            # 포지션
            if position is None:
                # 플래그 두개가 3틱이내에 겹치면 포지션 생성
                if (df['RSI_Flag'].iloc[-1] == 1 or df['RSI_Flag'].iloc[-2] == 1 or df['RSI_Flag'].iloc[-3] == 1) and \
                        (df['MACD_Flag'].iloc[-1] == 1 or df['MACD_Flag'].iloc[-2] == 1 or df['MACD_Flag'].iloc[-3] == 1):
                    position = 'long'
                    entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry_price = df['close'].iloc[-2]
                    contract = deposit * ratio * lev / entry_price
                    # 포지션 생성 문구 출력
                    #print(f"{entry_time} : Long position {username} entered at {entry_price}, contract {contract}", flush=True)
                elif (df['RSI_Flag'].iloc[-1] == -1 or df['RSI_Flag'].iloc[-2] == -1 or df['RSI_Flag'].iloc[-3] == -1) and \
                        (df['MACD_Flag'].iloc[-1] == -1 or df['MACD_Flag'].iloc[-2] == -1 or df['MACD_Flag'].iloc[-3] == -1):
                    position = 'short'
                    entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    entry_price = df['close'].iloc[-2]
                    contract = deposit * ratio * lev / entry_price
                    # 포지션 생성 문구 출력
                    #print(f"{entry_time} : Short position {username} entered at {entry_price}, contrat {contract}", flush=True)
            else:
                # 청산
                if position == 'long':
                    if df['close'].iloc[-2] >= entry_price * (1 + profit_ratio / 100) or df['close'].iloc[-2] <= entry_price * (1 - loss_ratio / 100):
                        exit_price = df['close'].iloc[-2]
                        exit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # 수익률 계산
                        profit = (exit_price - entry_price) * (1 - fee / 100) * contract
                        profit_rate = profit / (entry_price * contract)
                        profit_rate = round(profit_rate * 100)
                        deposit += profit

                        # 데이터베이스에 기록
                        connection = mysql.connector.connect(
                            user=USER,
                            password=PASSWORD,
                            host=HOST,
                            port=PORT,
                            database=DATABASE
                        )
                        cursor = connection.cursor()
                        query = f"INSERT INTO {username}aisimtrade (position, entryTime, entryPrice, exitTime, exitPrice, contract, profit, profitRate, deposit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
                    if df['close'].iloc[-2] <= entry_price * (1 - profit_ratio / 100) or df['close'].iloc[-2] >= entry_price * (1 + loss_ratio / 100):
                        exit_price = df['close'].iloc[-2]
                        exit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # 수익률 계산
                        profit = (entry_price - exit_price) * (1 - fee / 100) * contract
                        profit_rate = profit / (entry_price * contract)
                        profit_rate = round(profit_rate * 100)
                        deposit += profit

                        connection = mysql.connector.connect(
                            user=USER,
                            password=PASSWORD,
                            host=HOST,
                            port=PORT,
                            database=DATABASE
                        )
                        cursor = connection.cursor()
                        query = f"INSERT INTO {username}aisimtrade (position, entryTime, entryPrice, exitTime, exitPrice, contract, profit, profitRate, deposit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

            if(position is None):
                p = 'None'
            else:
                p = position
            # 현재 시간과 포지션, entry_price 출력
            #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " " + p + ", " + str(entry_price), flush=True)
            # 1분 sleep
            time.sleep(60)

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
    auto_trade(NAME, API_KEY, API_SECRET, SYMBOL, TIMEFRAME)
