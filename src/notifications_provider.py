import requests
import json
import asyncio
import threading
import time
from eorzea_time import getEorzeaTime, timeUntilInEorzea, getEorzeaTimeDecimal

class NotificationsProvider:
    """
    A class to provide notifications when a new gathering item becomes available to gather
    """

    def getData(self, gatheredItemsLocation, marketDataAddress):
        """
        Gets data both from Universalis, and from gathered_items.json
        """
        with open(gatheredItemsLocation) as file:
            gatheredItemsData = json.load(file)
            marketData = {}
            for key in list(gatheredItemsData.keys()):
                try:
                    with requests.request("GET", marketDataAddress + gatheredItemsData[key]["id"]) as response:
                        responseJson = response.json()
                        print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
                        marketData[key]=responseJson
                except requests.exceptions.RequestException as err:
                    print(f"Unable to get data from Universalis for {key}: {repr(err)}\n")
            return gatheredItemsData, marketData


    def __init__(self, gatheredItemsLocation, marketDataAddress):
        self.gatheredItemsData, self.marketData = self.getData(gatheredItemsLocation, marketDataAddress)

    async def gatherAlert(self, key):
        """Prints a message when a new gathering node spawns"""
        valuesData = self.gatheredItemsData
        price = self.marketData[key]['listings'][0]['pricePerUnit']
        while True:
            eorzeaHours, eorzeaMinutes = getEorzeaTimeDecimal()
            nextTimeIndex = 0
            spawnTimes = valuesData[key]['spawnTimes']
            for i in range(len(spawnTimes)):
                #print(f"Node: {key}, i: {i}")
                if eorzeaHours >= int(spawnTimes[i][:2]) and eorzeaHours < int(spawnTimes[i][:2])+valuesData[key]['lifespan']:
                    print(f"New node spawn[{eorzeaHours}]: {valuesData[key]['name']}  {price}gil per unit")
                    nextTimeIndex = (i+1, 0)[i==len(spawnTimes)-1]
                    break
                elif eorzeaHours > int(spawnTimes[i][:2]):
                    if i == len(spawnTimes)-1:
                        nextTimeIndex = 0
                else:
                    nextTimeIndex = i
                    break

            print(f"Node: {key}, nextTimeIndex: {nextTimeIndex}")
            sleepTime = timeUntilInEorzea(int(spawnTimes[nextTimeIndex][:2]))
            # print(f"Sleeping for: {sleepTime}")
            await asyncio.sleep(sleepTime)

    def beginGatherAlerts(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            functions = []
            for key in list(self.gatheredItemsData.keys()):
                functions.append(self.gatherAlert(key))
            loop.run_until_complete(asyncio.gather(*functions))
            # loop.run_until_complete(asyncio.gather(
            #     self.gatherAlert('Imperial Fern'),
            #     self.gatherAlert('Fireheart Cobalt'),
            #     self.gatherAlert('Duskblooms'),
            #     self.gatherAlert('Purpure Shell Chips'),
            #     self.gatherAlert('Merbau Log'),
            #     self.gatherAlert('Ashen Alumen'),
            #     ))

        finally:
            loop.close()

if __name__ == "__main__":
    notificationsProvider = NotificationsProvider('../res/values.json', "https://universalis.app/api/Chaos/")
    x=threading.Thread(target=notificationsProvider.beginGatherAlerts)
    x.start()
    #notificationsProvider.beginGatherAlerts()
