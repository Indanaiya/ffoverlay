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


    def __init__(self, gatheredItemsLocation, marketDataAddress, spawnCallback, despawnCallback):
        if not 'name' in spawnCallback.__code__.co_varnames and not 'price' in spawnCallback.__code__.co_varnames:
            raise ValueError("Expected name and price parameters in spawnCallback")
        if not 'name' in despawnCallback.__code__.co_varnames:
            raise ValueError("Expected name parameter in despawnCallback")

        self.gatheredItemsData, self.marketData = self.getData(gatheredItemsLocation, marketDataAddress)
        self.spawnCallback = spawnCallback
        self.despawnCallback = despawnCallback

    async def gatherAlert(self, key):
        """
        Executes the self.spawnCallback function when the node named 'key' spawns
        Executes the self.despawnCallback function when the node named 'key' despawns
        self.spawnCallback should have the arguments name and price
        self.despawnCallback should have the argument name
        """
        valuesData = self.gatheredItemsData
        price = self.marketData[key]['listings'][0]['pricePerUnit']
        while True:
            eorzeaHours, eorzeaMinutes = getEorzeaTimeDecimal()
            currentTimeIndex = 0
            nextTimeIndex = 0
            name = valuesData[key]['name']
            spawnTimes = valuesData[key]['spawnTimes']
            for i in range(len(spawnTimes)):
                #print(f"Node: {key}, i: {i}")
                if eorzeaHours >= int(spawnTimes[i][:2]) and eorzeaHours < int(spawnTimes[i][:2])+valuesData[key]['lifespan']: #Means the node is up
                    #print(f"New node spawn[{eorzeaHours}]: {valuesData[key]['name']}  {price}gil per unit")
                    currentTimeIndex = i
                    nextTimeIndex = (i+1, 0)[i==len(spawnTimes)-1]

                    #Notification for spawn:
                    self.spawnCallback(name=name, price=price)

                    #Notification for despawn:
                    sleepTime = timeUntilInEorzea(int(spawnTimes[currentTimeIndex][:2]) + self.gatheredItemsData[key]['lifespan'])
                    await asyncio.sleep(sleepTime)
                    self.despawnCallback(name=name)

                    break
                elif eorzeaHours > int(spawnTimes[i][:2]):
                    if i == len(spawnTimes)-1:
                        nextTimeIndex = 0
                else:
                    nextTimeIndex = i
                    break

            #Wait for node to spawn again:
            print(f"Node: {key}, nextTimeIndex: {nextTimeIndex}")
            sleepTime = timeUntilInEorzea(int(spawnTimes[nextTimeIndex][:2]))
            await asyncio.sleep(sleepTime)

    def beginGatherAlerts(self):
        """
        Starts gatherAlerts for all gatherable items on a new event loop
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            functions = [self.gatherAlert(key) for key in list(self.gatheredItemsData.keys())]
            loop.run_until_complete(asyncio.gather(*functions))
        finally:
            loop.close()

def printSpawnMessage(name=None, price=None):
    print(f"New node spawn[{getEorzeaTime()}]: {name}  {price}gil per unit")

def printDespawnMessage(name=None):
    print(f"Node despawn[{getEorzeaTime()}]: {name}")

if __name__ == "__main__":
    notificationsProvider = NotificationsProvider('../res/values.json', "https://universalis.app/api/Chaos/", printSpawnMessage, printDespawnMessage)
    x=threading.Thread(target=notificationsProvider.beginGatherAlerts)
    x.start()
    #notificationsProvider.beginGatherAlerts()
