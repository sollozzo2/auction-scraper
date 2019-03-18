import sys
import pycurl
import io
import certifi
import time
import datetime

prev = [0]
state = -1


#this iterates through the search results page 
#and saves the urls of each product into a file
def geturls():
    stub = 'first half of url'
    cap = 'second half of url'
    itemstub = 'url stub'
    itemurl = ''
    #page number of results page
    urlindex = 0 
    #there are 68 result pages in total, with 100 products per page
    for i in range(68):
        url = stub + str(i+1) + cap
        e = io.BytesIO()
        curlObj = pycurl.Curl()
        curlObj.setopt(pycurl.CAINFO, certifi.where())
        try :
            print("trying to curl")
            curlObj.setopt(curlObj.URL, url)
        except pycurl.error:
            print("error curling")
            return ['-2','-1','-1','-1','-1']
        curlObj.setopt(curlObj.WRITEFUNCTION, e.write)
        curlObj.perform()
        curlObj.close()
        http = decode(e.getvalue())
        #get all urls in search page
        while urlindex != -1:
            urlindex = http.find('html string ', urlindex)
            if urlindex == -1:
                break
            urlindex += len('html string')
            while http[urlindex] != '"':
                itemurl += http[urlindex]
                urlindex += 1
            g = open('urls.txt', 'a')
            g.write(itemstub + itemurl)
            print("writing url: ", itemstub + itemurl)
            g.write('\n')
            g.close()
            itemurl = ''
        urlindex = 0
        time.sleep(5)

#this visits the urls gathered from the previous function
#and parses the html file to retrieve the wholesale price,
#retail price and item name for each item
def getprices():
    wholesaleprice = ''
    msrp = ''
    metadata = ''
    with open("urls.txt", "r") as f:
        for url in f:
            #get rid of illegal character \r in url
            url = url[:-1]
            e = io.BytesIO()
            curlObj = pycurl.Curl()
            curlObj.setopt(pycurl.CAINFO, certifi.where())
            try :
                print("trying to curl")
                curlObj.setopt(curlObj.URL, url)
            except pycurl.error:
                print("error curling")
                return 2
            curlObj.setopt(curlObj.WRITEFUNCTION, e.write)
            curlObj.perform()
            curlObj.close()
            http = decode(e.getvalue())

            wholeind = http.find('"$" content="')
            if wholeind == -1:
                break
            wholeind += len('"$" content="')
            while http[wholeind] != '"':
                wholesaleprice += http[wholeind]
                wholeind += 1

            msrpind = http.find("data_msrp='")
            if msrpind == -1:
                print("can't find msrp")
                break
            msrpind += len("data_msrp='")
            while http[msrpind] != "'":
                msrp += http[msrpind]
                msrpind += 1
                
            metadataind = http.find('html string ')
            if metadataind == -1:
                print("can't find meta")
                break
            metadataind += len('html string ')
            while http[metadataind] != '"':
                metadata += http[metadataind]
                metadataind += 1
            
            g = open('data.txt', 'a')
            #strip false delimiters
            g.write(wholesaleprice + '|' + msrp + '|' + metadata.replace('|', '') + '\n')
            print("writing data: ", wholesaleprice, msrp, metadata)
            g.close()
            #reinitialize variables after each loop
            wholesaleprice = ''
            msrp = ''
            metadata = ''
            #remove the following line if you think the network admins & legal team are incompetent
            #time.sleep(15)


#helper function for pycurl, taken from stackoverflow
def decode(s, encoding="ascii", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)