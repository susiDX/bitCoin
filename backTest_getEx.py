import pybitflyer
import csv
import time
import random
import math
from matplotlib import pyplot
from api_informal import *

outputfile = "output11.csv"
ids = 50000 #2000000==14hours


API_KEY = "WBFnwpPtQofhxXVmigD1yq" #yassan
API_SECRET = "Ms/9pnvqivvrgwbfLJy5hAs5yut3UVFyV6D0GDVJVaQ="
public_api = pybitflyer.API()
api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

logIn(False)
start = time.time()
order_market("BUY", 0.01)
print(time.time() - start,flush=True)

f = open(outputfile, "w")
fieldnames = ['side', 'price', 'date']
writer = csv.DictWriter(f,fieldnames = fieldnames)
writer.writeheader()

values = []
executions = public_api.executions(product_code="FX_BTC_JPY",count=500)
iddd = executions[0]["id"]
print(executions[0]["exec_date"],flush=True)
for i in executions:
    side = i["side"]
    price = i["price"]
    date = int(i["exec_date"][8:10])*3600*24 + int(i["exec_date"][11:13])*3600 + int(i["exec_date"][14:16])*60 + int(i["exec_date"][17:19])
    values.append({"side": side, "price": price, "date":date})
last_id = executions[-1]["id"]
writer.writerows(values)

while True:
    values = []
    executions = public_api.executions(product_code="FX_BTC_JPY", before=last_id, count=500)
    for i in executions:
        side = i["side"]
        price = i["price"]
        date = int(i["exec_date"][8:10])*3600*24 + int(i["exec_date"][11:13])*3600 + int(i["exec_date"][14:16])*60 + int(i["exec_date"][17:19])
        values.append({"side": side, "price": price, "date":date})
    last_id = executions[-1]["id"]
    print(executions[-1]["exec_date"],flush=True)
    writer.writerows(values)
    if last_id < iddd - ids:
        break
f.close()

'''
excution = []
f = open("output.csv", "r")
reader = csv.DictReader(f)
for i in reader:
    excution.append(i)
f.close()
excution.reverse()

shisan = 0
myPosition = {"side": "NULL", "size":0, "avePrice":0}
buyList = []
sellList = []
ltp = 0
pow += 0.1
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
    if random.randrange(100)<(myPosition["size"]/maxSize * 100):
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
    sellSize = basicSize
    buySize = basicSize
    if myPosition["side"] == "SELL":
        buySize *= myPosition["size"]/maxSize + 1
    else:
        sellSize *= myPosition["size"]/maxSize + 1
    return sellSize, buySize

def getSellAndBuyPrice():
    global rangeD
    global pow
    global ltp
    tyouseiParam = rangeD / math.pow(rangeD, pow)
    rnd =  math.pow(random.randrange(0,rangeD,1), pow) * tyouseiParam
    sellPrice = ltp + rnd
    buyPrice = ltp - rnd
    return sellPrice, buyPrice

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

pyplot.plot(x, y)
pyplot.ylabel("pl")
pyplot.xlabel("minute")
pyplot.show()
'''
