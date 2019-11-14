import pybitflyer
import csv
import time
import random
import math
from matplotlib import pyplot

n = 10
filename = "8424-8444"

inputfile = filename+".csv"
outputfile = filename+"_"+str(n)+"sec.csv"

excution = []
f = open(inputfile, "r")
reader = csv.DictReader(f)
for i in reader:
    excution.append(i)
f.close()
excution.reverse()

updateDate = int(excution[0]["date"]) + n

values = []
high = 0
low = 10000000
volume = 0
openPrice = int(float(excution[0]["price"]))
date = int(float(excution[0]["date"]))
closePrice = int(float(excution[0]["price"]))
for ex in excution:
    high = max(high, int(float(ex["price"])))
    low = min(low, int(float(ex["price"])))
    volume += float(ex["size"])
    closePrice = int(float(ex["price"]))
    if int(ex["date"]) > updateDate:
        updateDate += n
        values.append({"o":openPrice, "h":high, "l":low, "c":closePrice, "date": date, "v":volume})
        high = 0
        low = 10000000
        volume = 0
        high = max(high, int(float(ex["price"])))
        low = min(low, int(float(ex["price"])))
        openPrice = int(float(ex["price"]))
        date = int(float(ex["date"]))

f = open(outputfile, "w")
fieldnames = ["o","h","l","c","date","v"]
writer = csv.DictWriter(f,fieldnames = fieldnames)
writer.writeheader()
writer.writerows(values)
f.close()
