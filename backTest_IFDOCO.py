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

basicSize = 0.1
maxSize = basicSize * 50
rangeD = 1000
pow = 0.9
reminTime = 180
sizeParam = 0
kurikaeshi = 3
LC = -1000000
inputfile = "output6_5sec.csv"

ohlcs = []
f = open(inputfile, "r")
reader = csv.DictReader(f)
for i in reader:
    ohlcs.append(i)
f.close()
#ohlcs = ohlcs[10000:27000]

shisan = 0
myPosition = {"side": "NULL", "size":0, "avePrice":0}
buyList = []
sellList = []
ltp = 0

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

def getSellAndBuyFlag():
    global myPosition
    global maxSize
    flag_buy = True
    flag_sell = True
    if random.randrange(100) < ( myPosition["size"]/maxSize * 100 ):
        flag_buy = False
        flag_sell = False
        if myPosition["side"] == "BUY":
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

def checkSellExcute(ohlc):
    global sellList
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

'''
updateDate = int(excution[0]["date"]) + 3
pfDate = int(excution[0]["date"]) + 60
x = []
y = []
for ex in excution:
    ltp = float(ex["price"])
    lenSell = len(sellList)
    for i in range(lenSell):
        if sellList[lenSell-1-i]["validDate"] < int(ex["date"]):
            sellList.pop(lenSell-1-i)
        elif sellList[lenSell-1-i]["price"] < ltp:
            excute("SELL",sellList[lenSell-1-i]["size"],sellList[lenSell-1-i]["price"])
            sellList.pop(lenSell-1-i)
    lenBuy = len(buyList)
    for i in range(lenBuy):
        if buyList[lenBuy-1-i]["validDate"] < int(ex["date"]):
            buyList.pop(lenBuy-1-i)
        elif buyList[lenBuy-1-i]["price"] > ltp:
            excute("BUY",buyList[lenBuy-1-i]["size"],buyList[lenBuy-1-i]["price"])
            buyList.pop(lenBuy-1-i)
    if int(ex["date"]) > updateDate:
        sellFlag, buyFlag = getSellAndBuyFlag()
        sellPrice, buyPrice = getSellAndBuyPrice()
        sellSize, buySize = getSellAndBuySize()
        if sellFlag:
            sellList.append({"size": sellSize, "price": sellPrice, "validDate": int(ex["date"])+reminTime})
        if buyFlag:
            buyList.append({"size": buySize, "price": buyPrice, "validDate": int(ex["date"])+reminTime})
        updateDate += 3
    if int(ex["date"]) > pfDate:
        pfDate += 60
        x.append(len(x))
        y.append(shisan)
'''
'''
xx = 0
for i in range(kurikaeshi):
    pfCounter = 0
    shisan = 0
    myPosition = {"side": "NULL", "size":0, "avePrice":0}
    buyList = []
    sellList = []
    ltp = 0
    x = []
    y = []
    sleep = 0
    for ohlc in ohlcs:
        if sleep > 0:
            sleep -= 1
        else:
            sleep = checkLC()
            pfCounter += 1
            if pfCounter > 20:
                x.append(len(x))
                y.append(shisan)
                pfCounter = 0
            ltp = float(ohlc["o"])
            checkSellExcute(ohlc)
            checkBuyExcute(ohlc)
            sellFlag, buyFlag = getSellAndBuyFlag()
            sellPrice, buyPrice = getSellAndBuyPrice()
            sellSize, buySize = getSellAndBuySize()
            if sellFlag:
                sellList.append({"size": sellSize, "price": sellPrice, "validDate": int(ohlc["date"])+reminTime})
            if buyFlag:
                buyList.append({"size": buySize, "price": buyPrice, "validDate": int(ohlc["date"])+reminTime})
    xx += shisan
print(xx/kurikaeshi,flush=True)
'''

shisan = 0
myPosition = {"side": "NULL", "size":0, "avePrice":0}
buyList = []
sellList = []
ltp = 0
x = []
y = []
sellIFDOCOList = []
buyIFDOCOList = []
sellOCOList = []
buyOCOList = []
def checkSellIFDOCO(ohlc):
    global sellIFDOCOList
    lenG = len(sellIFDOCOList)
    for i in range(lenG):
        if sellIFDOCOList[lenG-1-i]["validDate"] < int(ohlc["date"]):
            sellIFDOCOList.pop(lenG-1-i)
        elif sellIFDOCOList[lenG-1-i]["price"] < float(ohlc["h"]):
            excute("SELL",sellIFDOCOList[lenG-1-i]["size"],sellIFDOCOList[lenG-1-i]["price"])
            buyOCOList.append({"size":sellIFDOCOList[lenG-1-i]["size"], "prof": sellIFDOCOList[lenG-1-i]["prof"], "loss": sellIFDOCOList[lenG-1-i]["loss"]})
            sellIFDOCOList.pop(lenG-1-i)

def checkBuyIFDOCO(ohlc):
    global buyIFDOCOList
    lenG = len(buyIFDOCOList)
    for i in range(lenG):
        if buyIFDOCOList[lenG-1-i]["validDate"] < int(ohlc["date"]):
            buyIFDOCOList.pop(lenG-1-i)
        elif buyIFDOCOList[lenG-1-i]["price"] > float(ohlc["l"]):
            excute("BUY",buyIFDOCOList[lenG-1-i]["size"],buyIFDOCOList[lenG-1-i]["price"])
            sellOCOList.append({"size":buyIFDOCOList[lenG-1-i]["size"], "prof": buyIFDOCOList[lenG-1-i]["prof"], "loss": buyIFDOCOList[lenG-1-i]["loss"]})
            buyIFDOCOList.pop(lenG-1-i)

def checkBuyOCO(ohlc):
    global buyOCOList
    lenG = len(buyOCOList)
    for i in range(lenG):
        if buyOCOList[lenG-1-i]["prof"] > float(ohlc["l"]):
            excute("BUY",buyOCOList[lenG-1-i]["size"],buyOCOList[lenG-1-i]["prof"])
            buyOCOList.pop(lenG-1-i)
        elif buyOCOList[lenG-1-i]["loss"] < float(ohlc["h"]):
            excute("BUY",buyOCOList[lenG-1-i]["size"],buyOCOList[lenG-1-i]["loss"])
            buyOCOList.pop(lenG-1-i)

def checkSellOCO(ohlc):
    global sellOCOList
    lenG = len(sellOCOList)
    for i in range(lenG):
        if sellOCOList[lenG-1-i]["prof"] < float(ohlc["h"]):
            excute("SELL" ,sellOCOList[lenG-1-i]["size"],sellOCOList[lenG-1-i]["prof"])
            sellOCOList.pop(lenG-1-i)
        elif sellOCOList[lenG-1-i]["loss"] > float(ohlc["l"]):
            excute("SELL",sellOCOList[lenG-1-i]["size"],sellOCOList[lenG-1-i]["loss"])
            sellOCOList.pop(lenG-1-i)
LC = 2000
for ohlc in ohlcs:
    ltp = float(ohlc["o"])
    checkBuyIFDOCO(ohlc)
    checkSellIFDOCO(ohlc)
    checkBuyOCO(ohlc)
    checkSellOCO(ohlc)
    sellFlag, buyFlag = getSellAndBuyFlag()
    sellPrice, buyPrice = getSellAndBuyPrice()
    sellSize, buySize = getSellAndBuySize()
    if sellFlag:
        sellIFDOCOList.append({"size": sellSize, "price": sellPrice, "validDate": int(ohlc["date"])+reminTime, "prof": int(float(ohlc["o"])), "loss": int(float(ohlc["o"]))+LC})
    if buyFlag:
        buyIFDOCOList.append({"size": buySize, "price": buyPrice, "validDate": int(ohlc["date"])+reminTime, "prof": int(float(ohlc["o"])), "loss": int(float(ohlc["o"]))-LC})
    x.append(shisan)
print(shisan)

pyplot.plot(range(len(x)),x)
pyplot.ylabel("pl")
pyplot.xlabel("minute")
pyplot.show()
