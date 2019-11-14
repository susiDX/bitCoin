import pybitflyer
import math
import requests
import time
from datetime import datetime

code = "FX_BTC_JPY"

def kessai(api):
    while True:
        cancelAllOrders(api)
        size,side = getPos(api)
        if size < 0.01:
            break
        elif side == "SELL":
            print("kessaiSELL",flush=True)
            xx = buy_nariyuki(size, api)
            print(xx,flush=True)
            if len(xx) == 1:
                break
        elif side == "BUY":
            print("kessaiBUY",flush=True)
            xx = sell_nariyuki(size, api)
            print(xx,flush=True)
            if len(xx) == 1:
                break
        time.sleep(2)

def serverKessai(api):
    date = datetime.now()
    print(str(date) + "____________________________________________",flush=True)
    kessai(api)
    serverCheck(api)
    size, side = getPos(api)
    print(str(size) + "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",flush=True)

def serverCheck(api):
    while True:
        time.sleep(5)
        health = getHealth(api)
        if health == "NORMAL":
            break

def cancelAllOrders(api):
    api.cancelallchildorders(product_code = code)

def getPos(api):
    side = ""
    size = 0
    poss = api.getpositions(product_code = code)
    if len(poss) != 0:
        for pos in poss:
            global beforeSide
            global beforeSize
            try:
                side = pos["side"]
                size += pos["size"]
            except Exception as e:
                date = datetime.now()
                print(date,flush=True)
                side = beforeSide
                size = beforeSize
            beforeSide = side
            beforeSize = size
    return size,side

def getCollateralAmount(api):
    return api.getcollateral()["collateral"]

def getLtp(public_api):
    return public_api.ticker(product_code = code)["ltp"]

def getCollaratalOpen(api):
    return api.getcollateral()['open_position_pnl']

def getHealth(api):
    return api.getboardstate(product_code=code)["health"]

def sell_nariyuki(size,api):
    xx = api.sendchildorder(product_code = code,child_order_type = "MARKET", side = "SELL", size = math.floor(100000000*size)/100000000)
    return xx

def buy_nariyuki(size,api):
    xx = api.sendchildorder(product_code = code,child_order_type = "MARKET", side = "BUY", size = math.floor(100000000*size)/100000000)
    return xx

def buy_sashine(reminingTime, size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "BUY", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx

def sell_sashine(reminingTime, size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "SELL", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx

def sell_sashineDX(reminingTime, size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "SELL", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    count = 0
    while True:
        count += 1
        if len(xx) == 1 or count > 20:
            break
        else:
            time.sleep(2)
            xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "SELL", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx

def buy_sashineDX(reminingTime, size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "BUY", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    count = 0
    while True:
        count += 1
        if len(xx) == 1 or count > 20:
            break
        else:
            time.sleep(2)
            xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT", minute_to_expire = reminingTime, side = "BUY", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx
