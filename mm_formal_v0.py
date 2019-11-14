from api_formal import *
import time
from datetime import datetime
import sys
import random
import math
import traceback

flag_kato = True
lcParam = 0.8
sizeParam = 0.5
reminingTime = 3
range = 1000
pow = 0.9
maxSize = 5

if flag_kato:
    reminingTime = 15
    range = 1000
else:
    reminingTime = 3
    range = 1000

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

def getRnd(range, pow):
	rnd =  math.pow(random.randrange(0,100,1), pow) / math.pow(100, pow) * range
	return rnd

def getLC(basicSize, range):
    global lcParam
    return min(max(700,range),2000) * -100 * basicSize  * lcParam

def init():
    cancelAllOrders(api)
    global reminingTime
    global range
    basicSize = max(0.01,math.floor(getCollateralAmount(api)/getLtp(public_api) * 0.13 * 100000000)/100000000)
    maxSize = basicSize * 50
    LC = getLC(basicSize,range)
    lcCount = 0
    ltpSideCheckCounter = 0
    size, side = getPos(api)
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

basicSize, maxSize, LC, lcCount, size, side, ltpSideCheckCounter,sleepingTime = init()
print("basicSize = "+ str(basicSize),flush=True)
print("sleepingTime = " + str(sleepingTime),flush=True)
print("maxSize = "+str( maxSize),flush=True)
print("LC = " + str(LC), flush=True)
print("reminingTime = "+str(reminingTime),flush=True)
print("range = " + str(range),flush=True)
print("pow = " + str(pow),flush=True)
lastApi = "NULL"
while True:
    try:
        start = time.time()
        lastApi = "Col"
        colOpen = getCollaratalOpen(api)
        elapsedtime = time.time() - start
        if elapsedtime > 1:
            print(str(xx)+ " " + str(colOpen),flush=True)

        if colOpen < LC:
            serverKessai(api)
            colOpen = getCollaratalOpen(api)
            time.sleep(60 * 5)
            lcCount += 1
            range *= 1.2
            if lcCount > 3:
                sys.exit()

        date = datetime.now()
        if date.hour == 3 and date.minute == 59:
            kessai(api)
            time.sleep(15*60)
        if date.hour == 23 and date.minute == 59:
            kessai(api)
            time.sleep(2*60)

        if ltpSideCheckCounter%3 == 0:
            ltpSideCheckCounter = 1
            start = time.time()
            lastApi = "Pos"
            size,side = getPos(api)
            elapsedtime = time.time() - start
            if elapsedtime > 1:
                print(str(xx)+ " " + str(side),flush=True)
        else:
            ltpSideCheckCounter += 1
        start = time.time()
        lastApi = "Ltp"
        ltp = getLtp(public_api)
        elapsedtime = time.time() - start
        if elapsedtime > 1:
            print(str(xx)+ " " + str(ltp),flush=True)
        sellPrice = ltp + getRnd(range, pow)
        buyPrice = ltp - getRnd(range, pow)
        flag_sell,flag_buy = getSellAndBuyFlag(maxSize, size, side)
        sellSize,buySize = getSellAndBuySize(basicSize, maxSize, size, side)
        if flag_sell:
            start = time.time()
            lastApi = "Sell"
            xx = sell_sashine(reminingTime, sellSize, sellPrice, api)
            elapsedtime = time.time() - start
            if elapsedtime > 1:
                print(str(xx)+ " " + str(elapsedtime),flush=True)
        if flag_buy:
            start = time.time()
            lastApi = "Buy"
            buy_sashine(reminingTime, buySize, buyPrice, api)
            elapsedtime = time.time() - start
            if elapsedtime > 1:
                print(str(xx)+ " " + str(elapsedtime),flush=True)
        time.sleep(sleepingTime-0.3)

    except Exception as e:
        time.sleep(1)
        date = datetime.now()
        print(str(date)+" " +str(lastApi),flush=True)
        print(traceback.format_exc())
