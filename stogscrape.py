import sys
import pycurl
import io
import certifi
import time
import datetime

prev = [0]
state = -1
#-1 = initial
#0 = normal operation
#1 = no auctions available
# when switching between 0 and 1, write timestamp 
#to record beginning and end times

def getData():
    e = io.BytesIO()
    t = ContentCallback()
    curlObj = pycurl.Curl()
    curlObj.setopt(pycurl.CAINFO, certifi.where())
    try :
        print("trying to curl")
        curlObj.setopt(curlObj.URL, 'url string 1')
    except pycurl.error:
        print("error curling")
        return ['-2','-1','-1','-1','-1']
    curlObj.setopt(curlObj.WRITEFUNCTION, e.write)
    curlObj.perform()
    curlObj.close()
    http = decode(e.getvalue())

    name = ''
    lowest = ''
    initial = ''
    quantity = ''
    #actual strings redacted to prevent potential legal trouble
    result = http.find('html string 1')
    if result == -1:
	    name = '-1'
	    return ['-1','-1','-1','-1','-1']
    result += len('html string 2')
    while http[result] != '<':
        name += http[result]
        result += 1

    result = http.find("html string 3")
    if result == -1:
	    name = '-1'
	    return ['-1','-1','-1','-1','-1']
    result += len("html string 4")
    while http[result] != "'":
        lowest += http[result]
        result += 1

    result = http.find("html string 5")
    if result == -1:
	    name = '-1'
	    return ['-1','-1','-1','-1','-1']
    result += len("html string 5.5")
    while http[result] != "'":
        initial += http[result]
        result += 1
        
    result = http.find('html string 6')
    if result == -1:
	    name = '-1'
	    return ['-1','-1','-1','-1','-1']
    result += len('html string 7')
    while http[result] != "<":
        quantity += http[result]
        result += 1
		
	
    

    print(name, lowest, initial, quantity)
    return [name, lowest, initial, datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), quantity]

#helper function for turning curl bytes into string
#taken from Sven Marnach's stackoverflow answer
def decode(s, encoding="ascii", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)

def writeData():
        prev = [0]
        #state is used to signify beginning/end of auctions
        state = -1
        while True:
                data = getData()
                #avoid repeats
                if prev[0] == data[0]:
                        time.sleep(30)
                        continue
                #no auctions available at the moment
                if data[0] == '-1':
                        if state == 0:
                                g = open('auctiondata.csv', 'a')
                                g.write('Auctions End||||')
                                g.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
                                g.write('\n')
                                g.close()
                        state = 1
                        time.sleep(300)
                        continue
                #error curling
                if data[0] == '-2':
                        print("pycurl caught, sleeping")
                        time.sleep(5)
                        continue
                #auctions available
                g = open('auctiondata.csv', 'a')
                if state == 1:
                        g.write('Auctions Begin||||')
                        g.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
                        g.write('\n')
                state = 0
                #using vertical bar as delimiter to later parse into SQL db or excel
                g.write(data[0] + '|')
                g.write(data[1] + '|' + data[2])
                g.write('|' + data[3] + '|')
                g.write(data[4] + '\n')
                time.sleep(30)
                prev = data
                g.close()