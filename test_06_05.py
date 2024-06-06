import asyncio
import ccxt.pro as ccxtpro
import os
import pandas as pd
import talib
from dotenv import load_dotenv
import datetime
from aiohttp import ClientTimeout
from sqlalchemy import create_engine,MetaData, Table, Column, Integer, String, Float, DateTime

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# MySQL 데이터베이스 연결 설정
user = 'root'
password = '1234'
host = 'localhost'
port = '3306'
database = 'tradelog'


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

async def main(stop_event):
    # 15분 데이터 초기 불러오기
    exchange = ccxtpro.binance({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
    })


    #                                                                                           ################
    # 데이터베이스 연결 엔진 생성
    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}", echo=True)
    
    # 거래 테이블 메타데이터 정의
    metadata = MetaData()
    trades_table = Table(
        'trades', metadata,
        Column('id', Integer, primary_key=True),
        Column('datetime', DateTime),
        Column('position', String(10)),
        Column('entry_price', Float),
        Column('exit_price', Float),
        Column('profit', Float)
    )
    
    # 메타데이터와 연결 엔진을 사용하여 테이블을 생성합니다.
    metadata.create_all(engine)
    #########################################################################################\



    balance = initial_balance
    position = None
    entry_price = 0
    trades_log = []

    while not stop_event.is_set():
        lookback = 50  # 초기 lookback 값 설정
        df = await fetch_and_update_data(exchange, symbol, timeframe, lookback) # 883ms정도 걸림        
        df = update_flags(df)

        await asyncio.sleep(10) #10초

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
                        async with engine.connect() as conn:
                            await conn.execute(trades_table.insert().values(
                                datetime=datetime.datetime.now(),
                                position=position,
                                entry_price=entry_price,
                                exit_price=exit_price,
                                profit=profit
                            ))
                        print(f"Long position exited at {exit_price} with profit {profit}")
                        position = None
                elif position == 'short':
                    if df['close'].iloc[-1] <= entry_price * (1 - take_profit_ratio) or df['close'].iloc[-1] >= entry_price * (1 + stop_loss_ratio):
                        exit_price = df['close'].iloc[-1]
                        profit = (entry_price - exit_price) / entry_price  # 수익률 계산
                        balance += profit
                        async with engine.connect() as conn:
                            await conn.execute(trades_table.insert().values(
                                datetime=datetime.datetime.now(),
                                position=position,
                                entry_price=entry_price,
                                exit_price=exit_price,
                                profit=profit
                            ))
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
    async with engine.connect() as conn:
        await conn.execute(trades_table.delete())

    await exchange.close()

def run_trading_bot():
    stop_event = asyncio.Event()

    def stop_bot():
        input("종료하려면 Enter 키를 누르세요...")
        stop_event.set()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, stop_bot)
    loop.run_until_complete(main(stop_event))

run_trading_bot()
