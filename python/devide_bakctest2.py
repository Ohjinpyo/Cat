import pandas as pd
import pandas_ta as ta
import numpy as np
from multiprocessing import Pool
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


# RSI 구하기
def get_rsi_ma(df, period, ma_period):
    df['RSI'] = ta.rsi(df['close'], length=period)
    df['RSI_Hist'] = df['RSI'] - ta.sma(df['RSI'], length=ma_period)

    df['RSI_Flag'] = 0
    prev_value = df['RSI_Hist'].iloc[0]
    for i in range(1, len(df)):
        current_value = df['RSI_Hist'].iloc[i]
        if prev_value < 0 and current_value >= 0:
            if i >= 2:
                df.at[i-1, 'RSI_Flag'] = 1
            if i+2 < len(df):
                df.at[i, 'RSI_Flag'] = 1
                df.at[i+1, 'RSI_Flag'] = 1
                # df.at[i+2, 'RSI_Flag'] = 1
        elif prev_value >= 0 and current_value < 0:
            if i >= 2:
                df.at[i-1, 'RSI_Flag'] = -1
            if i+2 < len(df):
                df.at[i, 'RSI_Flag'] = -1
                df.at[i+1, 'RSI_Flag'] = -1
                # df.at[i+2, 'RSI_Flag'] = -1
        prev_value = current_value

    return df


# MACD 구하기
def get_macd(fast, slow, sig, df):
    df[['MACD', 'MACD_signal', 'MACD_hist']] = ta.macd(df['close'], fast=fast, slow=slow, signal=sig).iloc[:, [0, 2, 1]]
    df['MACD_Flag'] = 0
    prev_value = df['MACD_hist'].iloc[0]
    for i in range(1, len(df)):
        current_value = df['MACD_hist'].iloc[i]
        if prev_value < 0 and current_value >= 0:
            if i >= 2:
                df.at[i-1, 'MACD_Flag'] = 1
            if i+2 < len(df):
                df.at[i, 'MACD_Flag'] = 1
                df.at[i+1, 'MACD_Flag'] = 1
                # df.at[i+2, 'MACD_Flag'] = 1
        elif prev_value >= 0 and current_value < 0:
            if i >= 2:
                df.at[i-1, 'MACD_Flag'] = -1
            if i+2 < len(df):
                df.at[i, 'MACD_Flag'] = -1
                df.at[i+1, 'MACD_Flag'] = -1
                # df.at[i+2, 'MACD_Flag'] = -1
        prev_value = current_value

    return df


def enter(index, entryList, df, position, money, lev):
    contract = money*lev/ df['close'][index]
    entryList.loc[entryList.shape[0]] = [position, df['datetime'][index], df['close'][index], contract]
    return entryList


def exit(index, LS, entryPrice, contract, exitList, df, state, fee, money, lev):
    if(LS=='Long'):
      profit = ((1-fee/100)*df['close'][index]-(1+fee/100)*entryPrice)*contract
    else:
      profit = ((1-fee/100)*entryPrice-(1+fee/100)*df['close'][index])*contract 
        
    exitList.loc[exitList.shape[0]] = [df['datetime'][index], df['close'][index], profit, state, money+profit] 
    return exitList


def chung(index, LS, entryPrice, contract, exitList, df, state, fee, money, lev):
    profit = -1*entryPrice*contract/lev-(df['close'][index]+entryPrice)*contract*fee/100
    exitList.loc[exitList.shape[0]] = [df['datetime'][index], df['close'][index], profit, state, money+profit] 
    return exitList


