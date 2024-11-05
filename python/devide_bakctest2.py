import pandas as pd
import pandas_ta as ta
import numpy as np
import os
import sys
import json
from sqlalchemy import create_engine

# 음수/양수 판별용 함수
def isplus(number):
    if number >= 0:  # 0은 확인을 위해 양수로 판별
        return True
    elif number < 0:
        return False
    

# 플래그 찍기
def update_flags(df):
    df['RSI_Flag'] = 0
    df['MACD_Flag'] = 0
    for i in range(1, df.shape[0]):
        # RSI, MACD의 부호가 바뀌면 플래그를 찍음(음->양 1, 양->음 -1)
        if df['MACD_hist'].iloc[i - 1] < 0 and df['MACD_hist'].iloc[i] > 0:
            df.at[df.index[i], 'MACD_Flag'] = 1
        elif df['MACD_hist'].iloc[i - 1] > 0 and df['MACD_hist'].iloc[i] < 0:
            df.at[df.index[i], 'MACD_Flag'] = -1
        if df['RSI_Hist'].iloc[i - 1] < 0 and df['RSI_Hist'].iloc[i] > 0:
            df.at[df.index[i], 'RSI_Flag'] = 1
        elif df['RSI_Hist'].iloc[i - 1] > 0 and df['RSI_Hist'].iloc[i] < 0:
            df.at[df.index[i], 'RSI_Flag'] = -1

    return df


# 데이터프레임 만들기
def make_dataframe(df):
    df['MovingAverage'] = ta.sma(df['close'], length=30)
    # 가격 변동
    df['Change'] = df['close'].diff()
    # 상승분과 하락분
    df['Gain'] = df['Change'].apply(lambda x: x if x > 0 else 0)
    df['Loss'] = df['Change'].apply(lambda x: -x if x < 0 else 0)
    # 평균 상승분과 평균 하락분 계산 (14일 기준)
    df['Avg_Gain'] = df['Gain'].rolling(window=14, min_periods=1).mean()
    df['Avg_Loss'] = df['Loss'].rolling(window=14, min_periods=1).mean()
    df['RS'] = df['Avg_Gain'] / df['Avg_Loss']
    # 지표 계산
    df['RSI'] = ta.rsi(df['close'], length=14)
    df[['MACD', 'MACD_signal', 'MACD_hist']] = ta.macd(df['close'], fast=12, slow=26, signal=9).iloc[:, [0, 2, 1]]
    df['MovingAverage'] = ta.sma(df['close'], length=30)
    df['RSI_Hist'] = df['RSI'] - ta.sma(df['RSI'], length=30)
    df = df.dropna()
    df['RSI_Hist'] = df['RSI'] - ta.sma(df['RSI'], length=30)

    df = update_flags(df)

    return df
 

def enter(index, entryList, df, position, money, lev):
    contract = money*lev/ df['close'].iloc[index]
    entryList.loc[entryList.shape[0]] = [position, df['datetime'].iloc[index], df['close'].iloc[index], contract]
    return entryList


def exit(index, LS, entryPrice, contract, exitList, df, state, fee, money, lev):
    if(LS=='Long'):
      profit = ((1-fee/100)*df['close'].iloc[index]-(1+fee/100)*entryPrice)*contract
    else:
      profit = ((1-fee/100)*entryPrice-(1+fee/100)*df['close'].iloc[index])*contract 
        
    exitList.loc[exitList.shape[0]] = [df['datetime'].iloc[index], df['close'].iloc[index], profit, state, money+profit] 
    return exitList


def chung(index, LS, entryPrice, contract, exitList, df, state, fee, money, lev):
    profit = -1*entryPrice*contract/lev-(df['close'].iloc[index]+entryPrice)*contract*fee/100
    exitList.loc[exitList.shape[0]] = [df['datetime'].iloc[index], df['close'].iloc[index], profit, state, money+profit] 
    return exitList


