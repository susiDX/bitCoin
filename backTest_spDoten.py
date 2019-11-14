import requests
from datetime import datetime
import time
from matplotlib import pyplot

saitekiTime = 20
num = 2
targetSP = 300
flag_balance = False

def get_price(min, before=0, after=0):
	price = []
	params = {"periods" : min }
	if before != 0:
		params["before"] = before
	if after != 0:
		params["after"] = after
	response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params)
	data = response.json()

	if data["result"][str(min)] is not None:
		for i in data["result"][str(min)]:
			price.append({ "close_time" : i[0],
				"close_time_dt" : datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
				"open_price" : i[1],
				"high_price" : i[2],
				"low_price" : i[3],
				"close_price": i[4] })
		return price
	else:
		print("データが存在しません")
		return None

def trendCheck(price,num,count):
	countDown = 0
	countUp = 0
	for i in range(num):
		if price[count-1-i]["close_price"] > price[count-1-i]["open_price"]:
			countUp += 1
		else:
			countDown +=1
	if countUp > num/2:
		return "UP"
	elif countDown > num/2:
		return "DOWN"
	else:
		return "NULL"

date = datetime.now()
time = 1547046000 - 86400*10 + 86400*date.day + 3600*(date.hour-saitekiTime) + 60*date.minute + 86400*(31)
ashi = 1
sp = 100
pos = "SELL"
xx = []
yy = []

TorihikiTimes = 0
price = get_price(60*ashi, after=time)
while True:
	sp += 20
	lastTorihiki = price[0]["open_price"]
	count = num
	shisan = 0
	x = []
	y = []
	while True:
	    count+=1
	    x.append(len(x))
	    y.append(shisan)
	    if len(price)-2 < count:
	        if pos == "SELL":
	             shisan += (lastTorihiki - price[count]["open_price"])
	        elif pos=="BUY":
	             shisan += (price[count]["open_price"]-lastTorihiki)
	        x.append(len(x))
	        y.append(shisan)
	        break;
	    countDX = 0
	    aa = []
	    bb = []
	    while True:
	        countDX += 1
	        aa.append(price[count - countDX]["high_price"])
	        bb.append(price[count - countDX]["low_price"])
	        if countDX >= num:
	            break
	    high = max(aa)
	    low = min(bb)
	    highTmp = max(aa)
	    lowTmp = min(bb)
	    """
	    high = (highTmp+lowTmp)/2 + sp
	    low = (highTmp+lowTmp)/2 - sp
	    """
	    if high - low < sp*2:
	        if flag_balance:
		        high = (highTmp+lowTmp) + sp
		        low = (highTmp+lowTmp) - sp
		        if pos == "SELL":
		        	low = (highTmp+lowTmp)/2 - sp/2
		        if pos == "BUY":
		        	high = (highTmp+lowTmp)/2 + sp/2
	        else:
		        high = (highTmp+lowTmp)/2 + sp
		        low = (highTmp+lowTmp)/2 - sp
	    #"""
	    trend = trendCheck(price, num, count)
	    #print(trend,flush=True)
	    if price[count]["high_price"] > high and pos=="BUY":
	        #print(str(price[count]["close_time_dt"])+ " "+ str(len(x)),flush=True)
	        shisan -= (lastTorihiki - high) * (1+count/len(price))
	        lastTorihiki = high
	        x.append(len(x))
	        y.append(shisan)
	        pos = "SELL"
	        if sp == targetSP:
	        	print("SELL "+str(price[count]["close_time_dt"]+ " " + str(high)),flush=True)
	        	TorihikiTimes += 1
	    elif price[count]["low_price"] < low and pos=="SELL":
	        shisan -= (low - lastTorihiki) * (1+count/len(price))
	        lastTorihiki = low
	        x.append(len(x))
	        y.append(shisan)
	        pos = "BUY"
	        if sp == targetSP:
	        	print("BUY "+str(price[count]["close_time_dt"] + " " + str(low)),flush=True)
	        	TorihikiTimes += 1
	if sp == targetSP:
		pyplot.plot(x, y)
		pyplot.show()
	xx.append(sp)
	yy.append(shisan)
	if sp > 3000:
		break
print(TorihikiTimes,flush=True)
pyplot.plot(xx, yy)
pyplot.show()
