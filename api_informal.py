from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
import requests
import time
from datetime import datetime
import json
import random

product_code = "FX_BTC_JPY"
options = 0
browser = 0
url = 0
cookies = 0
headers = 0

def logIn(flag_kato):
	global options
	global browser
	global url
	global cookies
	global headers
	options = Options()
	options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
	#options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-gpu')
	browser = webdriver.Chrome(options=options, executable_path='C:\\chromedriver_win32\\chromedriver.exe')
	product_code = "FX_BTC_JPY"
	url = "https://lightning.bitflyer.jp/"
	browser.get(url)

	if flag_kato:
	    e = browser.find_element_by_css_selector("#LoginId")
	    e.send_keys("miyrr562244@yahoo.co.jp")
	    e = browser.find_element_by_css_selector("input[type=password]")
	    e.send_keys("Katouyuuya0204")
	else:
	    e = browser.find_element_by_css_selector("#LoginId")
	    e.send_keys("notyet1208messi@yahoo.co.jp")
	    e = browser.find_element_by_css_selector("input[type=password]")
	    e.send_keys("odaeri0425")
	e = browser.find_element_by_css_selector("#login_btn").click()
	cookies = dict(
	_gid = browser.get_cookie("_gid")["value"],
	_gat = browser.get_cookie("_gat")["value"],
	_ga = browser.get_cookie("_ga")["value"],
	api_session_v2 = browser.get_cookie("api_session_v2")["value"],
	NET_SessionId = browser.get_cookie("ASP.NET_SessionId")["value"],
	ai_user = browser.get_cookie("ai_user")["value"],
	__RequestVerificationToken = browser.get_cookie("__RequestVerificationToken")["value"],
	__cfduid = browser.get_cookie("__cfduid")["value"],
	_tdim = browser.get_cookie("_tdim")["value"],
	ai_session = browser.get_cookie("ai_session")["value"]
	)
	headers = {
	"accept":"*/*",
	"accept-encoding":"gzip, deflate, br",
	"accept-language":"ja,en;q=0.9",
	"content-length":"234",
	"content-type":"application/json; charset=utf-8",
	"origin":"https://lightning.bitflyer.jp",
	"referer":"https://lightning.bitflyer.jp/trade/",
	"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
	"x-requested-with":"XMLHttpRequest"
	}


def order_market(side,size) :
	url = "https://lightning.bitflyer.jp/api/trade/sendorder"
	today = datetime.now()
	data = {
	"product_code":product_code,
	"ord_type":"MARKET",
	"price": 0,
	"side" : side,
	"size": math.floor(100000000*size)/100000000,
	"minuteToExpire":43200,
	"time_in_force":"GTC",
	"order_ref_id":"JRF"+today.strftime('%Y%m%d-%H%M%S')+"-"+str(random.randint(100000,999999)),
	"is_check":False,
	"lang":"ja"
	}
	response = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
	res = response.json()
	return res

def order_limit(side, reminingTime, size, price) :
	url = "https://lightning.bitflyer.jp/api/trade/sendorder"
	today = datetime.now()
	id = "JRF"+today.strftime('%Y%m%d-%H%M%S')+"-"+str(random.randint(100000,999999))
	data = {
	"product_code":product_code,
	"ord_type":"LIMIT",
	"price": math.floor(price),
	"side" : side,
	"size": math.floor(100000000*size)/100000000,
	"minuteToExpire": reminingTime,
	"time_in_force":"GTC",
	"order_ref_id":id,
	"is_check":False,
	"lang":"ja"
	}
	response = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
	res = response.json()
	return res

def get_open_collateral() :
	url = "https://lightning.bitflyer.com/api/trade/getmyCollateral"
	data = {
	"lang": "ja",
	"product_code": product_code
	}
	response = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
	res = response.json()
	return int(res["data"]["margin_status"]["Details"]["FX_BTC_JPY"]["OpenPositionPnl"])

def kessai():
    while True:
        order_all_cancel()
        size,side = getPos()
        if size < 0.01:
            break
        elif side == "SELL":
            #print("kessaiSELL",flush=True)
            xx = order_market("BUY", size)
            print(xx,flush=True)
            if xx["status"] == 0:
                break
        elif side == "BUY":
            #print("kessaiBUY",flush=True)
            xx = order_market("SELL", size)
            print(xx,flush=True)
            if xx["status"] == 0:
                break
        time.sleep(2)

def getPos():
	url ="https://lightning.bitflyer.com/api/trade/getmyCollateral"
	data = {
	"product_code": product_code,
	"lang": "ja"
	}
	res = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
	position = res.json()["data"]
    #print(position["margin_status"]["Details"],flush=True)
	pos = position["margin_status"]["Details"]["FX_BTC_JPY"]["PositionAmount"]
	side = "NULL"
	size = 0
	if pos<=0.01:
		side = "SELL"
	elif pos>=0.01:
		side = "BUY"
	else:
		side = "NULL"
	size = math.fabs(pos)
	return size, side

def get_ltp() :
	url = "https://lightning.bitflyer.com/api/trade/ticker/all?v=1"
	response = requests.get(url)
	res = response.json()
	return res[1]["ticker"]["LTP"]

def serverCheck(api):
    ret = api.getboardstate(product_code=product_code)
    while True:
        time.sleep(5)
        state = api.getboardstate(product_code=product_code)
        if state["health"] == "NORMAL":
            break
    return ret["health"]


def order_all_cancel() :
	url = "https://lightning.bitflyer.com/api/trade/cancelallorder"
	data = {
	"product_code":product_code,
	"lang":"ja"
	}
	requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)

def order_cancel(order_id) :
    url = "https://lightning.bitflyer.com/api/trade/cancelorder"
    data = {
    "product_code":product_code,
    "order_id":order_id,
    "lang":"ja"
    }
    response = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
    res = response.json()
    return res

def my_board() :
	url = "https://lightning.bitflyer.com/api/trade/getMyBoardOrders"
	data = {
	"product_code": product_code,
	"lang": "ja"
	}
	res = requests.post(url, data=json.dumps(data),cookies = cookies,headers = headers)
	return res.json()



def serverKessai(api):
    date = datetime.now()
    print(str(date) + "____________________________________________",flush=True)
    kessai()
    serverCheck(api)
    size, side = getPos()
    print(str(size) + "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",flush=True)