# 백테스트 해보기
def backtest(data, base, fee, ratio, lev):
    df = data
    state = 'None'  # 현재 포지션
    money = base  # 돈
    entry_list = pd.DataFrame(columns=['Type', 'Time', 'Price','Contract'])  # 엔트리 데이터프레임 만들기
    exit_list = pd.DataFrame(columns=['Time', 'Price', 'Profit', 'State', 'Money'])  # 엑시트 데이터프레임 만들기

    enterPrice=0
    contract=0
    # 반복문 돌려 포지션 기록
    for i in range(2, df.shape[0] - 1):
        if state == 'None': # 현재 포지션(Long or Short)이 없을 때
            if (df['RSI_Flag'].iloc[i] == 1 or df['RSI_Flag'].iloc[i - 1] == 1 or df['RSI_Flag'].iloc[i - 2] == 1) and \
                    (df['MACD_Flag'].iloc[i] == 1 or df['MACD_Flag'].iloc[i - 1] == 1 or df['MACD_Flag'].iloc[i - 2] == 1) and \
                        df['RSI'].iloc[i] < 70:  # 3틱 이내 LongSignal 겹치면 Long 진입
                state = 'Long'
                entry_list = enter(i, entry_list, df, state, money * ratio, lev)
                enterPrice = entry_list['Price'][entry_list.shape[0] - 1]
                contract = entry_list['Contract'][entry_list.shape[0] - 1]
            elif (df['RSI_Flag'].iloc[i] == -1 or df['RSI_Flag'].iloc[i - 1] == -1 or df['RSI_Flag'].iloc[i - 2] == -1) and \
                    (df['MACD_Flag'].iloc[i] == -1 or df['MACD_Flag'].iloc[i - 1] == -1 or df['MACD_Flag'].iloc[i - 2] == -1) and \
                        df['RSI'].iloc[i] > 30:  # 3틱 이내 ShortSignal 겹치면 Short 진입
                state = 'Short'
                entry_list = enter(i, entry_list, df, state, money * ratio, lev)
                enterPrice = entry_list['Price'][entry_list.shape[0] - 1]
                contract = entry_list['Contract'][entry_list.shape[0] - 1]
        else:
            if state == 'Long': # 현재 포지션(Long or Short)이 Long 일때
                if df['RSI'].iloc[i] >= 70:  # RSI 70 이상이면 Long 익절
                    check = 'icc'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0] - 1]
                    state = 'None'
                elif enterPrice * (1 - 1/lev) >= data['low'].iloc[i]:  # Long 청산
                    check = 'chung'
                    exit_list = chung(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0] - 1]
                    state = 'None'
            elif state == 'Short': # 현재 포지션(Long or Short)이 Short 일때
                if df['RSI'].iloc[i] <= 30:  # RSI 30 이하이면 Short 익절
                    check = 'icc'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0] - 1]
                    state = 'None'
                elif enterPrice * (1 + 1/lev) <= data['high'].iloc[i]:  # Short 청산
                    check = 'chung'
                    exit_list = chung(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0] - 1]
                    state = 'None'
        
    result_data = pd.DataFrame(columns=['Type', 'EntryTime', 'EntryPrice', 'Contract',
                                        'ExitTime', 'ExitPrice', 'Profit', 'Deposit', 'State'])  # 결과 데이터프레임 만들기
    
    result_data['Type'] = entry_list['Type']
    result_data['EntryTime'] = entry_list['Time']
    result_data['EntryPrice'] = entry_list['Price']
    result_data['Contract'] = entry_list['Contract']
    result_data['ExitTime'] = exit_list['Time']
    result_data['ExitPrice'] = exit_list['Price']
    result_data['Profit'] = exit_list['Profit']
    result_data['Deposit'] = exit_list['Money']
    result_data['State'] = exit_list['State']

    # 컬럼 순서 변경
    result_data = result_data[['Type', 'EntryTime', 'EntryPrice', 'Contract', 'ExitTime', 'ExitPrice', 'Profit', 'Deposit', 'State']]

    return result_data


# 승률 확인하는 함수
def check_winrate(data):
    win = 0
    for i in range(data.shape[0]):
        if (data['Profit'][i]>0):
            win += 1

    winrate = win / (data.shape[0])

    return winrate


