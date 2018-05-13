import time
import pymysql.cursors
import requests
import ast
import unicodedata
from bs4 import BeautifulSoup
import urllib
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys
import re

#NOTE: Data saved in following form to .CSV file:
#State County CountyId TrumpVotes

newfile = open("data.csv", "w")

def addtofile(x):
    f.write(str(x))

#Normalizes unicode data and incodes it to ascii.
def cleanUp(x):
    if isinstance(x, str):
        x = re.sub(r'\W+', '', x)
        return str(x)
    elif isinstance(x, unicode):
        x = unicodedata.normalize('NFKD', x).encode('ascii','ignore')
        x = re.sub(r'\W+', '', x)
        return x

#Returns percentage of county that voted Trump in 2016.
def getPercentage(soup, countyname):
    div = soup.find('article', {'id': countyname})
    data1 = div.find("tr", {"class": "type-republican"})
    data2 = data1.find("span", {"class": "number"})
    percentage = data2.get_text().replace("%", "")
    return str(percentage)

def ScrapeInfo():
    # This uses DataUSA api to gather names and special ids for states.
    stateslink = "https://api.datausa.io/attrs/geo/?sumlevel=state"
    stateinfo = requests.get(stateslink).json()
    for row in stateinfo["data"]:
        urlname = row[0]
        statename = row[2]
        geo_id = row[8]
        parseBasicCountyInfo(urlname, statename, geo_id)
    print "All done!"
    input("Press enter to close:")
    newfile.close()

def parseBasicCountyInfo(stateurlname, statename, stateid):
    # This uses DataUSA api to gather names and special ids for states.
    countylink = "https://api.datausa.io/attrs/geo/" + stateid + "/children/"
    countyinfo = requests.get(countylink).json()
    countynumber = int(len(countyinfo["data"]))
    driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
    driver.get('https://www.politico.com/2016-election/results/map/president/' + str(stateurlname) + '/')
    var = 0
    x = 0
    while var < countynumber:
        x = x + 450
        driver.execute_script("window.scrollTo(0, " + str(x) + ")")
        time.sleep(1)
        var += 1

    r = driver.page_source  
    driver.quit()
    soup = BeautifulSoup(r, 'html.parser')
    geo_id = stateid
    for newrow in countyinfo["data"]:
        countyid = newrow[0]
        countyname = newrow[1]
        countyname = countyname.split(",")[0]
        countyname = countyname.replace("County", "").replace(" ", "")
        countyname = cleanUp(countyname)
        fakecname = "county" + countyname
        print countyname + " County"
        try:
            time.sleep(2)
            trumppercentage = getPercentage(soup, fakecname)
            addtofile("statename, " + statename)
            addtofile("countyname, " + countyname)
            addtofile("countyid, " + countyid)
            addtofile("trumppercentage, " + trumppercentage)
        except AttributeError:
            print "Skipped over " + county + ", " + statename + "."
        finally:
            print "done!"
ScrapeInfo()
