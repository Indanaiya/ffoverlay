import requests
import json
import functools
import asyncio
from eorzea_time import getEorzeaTime

baseurl = "https://universalis.app/api/Chaos/"

loop = asyncio.get_event_loop()

async def gatherAlert(key, valuesData, price):
    """Prints a message when a new gathering node spawns"""
    print(f"New node spawn: {valuesData[key][name]}  {price}gil per unit")

#This will need to be async in the final product:
#aiohttp?
try:
    with open('values.json') as file:
        valuesData = json.load(file)
        for key in list(valuesData.keys()):
            try:
                with requests.request("GET", baseurl + valuesData[key]["id"]) as response:
                    responseJson = response.json()
                    print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
                    loop
            except requests.exceptions.RequestException as err:
                print(f"Unable to get data from Universalis for {key}: {repr(err)}\n")
except Exception as err:
    print(repr(err))




print(getEorzeaTime())
