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

cached_market_data_address = "../res/chachedMarketData.json"
universalis_url = "https://universalis.app/api/"

class NotificationsProvider:
    """A class to provide notifications when a new gathering item becomes available to gather"""
    def __init__(self, gatherable_items_location, datacenter, spawn_callback, despawn_callback):
        if not 'name' in spawn_callback.__code__.co_varnames and not 'price' in spawn_callback.__code__.co_varnames:
            raise ValueError("Expected name and price parameters in spawnCallback.")
        if not 'name' in despawn_callback.__code__.co_varnames:
            raise ValueError("Expected name parameter in despawnCallback.")
        if not inspect.iscoroutinefunction(spawn_callback) or not inspect.iscoroutinefunction(despawn_callback):
            raise ValueError("spawnCallback and despawnCallback must both be coroutines.")
        self.gatherable_items, self.market_data = self.getData(gatherable_items_location, datacenter)
        self.spawn_callback = spawn_callback
        self.despawn_callback = despawn_callback
        self.stop = False
        
    def getData(self, gathered_items_location, datacenter):
        """Get data both from Universalis or cache, and from gathered_items.json"""
        #TODO handling if the JSON is bad including KeyError
        universalis_url_with_datacenter = f"{universalis_url}{datacenter}/"
        universalis_update_frequency = int(getConfig()['general']['universalisupdatefrequency'])

        if os.path.isfile(cached_market_data_address):
            print("file found")
            with open(cached_market_data_address) as file:
                old_market_data = json.load(file)
        else:
            old_market_data = {}

        new_market_data = copy.deepcopy(old_market_data)

        with open(gathered_items_location) as file:
                gatherable_items = json.load(file)
                if datacenter not in new_market_data.keys():
                    new_market_data[datacenter] = {}
                for key in list(gatherable_items.keys()):
                    if (not key in new_market_data[datacenter]) or (datetime.strptime(new_market_data[datacenter][key]['time'], "%Y-%m-%dT%H:%M:%S") < (datetime.now() - timedelta(hours=universalis_update_frequency))): #Key doesn't exist or the data was fetched more than the update frequency hours ago
                        with requests.request("GET", universalis_url_with_datacenter + gatherable_items[key]["id"]) as response:
                            response_json = response.json()
                            print(f"Item Id: {str(response_json['itemID'])}, lowest price: {str(response_json['listings'][0]['pricePerUnit'])}")
                            new_market_data[datacenter][key] = {}
                            new_market_data[datacenter][key]['minPrice'] = response_json['listings'][0]['pricePerUnit']
                            new_market_data[datacenter][key]['time'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                            
        if new_market_data != old_market_data:
            with open(cached_market_data_address, 'w') as file:
                json.dump(new_market_data, file)
        
        return gatherable_items, new_market_data[datacenter]

    async def gatherAlert(self, key, getTime=getEorzeaTimeDecimal):
        """
        Executes the self.spawnCallback coroutine when the node named 'key' spawns
        Executes the self.despawnCallback coroutine when the node named 'key' despawns
        self.spawnCallback should have the arguments name and price
        self.despawnCallback should have the argument name
        """
        gatherable_items = self.gatherable_items
        price = self.market_data[key]['minPrice']
        while True:
            eorzea_hours = getTime()[0]
            current_time_index = 0
            next_time_index = 0
            name = gatherable_items[key]['name']
            spawn_times = gatherable_items[key]['spawnTimes']
            for i in range(len(spawn_times)):
                if eorzea_hours >= int(spawn_times[i][:2]) and eorzea_hours < int(spawn_times[i][:2])+gatherable_items[key]['lifespan']: #Means the node is up
                    current_time_index = i
                    next_time_index = (i+1, 0)[i==len(spawn_times)-1]

                    spawn_time = spawn_times[current_time_index][:2]
                    despawn_time = int(spawn_times[current_time_index][:2]) + self.gatherable_items[key]['lifespan']

                    #Notification for spawn:
                    await self.spawn_callback(name=name, price=price, item_values=gatherable_items[key], spawn_time=spawn_time, despawn_time=despawn_time, market_data = self.market_data[key])

                    #Notification for despawn:
                    sleep_time = timeUntilInEorzea((despawn_time, despawn_time-24)[despawn_time>=24])#Ternary is to loop back around from 24 to 00 (of the next day)
                    await asyncio.sleep(sleep_time)
                    await self.despawn_callback(name=name)

                    break
                elif eorzea_hours < int(spawn_times[i][:2]):
                    next_time_index = i
                    break
                elif i == len(spawn_times) - 1:#eorzeaHours > int(spawnTimes[i][:2]) is implied by reaching this point
                    next_time_index = 0
                    break #Break here is just for clarity. if i==len(spawnTimes)-1 then this would be the last itteration of the for loop regardless

            #Wait for node to spawn again:
            sleep_time = timeUntilInEorzea(int(spawn_times[next_time_index][:2]))
            print(f"Node: {key}, nextTimeIndex: {next_time_index}, sleep for: {sleep_time}")
            await asyncio.sleep(sleep_time)

    def beginGatherAlerts(self):
        """
        Starts gatherAlerts for all gatherable items on a new event loop
        """
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            functions = [self.gatherAlert(key) for key in list(self.gatherable_items.keys())]
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
