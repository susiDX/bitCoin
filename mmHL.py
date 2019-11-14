CHANNEL = "lightning_executions_FX_BTC_JPY"
import websocket
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from api_informal import *
import time
from datetime import datetime
import sys
import random
import math
import pybitflyer
import traceback

flag_kato = True
reminingTime = 10
basicSize = 1
maxSize = 5
sizeParam = 0
sleepingTime = 2.6

if flag_kato:
    reminingTime = 10
    basicSize = 0.01
    maxSize = basicSize * 5
else:
    reminingTime = 10
    basicSize = 0.1
    maxSize = basicSize * 5

API_KEY = ""
API_SECRET = ""
code = "FX_BTC_JPY"
if flag_kato:
    API_KEY = "9fJUAkKzsB98GcfNSVS6v2"
    API_SECRET = "tJTncG/b7EezfXM3nwonKrC76Nt4wZWLP8eH83soNh4="
else:
    API_KEY = "WBFnwpPtQofhxXVmigD1yq" #yassan
    API_SECRET = "Ms/9pnvqivvrgwbfLJy5hAs5yut3UVFyV6D0GDVJVaQ="
public_api = pybitflyer.API()
api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

logIn(flag_kato)

def getSellAndBuySize(basicSize, maxSize, size, side):
    global sizeParam
    sellSize = basicSize
    buySize = basicSize
    if side == "SELL":
        buySize *= size/maxSize * sizeParam + 1
    else:
        sellSize *= size/maxSize * sizeParam + 1
    return sellSize, buySize

def getSellAndBuyFlag(maxSize, size, side):
    flag_buy = True
    flag_sell = True
    if random.randrange(100)<(size/maxSize * 100):
        flag_buy = False
        flag_sell = False
        if side == "BUY":
            flag_sell = True
        else:
            flag_buy = True
    return flag_sell, flag_buy

def getTime(date):
    overSec = int(executions[0]["exec_date"][8:10])*3600*24 + int(executions[0]["exec_date"][11:13])*3600 + int(executions[0]["exec_date"][14:16])*60 + int(executions[0]["exec_date"][17:19])
    miliSec = 0
    if len(executions[0]["exec_date"]) == 23:
        miliSec = int(executions[0]["exec_date"][20:23])
    elif len(executions[0]["exec_date"]) == 22:
        miliSec = int(executions[0]["exec_date"][20:22])*10
    elif len(executions[0]["exec_date"]) == 21:
        miliSec = int(executions[0]["exec_date"][20:22])*100
    else:
        miliSec = 0
    return overSec

low = 10000000
high = 0
start = time.time()
def on_message(ws, message):
    try:
        global low
        global high
        global sellList
        global buyList
        global start
        messageDX = json.loads(message)
        params_message = messageDX["params"]["message"]
        eTime = time.time() - start
        for p in params_message:
            high = max(p["price"],high)
            low = min(p["price"], low)
        if eTime > sleepingTime:
            size, side = getPos()
            flag_sell,flag_buy = getSellAndBuyFlag(maxSize, size, side)
            sellSize,buySize = getSellAndBuySize(basicSize, maxSize, size, side)
            sp = high - low - 4
            if flag_sell and high!=0 and sp>5:
                order_limit("SELL", 1, sellSize, high - 2)
            if flag_buy and low!=10000000 and sp>5:
                order_limit("BUY", 1, buySize, low + 2)
            board = my_board()
            for b in board:
                x = datetime.now()
                nowTime = x.day * 3600*24 + x.hour*3600 + x.minute*60 + x.second - 3600*9
                orderTime = int(b["order_id"][9:11])* 3600*24  + int(b["order_id"][12:14])*3600 + int(b["order_id"][14:16])*60 + + int(b["order_id"][16:18])
                if orderTime < nowTime-9:
                    order_cancel(b["order_id"])

            low = 10000000
            high = 0
            start = time.time()
    except Exception as e:
        date = datetime.now()
        print(date,flush=True)
        print(traceback.format_exc())
        time.sleep(1)

def on_open(ws):
    global start
    start = time.time()
    ws.send(json.dumps({"method": "subscribe", "params": {"channel": CHANNEL}}))

if __name__ == "__main__":
    while True:
        try:
            ws = websocket.WebSocketApp("wss://ws.lightstream.bitflyer.com/json-rpc", on_message=on_message, on_open=on_open)
            ws.run_forever()
        except Exception as e:
            date = datetime.now()
            print(date,flush=True)
            print(traceback.format_exc())
            time.sleep(1)
