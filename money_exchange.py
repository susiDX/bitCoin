import pybitflyer
import math
import requests
import time
from datetime import datetime

code = "BTCJPY15FEB2019"

API_KEY = "9fJUAkKzsB98GcfNSVS6v2"
API_SECRET = "tJTncG/b7EezfXM3nwonKrC76Nt4wZWLP8eH83soNh4="
api1 = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)
API_KEY = "WBFnwpPtQofhxXVmigD1yq" #yassan
API_SECRET = "Ms/9pnvqivvrgwbfLJy5hAs5yut3UVFyV6D0GDVJVaQ="
api2 = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)


public_api = pybitflyer.API()
api = pybitflyer.API(api_key = API_KEY, api_secret = API_SECRET)

def sell_nariyuki(size,api):
    xx = api.sendchildorder(product_code = code,child_order_type = "MARKET", side = "SELL", size = math.floor(100000000*size)/100000000)
    return xx

def buy_nariyuki(size,api):
    xx = api.sendchildorder(product_code = code,child_order_type = "MARKET", side = "BUY", size = math.floor(100000000*size)/100000000)
    return xx

def buy_sashine(size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT",  side = "BUY", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx

def sell_sashine(size, price, api):
    xx = api.sendchildorder(product_code = code,child_order_type = "LIMIT",  side = "SELL", price = math.floor(price), size = math.floor(100000000*size)/100000000)
    return xx

sell_sashine(4, 397000, api1)
buy_nariyuki(4, api2)
buy_sashine(4, 394500, api1)
sell_nariyuki(4, api2)
