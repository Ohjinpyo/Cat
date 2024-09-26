import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
import datetime
import sys
from ai import ai_test


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

# 투자 파라미터
# RATIO = 0.3
# LEV = 1
# P_START = 0.100
# P_END = 2.000
# L_START = 0.100
# L_END = 1.000
FEE = 0.02
RATIO = float(sys.argv[4])
LEV = int(sys.argv[5])
P_START = float(sys.argv[6])
P_END = float(sys.argv[7])
L_START = float(sys.argv[8])
L_END = float(sys.argv[9])

# 지갑 잔고 확인
def get_wallet():
    exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    })
    # 지갑 받아오기
    wallet = exchange.fetch_balance()
    wallet_usdt = wallet['free'].get('USDT', 0)

    return wallet_usdt


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
        CREATE TABLE IF NOT EXISTS {name}autotrade (
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
        query = f"DELETE FROM {name}autotrade"
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
        CREATE TABLE IF NOT EXISTS {name}autotrade (
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
        
        order_exchange = ccxt.binance({
                    'apiKey': key,
                    'secret': secret
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
        ratio = RATIO
        lev = LEV
        fee = FEE
        position = None 
        entry_price = 0
        loss_ratio = 0.02

        # 반복문
        while True:
            # 거래 상태 플래그 확인(데이터베이스)
            connection = mysql.connector.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                database=DATABASE
            )
            cursor = connection.cursor()
            query = "SELECT at FROM User WHERE username = %s"
            cursor.execute(query, (username,))
            all_rows = cursor.fetchall()
            flag = bool(all_rows[0][0])
            cursor.close()
            connection.close()

            # 거래 상태 플래그가 False면 거래 중단
            if flag == False:
                break

            # 계좌 잔고 가져오기
            deposit = get_wallet(order_exchange)

            # 체결 대기 있으면 취소
            resp = order_exchange.fetch_open_orders(
                symbol=symbol
            )
            if resp:
                cancel_resp = order_exchange.cancel_all_orders(symbol=symbol)

            # 주문 청산 됐는지 확인
            has_position = order_exchange.fetch_position(symbol=symbol)
            if position is not None and has_position:
                position = None

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
                    entry_price = df['close'].iloc[-2]
                    long_price_sl = entry_price * (1 - loss_ratio)
                    contract = deposit * ratio * lev / entry_price

                    # 포지션 진입 요청
                    buy_order = order_exchange.create_limit_buy_order(
                        symbol=symbol,
                        type="LIMIT",
                        side="buy",
                        amount=contract,
                        price=entry_price,
                        params={
                            'positionSide' : 'LONG'
                        }
                    )
                    buy_order_sl = order_exchange.create_limit_buy_order(
                        symbol=symbol,
                        type="STOP_MARKET",
                        side='sell',
                        amount=contract,
                        price=entry_price,
                        params={
                            'positionSide' : 'LONG',
                            'stopPrice' : long_price_sl
                        }
                    )
                elif (df['RSI_Flag'].iloc[-1] == -1 or df['RSI_Flag'].iloc[-2] == -1 or df['RSI_Flag'].iloc[-3] == -1) and \
                        (df['MACD_Flag'].iloc[-1] == -1 or df['MACD_Flag'].iloc[-2] == -1 or df['MACD_Flag'].iloc[-3] == -1):
                    position = 'short'
                    entry_price = df['close'].iloc[-2]
                    short_price_sl = entry_price * (1 + loss_ratio)
                    contract = deposit * ratio * lev / entry_price

                    # 포지션 진입 요청
                    sell_order = order_exchange.create_limit_buy_order(
                        symbol=symbol,
                        type="LIMIT",
                        side="sell",
                        amount=contract,
                        price=entry_price,
                        params={
                            'positionSide' : 'SHORT'
                        }
                    )
                    sell_order_sl = order_exchange.create_limit_buy_order(
                        symbol=symbol,
                        type="STOP_MARKET",
                        side='buy',
                        amount=contract,
                        price=entry_price,
                        params={
                            'positionSide' : 'SHORT',
                            'stopPrice' : short_price_sl
                        }
                    )

            elif position == 'long':
                if df['rsi'].iloc[-2] >= 70:
                        buy_order_tp = order_exchange.create_limit_buy_order(
                            symbol=symbol,
                            type="TAKE_PROFIT_MARKET",
                            side='sell',
                            amount=contract,
                            price=entry_price,
                            params={
                                'positionSide' : 'LONG',
                                'stopPrice' : df['close'].iloc[-2]
                            }
                        )
            elif position == 'short':
                if df['rsi'].iloc[-2] <= 30:
                        sell_order_tp = order_exchange.create_limit_buy_order(
                            symbol=symbol,
                            type="TAKE_PROFIT_MARKET",
                            side='buy',
                            amount=contract,
                            price=entry_price,
                            params={
                                'positionSide' : 'SHORT',
                                'stopPrice' : df['close'].iloc[-2]
                            }
                        )

            # sleep
            time.sleep(30)

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