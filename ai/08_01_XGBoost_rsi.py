import talib
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from imblearn.under_sampling import RandomUnderSampler

def preprocessing(df, windows=10):
    # 데이터 프레임 열 이름 표준화
    df.columns = [col.capitalize() for col in df.columns]

    df["Rsi"] = talib.RSI(df['Close'], timeperiod=14)
    df["Rsi_avg"] =df["Rsi"]- talib.SMA(df['Rsi'], timeperiod=30)
    df["Rsi_mvg"] = talib.SMA(df['Rsi'], timeperiod=30)
    df['Macd'], df['Macd_signal'], df['Macd_hist'] = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['Moving_average'] = talib.SMA(df['Close'], timeperiod=30)
    df['Label'] = (df['Close'].shift(-1) > df['Open'].shift(-1)).astype(int)

    # Rsi_label 열 생성 - 다음 값을 기준으로 현재 값의 부호 변화
    df['Rsi_next'] = df['Rsi_avg'].shift(-1)
    df['Rsi_label'] = 0
    df.loc[(df['Rsi_avg'] < 0) & (df['Rsi_next'] > 0), 'Rsi_label'] = 1
    df.loc[(df['Rsi_avg'] > 0) & (df['Rsi_next'] < 0), 'Rsi_label'] = 2

    # macd_hist_label 열 생성 - 다음 값을 기준으로 현재 값의 부호 변화
    df['Macd_hist_next'] = df['Macd_hist'].shift(-1)
    df['Macd_hist_label'] = 0
    df.loc[(df['Macd_hist'] < 0) & (df['Macd_hist_next'] > 0), 'Macd_hist_label'] = 1
    df.loc[(df['Macd_hist'] > 0) & (df['Macd_hist_next'] < 0), 'Macd_hist_label'] = 2

    df.dropna(inplace=True)

    # 윈도우 크기 설정
    rsi_windows = []
    macd_hist_windows = []
    macd_windows = []
    macd_signal_windows = []
    open_windows = []
    high_windows = []
    low_windows = []
    close_windows = []
    volume_windows = []
    rsi_labels = []
    macd_labels = []

    rsi_mvg_windows=[]

    for i in range(windows, len(df)):
        rsi_window = df['Rsi'].iloc[i - windows:i].values
        macd_hist_window = df['Macd_hist'].iloc[i - windows:i].values
        macd_window = df['Macd'].iloc[i - windows:i].values
        macd_signal_window = df['Macd_signal'].iloc[i - windows:i].values
        open_window = df['Open'].iloc[i - windows:i].values
        high_window = df['High'].iloc[i - windows:i].values
        low_window = df['Low'].iloc[i - windows:i].values
        close_window = df['Close'].iloc[i - windows:i].values
        volume_window = df['Volume'].iloc[i - windows:i].values
        rsi_label_window = df['Rsi_label'].iloc[i - 1]
        macd_label_window = df['Macd_hist_label'].iloc[i - 1]

        rsi_mvg_window = df['Rsi'].iloc[i - windows:i].values
        rsi_mvg_windows.append(rsi_mvg_window)

        rsi_windows.append(rsi_window)
        macd_hist_windows.append(macd_hist_window)
        macd_windows.append(macd_window)
        macd_signal_windows.append(macd_signal_window)
        open_windows.append(open_window)
        high_windows.append(high_window)
        low_windows.append(low_window)
        close_windows.append(close_window)
        volume_windows.append(volume_window)
        rsi_labels.append(rsi_label_window)
        macd_labels.append(macd_label_window)

    df_result = pd.DataFrame({
        'Rsi_windows': rsi_windows,
        'Macd_hist_windows': macd_hist_windows,
        'Macd_windows': macd_windows,
        'Macd_signal_windows': macd_signal_windows,
        'Open_windows': open_windows,
        'High_windows': high_windows,
        'Low_windows': low_windows,
        'Close_windows': close_windows,
        'Volume_windows': volume_windows,
        'Macd_label': macd_labels,
        'Rsi_label': rsi_labels,

        'Rsi_mvg':rsi_mvg_windows
    })

    return df_result

# 예시 데이터 불러오기 및 함수 적용
df_eth = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/A_eth.csv")
df_btc = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/A_btc.csv")
df_TSLA = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/TSLA_15.csv")
df_NVDA = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/NVDA_15.csv")
df_GOOGL = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/GOOGL_15.csv")
df_NDAQ = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/NDAQ_15.csv")
df_MSFT = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/MSFT_15.csv")
df_GOOG = pd.read_csv("C:/Users/lee/Desktop/CAT_AI/OneDrive_2024-07-17/GOOG_15.csv")

df_eth_processed = preprocessing(df_eth)
df_btc_processed = preprocessing(df_btc)
df_TSLA_processed = preprocessing(df_TSLA)
df_NVDA_processed = preprocessing(df_NVDA)
df_GOOGL_processed = preprocessing(df_GOOGL)
df_NDAQ_processed = preprocessing(df_NDAQ)
df_MSFT_processed = preprocessing(df_MSFT)
df_GOOG_processed = preprocessing(df_GOOG)

