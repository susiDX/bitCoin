import pybitflyer
import csv
import time
import random
import math
from matplotlib import pyplot

API_KEY = "WBFnwpPtQofhxXVmigD1yq" #yassan
API_SECRET = "Ms/9pnvqivvrgwbfLJy5hAs5yut3UVFyV6D0GDVJVaQ="
public_api = pybitflyer.API()
api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

#0.1 800
#0.3 800
basicSize = 0.1
reminTime = int(18/basicSize)
print(reminTime,flush=True)

rangeD = 1000
pow = 1
targetRange = 1000
targetPow = 1

sizeParam = 0
kurikaeshi = 3
LC = -1000000
maxSize = 5

inputfile = "output9_3sec.csv"
#print(reminTime,flush=True)

xlabel = "x"
ylabel = "y"

ohlcs = []
f = open(inputfile, "r")
reader = csv.DictReader(f)
for i in reader:
    ohlcs.append(i)
f.close()

shisan = 0
myPosition = {"side": "NULL", "size":0, "avePrice":0}
buyList = []
sellList = []

def init():
    global shisan
    global myPosition
    global sellList
    global buyList
    shisan = 0
    myPosition = {"side": "NULL", "size":0, "avePrice":0}
    buyList = []
    sellList = []

def excute(side, size, price):
    global shisan
    global myPosition
    if myPosition["side"] == "NULL":
        myPosition["side"] = side
        myPosition["size"] = size
        myPosition["avePrice"] = price
    elif side == "SELL":
        if myPosition["side"] == "BUY" and myPosition["size"] < size:
            shisan += myPosition["size"] * (price - myPosition["avePrice"])
            myPosition["side"] = "NULL"
            myPosition["size"] = 0
            myPosition["avePrice"] = 0
        elif myPosition["side"] == "BUY":
            shisan += size * (price - myPosition["avePrice"])
            myPosition["size"] -= size
        else:
            myPosition["avePrice"] = (myPosition["avePrice"]*myPosition["size"] + price*size)/(size+myPosition["size"])
            myPosition["size"] += size
    else: #side == BUY
        if myPosition["side"] == "SELL" and myPosition["size"] < size:
            shisan += myPosition["size"] * (myPosition["avePrice"] - price)
            myPosition["side"] = "NULL"
            myPosition["size"] = 0
            myPosition["avePrice"] = 0
        elif myPosition["side"] == "SELL":
            shisan += size * (myPosition["avePrice"] - price)
            myPosition["size"] -= size
        else:
            myPosition["avePrice"] = (myPosition["avePrice"]*myPosition["size"] + price*size)/(size+myPosition["size"])
            myPosition["size"] += size

def checkSellExcute(ohlc):
    global sellList
    sellList = sellList.sorted(sellList, key lambda x:x["validDate"]>100)
    lenSell = len(sellList)
    for i in range(lenSell):
        if sellList[lenSell-1-i]["validDate"] < int(ohlc["date"]):
            sellList.pop(lenSell-1-i)
        elif sellList[lenSell-1-i]["price"] < float(ohlc["h"]):
            excute("SELL",sellList[lenSell-1-i]["size"],sellList[lenSell-1-i]["price"])
            sellList.pop(lenSell-1-i)

def checkBuyExcute(ohlc):
    global buyList
    lenBuy = len(buyList)
    for i in range(lenBuy):
        if buyList[lenBuy-1-i]["validDate"] < int(ohlc["date"]):
            buyList.pop(lenBuy-1-i)
        elif buyList[lenBuy-1-i]["price"] > float(ohlc["l"]):
            excute("BUY",buyList[lenBuy-1-i]["size"],buyList[lenBuy-1-i]["price"])
            buyList.pop(lenBuy-1-i)

def getSellAndBuyFlag(shihyou):
    defaultSize = (sum(shihyou) / len(shihyou) - 0.5) * 10
    #defaultSize = 0
    global myPosition
    global maxSize

    flag_buy = True
    flag_sell = True
    size = myPosition["size"]
    if myPosition["side"] == "SELL":
        size = -size
    if random.randrange(100) < abs(( size - defaultSize ) / maxSize * 100 ):
        flag_buy = False
        flag_sell = False
        if defaultSize < size:
            flag_sell = True
        else:
            flag_buy = True
    return flag_sell, flag_buy

