import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# 데이터 로딩
df_btc = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/A_btc.csv", parse_dates=['Datetime'], index_col='Datetime')

# 필요한 열 선택
df = df_btc[['Rsi', 'Macd', 'MacdSignal', 'MacdHist']]

# 특성과 타겟 변수 정의
features = df[['Rsi', 'Macd', 'MacdSignal']].values
target = df['MacdHist'].values

# 데이터 정규화
scaler_features = MinMaxScaler()
scaled_features = scaler_features.fit_transform(features)

scaler_target = MinMaxScaler()
scaled_target = scaler_target.fit_transform(target.reshape(-1, 1))

# 스케일러 저장
joblib.dump(scaler_features, 'scaler_features.pkl')
joblib.dump(scaler_target, 'scaler_target.pkl')

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
history = model.fit(X_train_seq, y_train_seq, epochs=50, batch_size=32, validation_split=0.1)

# 모델 평가
loss = model.evaluate(X_test_seq, y_test_seq)
print(f'Test Loss: {loss}')

# 예측
y_pred = model.predict(X_test_seq)
y_pred = scaler_target.inverse_transform(y_pred)
y_test = scaler_target.inverse_transform(y_test_seq)

# 성능 지표 계산
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
print(f'RMSE: {rmse}')
print(f'R² Score: {r2}')

# 정확도 계산 (절대 오차가 임계값 이내인 경우의 비율)
threshold = 0.1  # 예: 0.1의 임계값
accuracy = np.mean(np.abs(y_pred - y_test) < threshold)
print(f'Accuracy: {accuracy * 100:.2f}%')

# 모델 저장
save_model(model, "btc_macd_hist_predictor.h5")

# 결과 시각화
plt.figure(figsize=(14, 7))
plt.plot(range(len(y_test)), y_test, label='Actual MACD Hist', color='blue')
plt.plot(range(len(y_pred)), y_pred, label='Predicted MACD Hist', color='red')
plt.xlabel('Time')
plt.ylabel('MACD Hist')
plt.legend()
plt.title('MACD Histogram Prediction')
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
