import requests
import json

baseurl = "https://universalis.app/api/Chaos/"

try:
    with open('values.json') as file:
        valuesData = json.load(file)
        for key in list(valuesData.keys()):
            try:
                with requests.request("GET", baseurl + valuesData[key]["id"]) as response:
                    responseJson = response.json()
                    print("Item Id: " + str(responseJson['itemID']) + ", lowest price: " + str(responseJson['listings'][0]['pricePerUnit']))
            except requests.exceptions.RequestException as err:
                print(f"Unable to get data from Universalis for {key}: {repr(err)}\n")
except Exception as err:
    print(repr(err))