def getSellAndBuySize():
    global maxSize
    global basicSize
    global myPosition
    global sizeParam
    sellSize = basicSize
    buySize = basicSize
    if myPosition["side"] == "SELL":
        buySize *= myPosition["size"]/maxSize * sizeParam + 1
    else:
        sellSize *= myPosition["size"]/maxSize * sizeParam + 1
    return sellSize, buySize

def getSellAndBuyPrice():
    global rangeD
    global pow
    global ltp
    rnd =  math.pow(random.randrange(0,100,1), pow) / math.pow(100, pow) * rangeD
    #print(rnd,flush=True)
    sellPrice = ltp + rnd
    buyPrice = ltp - rnd
    return sellPrice, buyPrice

def kessai():
    global myPosition
    global ltp
    global shisan
    global sellList
    global buyList
    sellList = []
    buyList = []
    pnl = 0
    if myPosition["side"] == "SELL":
        pnl = (myPosition["avePrice"] - ltp) * myPosition["size"]
    elif myPosition["side"] == "BUY":
        pnl = (ltp - myPosition["avePrice"]) * myPosition["size"]
    shisan += pnl
    myPosition["side"] = "NULL"
    myPosition["size"] = 0
    myPosition["avePrice"] = 0

def checkLC():
    global myPosition
    global ltp
    pnl = 0
    if myPosition["side"] == "SELL":
        pnl = (myPosition["avePrice"] - ltp) * myPosition["size"]
    elif myPosition["side"] == "BUY":
        pnl = (ltp - myPosition["avePrice"]) * myPosition["size"]
    if pnl < LC:
        kessai()
        print("kessai",flush=True)
        return 20*5
    return 0

def test(kurikaeshi,rangeD,pow,flag_graph):
    global myPosition
    global buyList
    global sellList
    global ltp
    global shisan
    xx = 0
    print(str(rangeD)+" " + str(pow),flush=True)
    oneMinOHLCs = [1,0,1,0,1]
    ohlcsDate = int(ohlcs[0]["date"])
    oneMinP = int(float(ohlcs[0]["o"]))
    for i in range(kurikaeshi):
        myPosition = {"side": "NULL", "size":0, "avePrice":0}
        buyList = []
        sellList = []
        ltp = 0
        pfCounter = 0
        shisan = 0
        x = []
        sleep = 0
        for ohlc in ohlcs:
            if ohlcsDate + 60 < int(ohlc["date"]):
                ohlcsDate = int(ohlc["date"])
                oneMinOHLCs.pop(0)
                if int(float(ohlc["o"])) > oneMinP:
                    oneMinOHLCs.append(1)
                else:
                    oneMinOHLCs.append(0)
                oneMinP = int(float(ohlc["o"]))
                print(sum(oneMinOHLCs),flush=True)
            if sleep > 0:
                sleep -= 1
            else:
                sleep = checkLC()
                pfCounter += 1
                if flag_graph and pfCounter > 20:
                    x.append(shisan)
                    pfCounter = 0
                ltp = float(ohlc["o"])
                checkSellExcute(ohlc)
                checkBuyExcute(ohlc)
                sellFlag, buyFlag = getSellAndBuyFlag(oneMinOHLCs)
                sellPrice, buyPrice = getSellAndBuyPrice()
                sellSize, buySize = getSellAndBuySize()
                if sellFlag:
                    sellList.append({"size": sellSize, "price": sellPrice, "validDate": int(ohlc["date"])+reminTime})
                if buyFlag:
                    buyList.append({"size": buySize, "price": buyPrice, "validDate": int(ohlc["date"])+reminTime})
        xx += shisan
    if flag_graph:
        pyplot.plot(range(len(x)),x)
        pyplot.ylabel("pl")
        pyplot.xlabel("minute")
        pyplot.show()
    return xx/kurikaeshi
