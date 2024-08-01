import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import talib

# 데이터 로딩
df_btc = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/A_btc.csv", parse_dates=['Datetime'], index_col='Datetime')
df_btc['Rsi_avg'] = df_btc["Rsi"]- talib.SMA(df_btc['Rsi'], timeperiod=30)
# 필요한 열 선택
df = df_btc[['Rsi', 'Macd', 'MacdSignal', 'Close','Open','High','Low','MacdSignal','MacdHist','MovingAverage','Rsi_avg']]

##

##
# 특성과 타겟 변수 정의
features = df[['Rsi','Macd', 'MacdSignal','Open','High','Low','MacdSignal','MacdHist','MovingAverage']].values
target = df['Rsi_avg'].values

# 데이터 정규화
scaler_features = MinMaxScaler()
scaled_features = scaler_features.fit_transform(features)

scaler_target = MinMaxScaler()
scaled_target = scaler_target.fit_transform(target.reshape(-1, 1))

# 데이터셋 분할
X_train, X_test, y_train, y_test = train_test_split(scaled_features, scaled_target, test_size=0.2, shuffle=False)

# LSTM 입력 형태로 데이터 변환
def create_sequences(X, y, seq_length):
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_length):
        X_seq.append(X[i:i+seq_length])
        y_seq.append(y[i+seq_length])
    return np.array(X_seq), np.array(y_seq)

SEQ_LENGTH = 10  # 예를 들어, 10개의 타임스텝 사용
X_train_seq, y_train_seq = create_sequences(X_train, y_train, SEQ_LENGTH)
X_test_seq, y_test_seq = create_sequences(X_test, y_test, SEQ_LENGTH)

# LSTM 모델 구축
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(SEQ_LENGTH, X_train_seq.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(50, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1))  # 타겟이 1차원이므로 Dense(1)
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 학습
history = model.fit(X_train_seq, y_train_seq, epochs=20, batch_size=32, validation_split=0.1)

# 모델 평가
loss = model.evaluate(X_test_seq, y_test_seq)
print(f'Test Loss: {loss}')

# 예측
y_pred = model.predict(X_test_seq)
y_pred = scaler_target.inverse_transform(y_pred)
y_test = scaler_target.inverse_transform(y_test_seq)

# 결과 시각화
plt.figure(figsize=(14, 7))
plt.plot(range(len(y_test)), y_test, label='Actual Close Price', color='blue')
plt.plot(range(len(y_pred)), y_pred, label='Predicted Close Price', color='red')
plt.xlabel('Time')
plt.ylabel('Close Price')
plt.legend()
plt.title('Close Price Prediction')
plt.show()

# 학습 과정 시각화
plt.figure(figsize=(14, 7))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Model Loss during Training')
plt.show()