# 백테스트 해보기
def backtest(data, base, fee, ratio, upSell, downSell, lev):
    df = data
    state = 'None'  # 현재 포지션
    money = base  # 돈
    upSell = upSell/100 + 1 # 익절 비율
    downSell = 1 - downSell/100 # 손절 비율
    entry_list = pd.DataFrame(columns=['Type', 'Time', 'Price','Contract'])  # 엔트리 데이터프레임 만들기
    exit_list = pd.DataFrame(columns=['Time', 'Price', 'Profit', 'State', 'Money'])  # 엑시트 데이터프레임 만들기

    enterPrice=0
    contract=0
    # 반복문 돌려 포지션 기록
    for i in range(0, df.shape[0]):
        if state == 'None': # 현재 포지션(Long or Short)이 없을 때
            if df['MACD_Flag'][i] == 1 and df['RSI_Flag'][i] == 1:  # Long 진입
                state = 'Long'
                entry_list = enter(i, entry_list, df, state, money*ratio, lev)
                enterPrice = entry_list['Price'][entry_list.shape[0]-1]
                contract = entry_list['Contract'][entry_list.shape[0]-1]
            elif df['MACD_Flag'][i] == -1 and df['RSI_Flag'][i] == -1:  # Short 진입
                state = 'Short'
                entry_list = enter(i, entry_list, df, state, money*ratio, lev)
                enterPrice = entry_list['Price'][entry_list.shape[0]-1]
                contract = entry_list['Contract'][entry_list.shape[0]-1]
        else:
            if state == 'Long': # 현재 포지션(Long or Short)이 Long 일때
                if enterPrice*upSell <= data['close'][i]:  # Long 익절
                    check = 'icc'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
                    state = 'None'
                elif enterPrice*downSell >= data['close'][i]:  # Long 손절
                    check = 'son'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
                    state = 'None'
                elif enterPrice*(1-1/lev)>= data['low'][i]:  # Long 청산
                    check = 'chung'
                    exit_list = chung(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
                    state = 'None'
            elif state == 'Short': # 현재 포지션(Long or Short)이 Short 일때
                if enterPrice*upSell >= data['close'][i]:  # Short 익절
                    check = 'icc'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
                    state = 'None'
                elif enterPrice*downSell <= data['close'][i]:  # Short 손절
                    check = 'son'
                    exit_list = exit(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
                    state = 'None'  
                elif  enterPrice*(1+1/lev)<= data['high'][i]:  # Short 청산
                    check = 'chung'
                    exit_list = chung(i, state, enterPrice, contract, exit_list, df, check, fee, money, lev)
                    money = exit_list['Money'][exit_list.shape[0]-1]
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


# 최적 지표 찾기
def find_param_worker(args):
    data, base, fee, ratio, p, l, lev = args
    result = backtest(data, base, fee, ratio, p, l, lev)
    result = result.dropna(axis=0)
    winrate = check_winrate(result) * 100

    return winrate, p, l


def find_params(data, base, fee, ratio, lev, p_start, p_end, l_start, l_end):
    num_cores = os.cpu_count()
    # 각각 0~2.0% 사이에서 최적 지표 찾기
    p_range = np.arange(p_start, p_end, 0.1)
    l_range = np.arange(l_start, l_end, 0.1)

    params_list = []
    for p in p_range:
        for l in l_range:
            params_list.append((data, base, fee, ratio, p, l, lev))

    with Pool(processes=num_cores) as pool:
        tmp_datas = pool.map(find_param_worker, params_list)

    top_winrate = -99999
    top_p = 0
    top_l = 0
    for tmp_data in tmp_datas:
        winrate, p, l = tmp_data
        if winrate > top_winrate:
            top_winrate = winrate
            top_p = p
            top_l = l

    detail_p_range = np.arange(top_p - 0.05, top_p + 0.05, 0.01)
    detail_l_range = np.arange(top_l - 0.05, top_l + 0.05, 0.01)

    params_list = []
    for detail_p in detail_p_range:
        for detail_l in detail_l_range:
            params_list.append((data, base, fee, ratio, detail_p, detail_l, lev))

    with Pool(processes=num_cores) as pool:
        last_datas = pool.map(find_param_worker, params_list)

    top_winrate = -99999
    detail_p = 0
    detail_l = 0
    for last_data in last_datas:
        winrate, p, l = last_data
        if winrate > top_winrate:
            top_winrate = winrate
            detail_p = p
            detail_l = l

    return detail_p, detail_l


# 쪼개서 백테스팅
def devide_backtest(base, fee, ratio,dataframe, devide, lev, p_start, p_end, l_start, l_end):
    data = dataframe
    money = base
    final_result = pd.DataFrame(columns=['Type', 'EntryTime', 'EntryPrice', 'Contract', 
                                         'ExitTime', 'ExitPrice', 'Profit', 'Deposit', 'State'])

    # 쪼갠 일자 분으로 변환
    devide_standard = devide * 24 * 4
    while(data.shape[0] > devide_standard):
        # 데이터 크기가 쪼개기보다 크면 쪼개기
        if data.shape[0] > devide_standard:
            sep_data = data.loc[0:devide_standard - 1]
            data.drop(labels=range(0, devide_standard), inplace=True)
            data = data.reset_index(drop=True)
        # 데이터 크기가 쪼개기보다 작으면 쪼개지 않기
        else:
            sep_data = data

        # 데이터 최적 승률 찾기
        p, l = find_params(sep_data, money, fee, ratio, lev, p_start, p_end, l_start, l_end)
        # print(p, l)
        # 찾은 승률로 백테스트(다음 데이터로)
        test_data = data.loc[0:devide_standard - 1]
        result_data = backtest(test_data, money, fee, ratio, p, l, lev)
        result_data = result_data.dropna(axis=0)
        
        # 자본금 최신화
        money = result_data['Deposit'][result_data.shape[0] - 1]
        final_result = pd.concat([final_result, result_data])
    
    return final_result

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
    # end = '2020-02-01'
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
    p_start = 0.100
    p_end = 2.000
    l_start = 0.100
    l_end = 1.000

    fast = 12
    slow = 26
    sig = 9
    per = 14
    m_per = 50
    f = 0.02
    d = 10
    df = get_data(start, end)
    df = get_macd(fast, slow, sig, df)
    df = get_rsi_ma(df, per, m_per)
    result = devide_backtest(b, f, r, df, d, l, p_start, p_end, l_start, l_end)
    result = result.reset_index()
    
    save_to_database(result, 'trade')
    # result.to_csv('C:/Users/jinpyo/IdeaProjects/demo/src/main/fronted/public/data/Result.csv')

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