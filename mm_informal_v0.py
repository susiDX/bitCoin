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
lcParam = 0.8
sizeParam = 0.5
reminingTime = 3
range = 1000
pow = 0.9
maxSize = 5

if flag_kato:
    reminingTime = 3
    sizeParam = 0.5
else:
    reminingTime = 3
    sizeParam = 0.5

API_KEY = ""
API_SECRET = ""
code = "FX_BTC_JPY"
if flag_kato:
    API_KEY = "9fJUAkKzsB98GcfNSVS6v2"
    API_SECRET = "tJTncG/b7EezfXM3nwonKrC76Nt4wZWLP8eH83soNh4="
else:
    API_KEY = "WBFnwpPtQofhxXVmigD1yq" #yassan
    API_SECRET = "Ms/9pnvqivvrgwbfLJy5hAs5yut3UVFyV6D0GDVJVaQ="

logIn(flag_kato)

public_api = pybitflyer.API()
api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

def getRnd(range, pow):
	rnd =  math.pow(random.randrange(0,100,1), pow) / math.pow(100, pow) * range
	return rnd

def getLC(basicSize, range):
    global lcParam
    return min(max(700,range),2000) * -100 * basicSize * lcParam

def init():
    order_all_cancel()
    global reminingTime
    global range
    basicSize = max(0.01,math.floor(api.getcollateral()["collateral"]/public_api.ticker(product_code = code)["ltp"] * 0.13 * 100000000)/100000000)
    maxSize = basicSize * 50
    LC = getLC(basicSize,range)
    lcCount = 0
    ltpSideCheckCounter = 0
    size, side = getPos()
    sleepingTime = 3

    basicSize *= 3/reminingTime
    if reminingTime >= 4:
        sleepingTime = int(2/3*reminingTime)
        basicSize *= sleepingTime/3

    return basicSize, maxSize, LC, lcCount, size, side, ltpSideCheckCounter, sleepingTime

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

basicSize, maxSize, LC, lcCount, size, side, ltpSideCheckCounter, sleepingTime = init()
print("basicSize = "+ str(basicSize),flush=True)
print("sleepingTime = " + str(sleepingTime),flush=True)
print("maxSize = "+str( maxSize),flush=True)
print("LC = " + str(LC), flush=True)
print("reminingTime = "+str(reminingTime),flush=True)
print("range = " + str(range),flush=True)
print("pow = " + str(pow),flush=True)
while True:
    try:
        col = get_open_collateral()
        if col < LC:
            serverKessai(api)
            col = get_open_collateral()
            while True:
                time.sleep(60 * 5)
                if serverCheck(api) == "NORMAL":
                    break
            lcCount += 1
            range *= 1.2
            if lcCount > 3:
                sys.exit()

        date = datetime.now()
        if date.hour == 3 and date.minute == 59:
            kessai()
            time.sleep(15*60)
        if date.hour == 23 and date.minute == 59:
            kessai()
            time.sleep(2*60)

        if ltpSideCheckCounter%3 == 0:
            ltpSideCheckCounter = 1
            size,side = getPos()
        else:
            ltpSideCheckCounter += 1
        ltp = get_ltp()
        sellPrice = ltp + getRnd(range, pow)
        buyPrice = ltp - getRnd(range, pow)
        flag_sell,flag_buy = getSellAndBuyFlag(maxSize, size, side)
        sellSize,buySize = getSellAndBuySize(basicSize, maxSize, size, side)
        if flag_sell:
            xx = order_limit("SELL", reminingTime, sellSize, sellPrice)
        if flag_buy:
            xx = order_limit("BUY", reminingTime, buySize, buyPrice)
        time.sleep(sleepingTime-0.3)

    except Exception as e:
        time.sleep(1)
        date = datetime.now()
        print(str(date) + " Error",flush=True)
        #print(traceback.format_exc())