# 데이터 선정(날짜 지정)하는 함수 - 날짜 형식은 반드시 yyyy-mm-dd 여야 함
def get_data(start_date, end_date):
    data = pd.DataFrame()
    # 입력받은 날짜들의 연도 추출
    start_year = start_date[:4]
    end_year = end_date[:4]

    try:
        # SQLAlchemy 엔진을 사용하여 데이터베이스에 연결
        with engine.connect() as connection:
            if start_year == end_year:  # 년도가 같으면 하나만
                query = f"SELECT * FROM binancedata{start_year} WHERE datetime BETWEEN '{start_date} 00:00:00' AND '{end_date} 23:59:59'"
                data = pd.read_sql(query, connection)
            else:  # 년도가 다르면 여러개 불러와서 합치기
                year_length = int(end_year) - int(start_year)
                data_frames = []
                for year in range(int(start_year), int(end_year) + 1):
                    start_time = f'{year}-01-01 0:00'
                    end_time = f'{year}-12-31 23:45'
                    query = f"SELECT * FROM binancedata{year} WHERE datetime BETWEEN '{start_time}' AND '{end_time}'"
                    data_frames.append(pd.read_sql(query, connection))
                
                data = pd.concat(data_frames, ignore_index=True)

            # 시작 날짜와 끝 날짜의 데이터만 선택
            start = start_date + " 0:00"
            end = end_date + " 23:45"
            data = data[(data['datetime'] >= start) & (data['datetime'] <= end)].reset_index(drop=True)

    except Exception as e:
        print(f"Error: {e}")

    return data


# MySQL 데이터베이스 연결 설정
user = 'root'
password = 'Cat2024!!'
host = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
port = '3306'
database = 'backtest'

# SQLAlchemy 엔진 생성
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}')

# result 데이터프레임을 MySQL 데이터베이스에 저장하는 함수
def save_to_database(df, table_name):
    try:
        df = df.reset_index(drop=True)
        df.insert(0,'id', df.index+1)
        df = df.drop(columns=['index'])
        # 데이터프레임을 데이터베이스에 저장
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        # print(f"{table_name} 테이블에 데이터가 저장되었습니다.")
    except Exception as e:
        print("")

if __name__ == "__main__":

    # start = '2020-01-01'
    # end = '2020-01-13'
    # b = 1000000
    # r = 0.3
    # l = 10

    start = sys.argv[1]
    end = sys.argv[2]
    b = int(sys.argv[3])
    r = float(sys.argv[4])
    l = int(sys.argv[5])
    # p_start = float(sys.argv[6])
    # p_end = float(sys.argv[7])
    # l_start = float(sys.argv[8])
    # l_end = float(sys.argv[9])
    f = 0.02

    df = get_data(start, end)
    df = make_dataframe(df)
    # df.to_csv('Tmp.csv')
    result = backtest(df, b, f, r, l)
    result = result.reset_index()
    result = result.dropna()
    
    save_to_database(result, 'trade')
    # result.to_csv('Result.csv')

    last_index = result.shape[0] - 1
    profit = result['Deposit'][last_index] - b
    profit_ratio = profit / b * 100
    winrate = check_winrate(result) * 100

    # print(start) # 시작일
    # print(end) # 완료일
    # print(str(b)) # 자본금
    # print(str(round(result['Deposit'][last_index]))) # 최종 환수금
    # print(str(round(profit)) + "(" + str(round(profit_ratio)) + "%)") # 수익
    # print(str(result.shape[0])) # 거래 횟수
    # print(str(round(winrate)) + "%") # 승률

    output = {
    'start': start,
    'end': end,
    'capital': str(b),
    'final_deposit': str(round(result['Deposit'][last_index])),
    'profit': str(round(profit)) + "(" + str(round(profit_ratio)) + "%)",
    'trade_count': str(result.shape[0]),
    'winrate': str(round(winrate)) + "%"
    }

    print(json.dumps(output))