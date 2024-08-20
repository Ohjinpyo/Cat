import ccxt
import pandas as pd
import pandas_ta as ta
import time
import mysql.connector
import datetime
import sys

# NAME = sys.argv[1]
# API_KEY = sys.argv[2]
# API_SECRET = sys.argv[3]

key = 'BBuXPScjNckeStgURfoKG1Dk5eFQVKiO7hpVfjPBZVovF0N87INWp27NbUZnqicQ'
sec = 'JR9dho2nwoOUgWoHVnAo6lDekKfyUkemKb7RB0sMui3ladFv9ND7nPkDJVap3ukA'

SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'

USER = 'root'
PASSWORD = 'Cat2024!!'
HOST = 'capstonedb.cd4co2ui6q38.ap-northeast-2.rds.amazonaws.com'
PORT = '3306'
DATABASE = 'backtest'

# 투자 파라미터
BALANCE = 1000000
FEE = 0.02
RATIO = 0.3
LEV = 1
P_START = 0.100
P_END = 2.000
L_START = 0.100
L_END = 1.000
# BALANCE = int(sys.argv[4])
# FEE = 0.02
# RATIO = float(sys.argv[5])
# LEV = int(sys.argv[6])
# P_START = float(sys.argv[7])
# P_END = float(sys.argv[8])
# L_START = float(sys.argv[9])
# L_END = float(sys.argv[10])

# 지갑 잔고 확인
def get_wallet(exchange):
    wallet = exchange.fetch_balance()
    # wallet_usdt = wallet['free'].get('USDT', 0)

    return wallet

exchange = ccxt.binance({
        'apiKey': key,
        'secret': sec,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'timeout': 30000,  # 타임아웃 시간을 30초로 설정
         })

print(get_wallet(exchange))