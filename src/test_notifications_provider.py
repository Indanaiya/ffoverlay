import unittest
import os
import json
from notifications_provider import NotificationsProvider, cached_market_data_address

datacenter = 'Chaos'
gatherable_items_location = '../res/values.json'

async def SpawnCallback(name=None, price=None):
    print("SpawnCallback")
    
async def DespawnCallback(name=None):
    print("DespawnCallback")

class NotificationsProviderTests(unittest.TestCase):
    def setUp(self):
        """Tests that you can create NotificationsProvider when appropriate arguments are supplied"""
        self.np = NotificationsProvider(gatherable_items_location, datacenter, SpawnCallback, DespawnCallback)

    def test_init_with_bad_arguments(self):
        """Tests that the correct exceptions are raised if innappropriate arguments are supplied"""
        def nonAsyncSpawnCallback(name=None, price=None):
            pass
        def nonAsyncDespawnCallback(name=None):
            pass
        async def noArgumentsCallback():
            pass

        with self.assertRaises(ValueError) as context:
            NotificationsProvider(gatherable_items_location, datacenter, nonAsyncSpawnCallback, DespawnCallback)
        self.assertEqual(str(context.exception), "spawnCallback and despawnCallback must both be coroutines.")

        with self.assertRaises(ValueError) as context:
            NotificationsProvider(gatherable_items_location, datacenter, SpawnCallback, nonAsyncDespawnCallback)
        self.assertEqual(str(context.exception), "spawnCallback and despawnCallback must both be coroutines.")

        with self.assertRaises(ValueError) as context:
            NotificationsProvider(gatherable_items_location, datacenter, noArgumentsCallback, DespawnCallback)
        self.assertEqual(str(context.exception), "Expected name and price parameters in spawnCallback.")
        
        with self.assertRaises(ValueError) as context:
            NotificationsProvider(gatherable_items_location, datacenter, SpawnCallback, noArgumentsCallback)
        self.assertEqual(str(context.exception), "Expected name parameter in despawnCallback.")

    # def test_getData(self):
    #     """Check that getData creates a file called carchedMarketData.json"""
    #     if os.path.isfile(cachedMarketDataAddress):
    #         os.remove(cachedMarketDataAddress)
    #     self.np.getData(gatheredItemsLocation, datacenter)
    #     self.assertEqual(True, os.path.isfile(cachedMarketDataAddress))

    def test_cachedMarketData(self):
        """Tests that init created a file called cachedMarketData.json, if it didn't exist already, and that it contains the appropriate information"""
        with open(cached_market_data_address) as file:
            marketData = json.load(file)
        with open(gatherable_items_location) as file:
            gatheredItemsData = json.load(file)

        #Checks that every gatherable has an entry for the given datacenter
        for key in gatheredItemsData.keys():
            self.assertEqual(True, key in marketData[datacenter].keys())
        #Checks that there are time and minPrice values for every item entry
        for v in marketData[datacenter].values():
            keys = v.keys()
            self.assertEqual(True, 'time' in keys)
            self.assertEqual(True, 'minPrice' in keys)
