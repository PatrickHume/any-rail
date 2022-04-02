import geopy.distance
import requests
import re
from bs4 import BeautifulSoup
import sys
import json

if(len(sys.argv) != 6):
    exit()

src = sys.argv[1]
dst = sys.argv[2]
start = sys.argv[3]
end = sys.argv[4]
date = sys.argv[5]

def pennyStringToPounds(pennies):
    p = str(pennies)
    return f'£{p[:-2]}.{p[-2:]}'

def get_ordered_list(srcCoords, dstCodes):
   dstCodes.sort(key = lambda dstCode: geopy.distance.geodesic(srcCoords, coordsDict[dstCode]))
   return dstCodes

allCodes = []
stationDict = {}
codeDict = {}
with open('stations.txt') as f:
    for line in f:
        code = line.strip()[-3:]
        station = line.strip()[:-3].strip()

        allCodes.append(code)
        stationDict.update({code: station})
        codeDict.update({station: code})
f.close()

coordsDict = {}
knownCodes = []
with open('coords.txt') as f:
    for line in f:
        code = line.strip()[:3]

        if(code in stationDict):
            knownCodes.append(code)
            coordsDict.update({code: [float(line.split()[1]),float(line.split()[2])]})
f.close()

knownCodes.remove(src)
nearestCodes = []

if src not in coordsDict:
    exit()

#radiusKm = 30
maxStations = 35

srcCoords = coordsDict[src];
dstCoords = coordsDict[dst];
#for someDst in knownCodes:
#    if someDst not in coordsDict:
#        continue
#    someDstCoords = coordsDict[someDst];
#
#    if geopy.distance.geodesic(dstCoords, someDstCoords).km <= radiusKm:
#        nearestCodes.append(someDst)
#
#orderedCodes = get_ordered_list(dstCoords,nearestCodes)[0:maxStations]
orderedCodes = get_ordered_list(dstCoords,knownCodes)[0:maxStations]
amount = len(orderedCodes)
counter = 0

info = {"src":src, "dst":dst, "start":start, "end":start, "date":date, "status":"incomplete"}
payload = []
JSONdata = {"info":info,"results":payload}

filename = f'{src}-{dst}-{start}-{end}-{date}.txt'
faresFile = open(filename, 'w')
faresFile.write(json.dumps(JSONdata))
faresFile.close()

for count, code in enumerate(orderedCodes):
    lowestIntFare = 999999
    lowestArr = ""
    lowestDep = ""
    found = False

    time        = start
    timeUpdated = time

    progress = f'{count+1}/{amount}'

    dst = code

    print(stationDict[src], "-->", stationDict[dst], progress)

    notes = ""

    for k in range(5):
        link = f'https://ojp.nationalrail.co.uk/service/timesandfares/{src}/{dst}/{date}/{time}/dep'
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        head = soup.find("h2", {"class": "ctf-title"})

        #if len(codes) == 0:
        #    continue
        results = soup.find("div", {"id": "ctf-results"})

        if "no outbound journeys" in str(soup.find('body')):
            notes = "No Journey"
            break

        if results == None:
            break

        tab = results.find("table", {"id": "oft"})

        if tab == None:
            break

        body = tab.find("tbody")

        if body == None:
            break

        locationIsFound = False
        foundLocations = re.findall('\[.*?\]',head.getText())
        for location in foundLocations:
            if location[1:4] == dst:
                locationIsFound = True

        if not locationIsFound:
            break

        for tr in body.select('tr[class*="mtx"]'):
            if "bus service" in str(tr):
                notes = "Bus Only"
                continue

            fares = tr.select('td[class*="fare"]')[0].select('label[for*="fare"]')
            
            if (fares == []):
                continue
            else:
                fare = fares[0].get_text().strip()

            dep = tr.find("div", {"class": "dep"}).get_text().strip()
            arr = tr.find("div", {"class": "arr"}).get_text().strip()

            if int(dep[0:2]+dep[3:5]) > int(end) or int(dep[0:2]+dep[3:5]) < int(start):
                continue;

            if(fare == ''):
                continue;

            intFare = int(fare[1:-3] + fare[-2:])
            if intFare < lowestIntFare:
                lowestIntFare = intFare
                lowestArr = arr
                lowestDep = dep
                found = True

            #print(dep,arr,fare)

            #faresFile.write(f'{dep[0:2]+dep[3:5]} {arr[0:2]+arr[3:5]} {fare[1:-3] + fare[-2:]}\n')

            minutes = int(dep[3:5]) + 10
            hours = int(dep[0:2]) + (minutes//60)
            minutes = minutes%60
            if hours >= 24:
                break

            timeUpdated = str(hours).zfill(2) + str(minutes).zfill(2)

        if not found:
            break

        if int(dep[0:2]+dep[3:5]) > int(end):
            break
        if int(timeUpdated) < int(time):
            break
        
        time = timeUpdated
        if body.find("tr",{"class": "next-day"}) != None:
            break

    '''
    if(found):
        print(f'{lowestDep} {lowestArr} {pennyStringToPounds(lowestIntFare)}')
        faresFile.write(f'{lowestIntFare}\n')
    else:
        print("Not possible")
        faresFile.write("None\n")
    '''
    print(f'{lowestDep} {lowestArr} {pennyStringToPounds(lowestIntFare)}')

    if count+1 >= amount:
        info["status"] = "complete"
    
    payload.append({"src":src, "dst":dst, "dep":lowestDep, "arr":lowestArr, "date":date, "price":lowestIntFare, "notes":notes})
    JSONdata = {"info":info,"results":payload}

    faresFile = open(filename, 'w')
    faresFile.write(json.dumps(JSONdata, indent=4))
    faresFile.close()
    