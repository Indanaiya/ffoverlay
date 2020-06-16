import requests
import json

baseurl = "https://universalis.app/api/Chaos/"

#Should change this to a try catch to display custom messages if something goes wrong
with open('values.json') as file:
    valuesData = json.load(file)
    for key in list(valuesData.keys()):
        with requests.request("GET", "https://universalis.app/api/Chaos/" + valuesData[key]["id"]) as response:
            responseJson = response.json()
            print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
