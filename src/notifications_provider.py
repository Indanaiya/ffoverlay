import requests
import json
import asyncio
import threading
import time
import inspect
from eorzea_time import getEorzeaTime, timeUntilInEorzea, getEorzeaTimeDecimal

class NotificationsProvider:
    """
    A class to provide notifications when a new gathering item becomes available to gather
    """
    def __init__(self, gatheredItemsLocation, marketDataAddress, spawnCallback, despawnCallback):
        if not 'name' in spawnCallback.__code__.co_varnames and not 'price' in spawnCallback.__code__.co_varnames:
            raise ValueError("Expected name and price parameters in spawnCallback.")
        if not 'name' in despawnCallback.__code__.co_varnames:
            raise ValueError("Expected name parameter in despawnCallback.")
        if not inspect.iscoroutinefunction(spawnCallback) or not inspect.iscoroutinefunction(despawnCallback):
            raise ValueError("spawnCallback and despawnCallback must both be coroutines.")
        self.gatheredItemsData, self.marketData = self.getData(gatheredItemsLocation, marketDataAddress)
        self.spawnCallback = spawnCallback
        self.despawnCallback = despawnCallback


    def getData(self, gatheredItemsLocation, marketDataAddress):
        """
        Gets data both from Universalis, and from gathered_items.json
        """
        with open(gatheredItemsLocation) as file:#Rahter than do this all at the start. I should get the data when needed, and then cache it
            gatheredItemsData = json.load(file)
            marketData = {}
            for key in list(gatheredItemsData.keys()):
                try:
                    with requests.request("GET", marketDataAddress + gatheredItemsData[key]["id"]) as response:
                        responseJson = response.json()
                        print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
                        marketData[key] = responseJson
                except requests.exceptions.RequestException as err:
                    print(f"Unable to get data from Universalis for {key}: {repr(err)}\n")
            return gatheredItemsData, marketData


    async def gatherAlert(self, key, getTime=getEorzeaTimeDecimal):
        """
        Executes the self.spawnCallback coroutine when the node named 'key' spawns
        Executes the self.despawnCallback coroutine when the node named 'key' despawns
        self.spawnCallback should have the arguments name and price
        self.despawnCallback should have the argument name
        """
        valuesData = self.gatheredItemsData
        price = self.marketData[key]['listings'][0]['pricePerUnit']
        while True:
            eorzeaHours, eorzeaMinutes = getTime()
            currentTimeIndex = 0
            nextTimeIndex = 0
            name = valuesData[key]['name']
            spawnTimes = valuesData[key]['spawnTimes']
            for i in range(len(spawnTimes)):
                if eorzeaHours >= int(spawnTimes[i][:2]) and eorzeaHours < int(spawnTimes[i][:2])+valuesData[key]['lifespan']: #Means the node is up
                    #print(f"Function says New node spawn[{eorzeaHours}]: {valuesData[key]['name']}  {price}gil per unit")
                    currentTimeIndex = i
                    nextTimeIndex = (i+1, 0)[i==len(spawnTimes)-1]

                    spawnTime = spawnTimes[currentTimeIndex][:2]
                    despawnTime = int(spawnTimes[currentTimeIndex][:2]) + self.gatheredItemsData[key]['lifespan']

                    #Notification for spawn:
                    await self.spawnCallback(name=name, price=price, itemValues=valuesData[key], spawnTime=spawnTime, despawnTime=despawnTime, marketData = self.marketData[key])

                    #Notification for despawn:
                    sleepTime = timeUntilInEorzea((despawnTime, despawnTime-24)[despawnTime>=24])#Ternary is to loop back around from 24 to 00 (of the next day)
                    await asyncio.sleep(sleepTime)
                    await self.despawnCallback(name=name)

                    break
                elif i == len(spawnTimes) - 1:#eorzeaHours > int(spawnTimes[i][:2]) is implied by reaching this point
                    nextTimeIndex = 0
                    break #Break here is just for clarity. if i==len(spawnTimes)-1 then this would be the last itteration of the for loop regardless
                elif eorzeaHours < int(spawnTimes[i][:2]):
                    nextTimeIndex = i

            #Wait for node to spawn again:
            sleepTime = timeUntilInEorzea(int(spawnTimes[nextTimeIndex][:2]))
            print(f"Node: {key}, nextTimeIndex: {nextTimeIndex}, sleep for: {sleepTime}")
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



if __name__ == "__main__":
    """
    Provides notifications in a console app
    """
    async def printSpawnMessage(name=None, price=None):
        print(f"New node spawn[{getEorzeaTime()}]: {name}  {price}gil per unit")

    async def printDespawnMessage(name=None):
        print(f"Node despawn[{getEorzeaTime()}]: {name}")

    notificationsProvider = NotificationsProvider('../res/values.json', "https://universalis.app/api/Chaos/", printSpawnMessage, printDespawnMessage)
    notificationsProviderThread = threading.Thread(target = notificationsProvider.beginGatherAlerts)
    notificationsProviderThread.start()
