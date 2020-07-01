import requests
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
import inspect
import os
import copy
from eorzea_time import getEorzeaTime, timeUntilInEorzea, getEorzeaTimeDecimal
from load_configuration import getConfig

cachedMarketDataAddress = "../res/chachedMarketData.json"
universalisUrl = "https://universalis.app/api/"

class NotificationsProvider:
    """
    A class to provide notifications when a new gathering item becomes available to gather
    """
    def __init__(self, gatheredItemsLocation, datacenter, spawnCallback, despawnCallback):
        if not 'name' in spawnCallback.__code__.co_varnames and not 'price' in spawnCallback.__code__.co_varnames:
            raise ValueError("Expected name and price parameters in spawnCallback.")
        if not 'name' in despawnCallback.__code__.co_varnames:
            raise ValueError("Expected name parameter in despawnCallback.")
        if not inspect.iscoroutinefunction(spawnCallback) or not inspect.iscoroutinefunction(despawnCallback):
            raise ValueError("spawnCallback and despawnCallback must both be coroutines.")
        self.gatheredItemsData, self.marketData = self.getData(gatheredItemsLocation, datacenter)
        self.spawnCallback = spawnCallback
        self.despawnCallback = despawnCallback
        self.stop = False
        


    def getData(self, gatheredItemsLocation, datacenter):
        """
        Gets data both from Universalis or cache, and from gathered_items.json
        """
        #TODO handling if the JSON is bad including KeyError
        marketDataAddress = f"{universalisUrl}{datacenter}/"
        universalisUpdateFrequency = int(getConfig()['general']['universalisupdatefrequency'])


        if os.path.isfile(cachedMarketDataAddress):
            print("file found")
            with open(cachedMarketDataAddress) as file:
                oldMarketData = json.load(file)
        else:
            oldMarketData = {}

        newMarketData = copy.deepcopy(oldMarketData)

        with open(gatheredItemsLocation) as file:
                gatheredItemsData = json.load(file)
                if datacenter not in newMarketData.keys():
                    newMarketData[datacenter] = {}
                for key in list(gatheredItemsData.keys()):#TODO make the time between updates user changeable
                    if (not key in newMarketData[datacenter]) or (datetime.strptime(newMarketData[datacenter][key]['time'], "%Y-%m-%dT%H:%M:%S") < (datetime.now() - timedelta(hours=universalisUpdateFrequency))): #Key doesn't exist or the data was fetched more than the update frequency hours ago
                        with requests.request("GET", marketDataAddress + gatheredItemsData[key]["id"]) as response:
                            responseJson = response.json()
                            print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
                            newMarketData[datacenter][key] = {}
                            newMarketData[datacenter][key]['minPrice'] = responseJson['listings'][0]['pricePerUnit']
                            newMarketData[datacenter][key]['time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                            

        if newMarketData != oldMarketData:
            with open(cachedMarketDataAddress, 'w') as file:
                json.dump(newMarketData, file)
        else:
            print("Equal")
        
        return gatheredItemsData, newMarketData[datacenter]


    async def gatherAlert(self, key, getTime=getEorzeaTimeDecimal):
        """
        Executes the self.spawnCallback coroutine when the node named 'key' spawns
        Executes the self.despawnCallback coroutine when the node named 'key' despawns
        self.spawnCallback should have the arguments name and price
        self.despawnCallback should have the argument name
        """
        valuesData = self.gatheredItemsData
        price = self.marketData[key]['minPrice']
        while True:
            eorzeaHours = getTime()[0]
            currentTimeIndex = 0
            nextTimeIndex = 0
            name = valuesData[key]['name']
            spawnTimes = valuesData[key]['spawnTimes']
            for i in range(len(spawnTimes)):
                if eorzeaHours >= int(spawnTimes[i][:2]) and eorzeaHours < int(spawnTimes[i][:2])+valuesData[key]['lifespan']: #Means the node is up
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
                elif eorzeaHours < int(spawnTimes[i][:2]):
                    nextTimeIndex = i
                    break
                elif i == len(spawnTimes) - 1:#eorzeaHours > int(spawnTimes[i][:2]) is implied by reaching this point
                    nextTimeIndex = 0
                    break #Break here is just for clarity. if i==len(spawnTimes)-1 then this would be the last itteration of the for loop regardless

            #Wait for node to spawn again:
            sleepTime = timeUntilInEorzea(int(spawnTimes[nextTimeIndex][:2]))
            print(f"Node: {key}, nextTimeIndex: {nextTimeIndex}, sleep for: {sleepTime}")
            await asyncio.sleep(sleepTime)

    def beginGatherAlerts(self):
        """
        Starts gatherAlerts for all gatherable items on a new event loop
        """
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            functions = [self.gatherAlert(key) for key in list(self.gatheredItemsData.keys())]
            functions.append(self.checkToStop())
            print(functions)
            self.loop.run_until_complete(asyncio.gather(*functions))
        finally:
            self.loop.close()

    async def checkToStop(self):
        """Stops the asyncio loop for gather alerts if the stop flag has been set (by stopGatherAlerts)"""
        while not self.stop:
            await asyncio.sleep(1)
        self.loop.stop()

    def stopGatherAlerts(self):
        """Tells the object to stop the asyncio loop for gather alerts"""
        self.stop = True

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