# 데이터 언더샘플링 함수
def undersample_data(df):
    under_sampler = RandomUnderSampler(random_state=42)
    X_resampled, y_resampled = under_sampler.fit_resample(df.drop(columns=['Macd_label', 'Rsi_label']), df['Rsi_label'])
    df_resampled = pd.DataFrame(X_resampled, columns=[
        'Rsi_windows', 'Macd_hist_windows', 'Macd_windows', 'Macd_signal_windows','Rsi_mvg',
        'Open_windows', 'High_windows', 'Low_windows', 'Close_windows', 'Volume_windows'])
    df_resampled['Rsi_label'] = y_resampled
    return df_resampled

# 언더샘플링
df_TSLA_resampled = undersample_data(df_TSLA_processed)
df_NVDA_resampled = undersample_data(df_NVDA_processed)
df_GOOGL_resampled = undersample_data(df_GOOGL_processed)
df_NDAQ_resampled = undersample_data(df_NDAQ_processed)
df_MSFT_resampled = undersample_data(df_MSFT_processed)
df_GOOG_resampled = undersample_data(df_GOOG_processed)

print(df_TSLA_processed['Rsi_label'].value_counts())

# 결합 데이터프레임 생성
df_combined = pd.concat([df_TSLA_resampled, df_NVDA_resampled, df_GOOGL_resampled, df_NDAQ_resampled, df_MSFT_resampled, df_GOOG_resampled], ignore_index=True)

# XGBoost를 위한 데이터 준비
X_combined = np.hstack([
    np.array(df_combined['Rsi_windows'].tolist()),
    np.array(df_combined['Macd_windows'].tolist()),
    np.array(df_combined['Macd_hist_windows'].tolist()),
    np.array(df_combined['Macd_signal_windows'].tolist()),
    np.array(df_combined['Open_windows'].tolist()),
    np.array(df_combined['High_windows'].tolist()),
    np.array(df_combined['Low_windows'].tolist()),
    np.array(df_combined['Close_windows'].tolist()),
    np.array(df_combined['Volume_windows'].tolist()),

    np.array(df_combined['Rsi_mvg'].tolist())
])
y_combined = df_combined['Rsi_label']

# 학습 데이터와 테스트 데이터로 나누기
X_train, X_test, y_train, y_test = train_test_split(X_combined, y_combined, test_size=0.2, random_state=42)

# 하이퍼파라미터 그리드 설정
param_dist = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 4, 5, 6],
    'learning_rate': [0.01, 0.1, 0.2, 0.3],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.7, 0.8, 0.9, 1.0]
}

# RandomizedSearchCV 설정
random_search = RandomizedSearchCV(estimator=xgb.XGBClassifier(random_state=42),
                                   param_distributions=param_dist,
                                   n_iter=100,
                                   scoring='accuracy',
                                   cv=3,
                                   verbose=2,
                                   random_state=42,
                                   n_jobs=-1)

# RandomizedSearchCV 실행
random_search.fit(X_train, y_train)

# 최적의 하이퍼파라미터 출력
print(f"Best parameters found: {random_search.best_params_}")

# 최적의 하이퍼파라미터로 모델 학습
best_model = random_search.best_estimator_
best_model.fit(X_train, y_train)

# 테스트 데이터 준비
X_test_btc = np.hstack([
    np.array(df_btc_processed['Rsi_windows'].tolist()),
    np.array(df_btc_processed['Macd_windows'].tolist()),
    np.array(df_btc_processed['Macd_hist_windows'].tolist()),
    np.array(df_btc_processed['Macd_signal_windows'].tolist()),
    np.array(df_btc_processed['Open_windows'].tolist()),
    np.array(df_btc_processed['High_windows'].tolist()),
    np.array(df_btc_processed['Low_windows'].tolist()),
    np.array(df_btc_processed['Close_windows'].tolist()),
    np.array(df_btc_processed['Volume_windows'].tolist()),

    np.array(df_btc_processed['Rsi_mvg'].tolist())
])
y_test_btc = df_btc_processed['Rsi_label']

X_test_eth = np.hstack([
    np.array(df_eth_processed['Rsi_windows'].tolist()),
    np.array(df_eth_processed['Macd_windows'].tolist()),
    np.array(df_eth_processed['Macd_hist_windows'].tolist()),
    np.array(df_eth_processed['Macd_signal_windows'].tolist()),
    np.array(df_eth_processed['Open_windows'].tolist()),
    np.array(df_eth_processed['High_windows'].tolist()),
    np.array(df_eth_processed['Low_windows'].tolist()),
    np.array(df_eth_processed['Close_windows'].tolist()),
    np.array(df_eth_processed['Volume_windows'].tolist()),

    np.array(df_eth_processed['Rsi_mvg'].tolist())
])
y_test_eth = df_eth_processed['Macd_label']

# 테스트 데이터로 예측 (BTC)
y_pred_btc = best_model.predict(X_test_btc)
accuracy_btc = accuracy_score(y_test_btc, y_pred_btc)
print(f"Accuracy - BTC: {accuracy_btc:.2f}")

# 테스트 데이터로 예측 (ETH)
y_pred_eth = best_model.predict(X_test_eth)
accuracy_eth = accuracy_score(y_test_eth, y_pred_eth)
print(f"Accuracy - ETH: {accuracy_eth:.2f}")


#### 모델 저장
import pickle

# 학습된 모델 저장
with open('best_model_macd.pkl', 'wb') as file:
    pickle.dump(best_model, file)
