import requests
import json
import asyncio
from eorzea_time import getEorzeaTime, timeUntilInEorzea

baseurl = "https://universalis.app/api/Chaos/"
valuesJsonFileLocation = '../res/values.json'

async def gatherAlert(key, valuesData, price):
    """Prints a message when a new gathering node spawns"""
    eorzeaHours, eorzeaMinutes = getEorzeaTime()
    nextTimeIndex = 0
    spawnTimes = valuesData[key]['spawnTimes']
    for i in range(len(spawnTimes)):
        if eorzeaHours == int(spawnTimes[i][:2]):
            if not (i == len(spawnTimes)-1):
                nextTimeIndex = i+1
            print(f"New node spawn: {valuesData[key]['name']}  {price}gil per unit")
            await loop.call_later(timeUntilInEorzea(int(spawnTimes[nextTimeIndex][:2])), gatherAlert(key, valuesData, price))

#This will need to be async in the final product:
#aiohttp?
def main():
    with open(valuesJsonFileLocation) as file:
        valuesData = json.load(file)
        jsonData = {}
        for key in list(valuesData.keys()):
            try:
                with requests.request("GET", baseurl + valuesData[key]["id"]) as response:
                    responseJson = response.json()
                    print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
                    jsonData[key]=responseJson
            except requests.exceptions.RequestException as err:
                print(f"Unable to get data from Universalis for {key}: {repr(err)}\n")
        return valuesData, jsonData



if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        valuesData, jsonData = main()
        loop.run_until_complete(gatherAlert('Imperial Fern', valuesData, jsonData['Fireheart Cobalt']['listings'][0]['pricePerUnit']))
    finally:
        loop.close()
