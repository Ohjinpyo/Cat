import ccxt
import pandas as pd
import numpy as np
import time
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas_ta as ta
import joblib


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

SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'
API_KEY = 'yz5twLkIxD7y3rGJuY04IA4PUJR0Upk9DS9jBD4oWZBg5kLJIDqIdOTLXPxvholU'
API_SECRET = 'LE8Gqnjg6ZhxBnyERuEUe5tSpEGE656gb3VjEzIWd2NaiR1v52pzedstugvZNjG0'

# 바이낸스 거래소 객체 생성
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    },
    'timeout': 30000,  # 타임아웃 시간을 30초로 설정
})

# 데이터 업데이트
# df = fetch_and_update_data(exchange, SYMBOL, TIMEFRAME, lookback=60)
# df['Rsi'] = ta.rsi(df['close'], length=14)
# macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
# df['Macd'] = macd['MACD_12_26_9']
# df['MacdSignal'] = macd['MACDs_12_26_9']
# df['MacdHist'] = macd['MACDh_12_26_9']
# df['MovingAverage'] = ta.sma(df['close'], length=30)
# df['Rsi_avg'] = df['Rsi'] - ta.sma(df['Rsi'], length=30)

# NaN 값 제거
# df = df.dropna()

def set_model_macd():    
    # 모델 및 스케일러 로드
    # model_macd_hist = load_model("D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/btc_macd_hist_predictor.h5")
    # scaler_features_macd = joblib.load('D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/scaler_features_macd.pkl')
    # scaler_target_macd = joblib.load('D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/scaler_target_macd.pkl')
    model_macd_hist = load_model("/home/ec2-user/ttttt/python/ai/btc_macd_hist_predictor.h5")
    scaler_features_macd = joblib.load('/home/ec2-user/ttttt/python/ai/scaler_features_macd.pkl')
    scaler_target_macd = joblib.load('/home/ec2-user/ttttt/python/ai/scaler_target_macd.pkl')

    return model_macd_hist, scaler_features_macd, scaler_target_macd

def set_model_rsi():

    # model_rsi_avg = load_model("D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/btc_onlyrsi_predictor.h5")
    # scaler_features_rsi = joblib.load('D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/scaler_features_onlyrsi.pkl')
    # scaler_target_rsi = joblib.load('D:/study/college/capstone/capstoneCode/java/springboot/ttttt/python/ai/scaler_target_onlyrsi.pkl')
    model_rsi_avg = load_model("/home/ec2-user/ttttt/python/ai/btc_onlyrsi_predictor.h5")
    scaler_features_rsi = joblib.load('/home/ec2-user/ttttt/python/ai/scaler_features_onlyrsi.pkl')
    scaler_target_rsi = joblib.load('/home/ec2-user/ttttt/python/ai/scaler_target_onlyrsi.pkl')

    return model_rsi_avg, scaler_features_rsi, scaler_target_rsi


def get_predict(model_macd_hist, scaler_features_macd, scaler_target_macd, model_rsi_avg, scaler_features_rsi, scaler_target_rsi, df):
    # 특성과 타겟 변수 정의
    features_macd = df[['Rsi', 'Macd', 'MacdSignal']].values[-10:]
    features_rsi = df[['Rsi_avg','RS','Avg_Gain','Avg_Loss','Gain','Loss','Change','Rsi_movingavg']].values[-10:]

    scaled_features_macd = scaler_features_macd.transform(features_macd)
    scaled_features_rsi = scaler_features_rsi.transform(features_rsi)

    # LSTM 입력 형태로 데이터 변환
    X_recent_seq_macd = scaled_features_macd.reshape((1, 10, scaled_features_macd.shape[1]))
    X_recent_seq_rsi = scaled_features_rsi.reshape((1, 10, scaled_features_rsi.shape[1]))

    # 예측
    y_pred_macd = model_macd_hist.predict(X_recent_seq_macd, verbose=0)
    y_pred_macd = scaler_target_macd.inverse_transform(y_pred_macd)

    y_pred_rsi = model_rsi_avg.predict(X_recent_seq_rsi, verbose=0)
    y_pred_rsi = scaler_target_rsi.inverse_transform(y_pred_rsi)

    # 결과 출력
    return y_pred_macd, y_pred_rsi



# 결과 출력
# print(f'Predicted MACD Hist: {y_pred_macd[0][0]}')
# print(f'Predicted RSI Avg: {y_pred_rsi[0][0]}')

# # 결과 시각화 (Optional)
# plt.figure(figsize=(14, 7))
# plt.plot(df.index, df['MacdHist'], label='Actual MACD Hist', color='blue')
# plt.axhline(y=y_pred_macd[0][0], color='red', linestyle='--', label='Predicted MACD Hist')
# plt.xlabel('Time')
# plt.ylabel('MACD Hist')
# plt.legend()
# plt.title('MACD Histogram Prediction')
# plt.show()

# plt.figure(figsize=(14, 7))
# plt.plot(df.index, df['Rsi_avg'], label='Actual RSI Avg', color='blue')
# plt.axhline(y=y_pred_rsi[0][0], color='red', linestyle='--', label='Predicted RSI Avg')
# plt.xlabel('Time')
# plt.ylabel('RSI Avg')
# plt.legend()
# plt.title('RSI Avg Prediction')
# plt.show()

# # 데이터 출력
# print(df)
