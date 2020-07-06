import unittest
import os
from load_configuration import *
import shutil
import copy

def test_generateConfig(self):
    generateConfig()
    parser = configparser.ConfigParser()
    parser.read(configAddress)
    self.assertEqual(dict(parser['general']), defaults)

def test_updateValue(self, key, value):
    updateValue(key, value)
    self.assertEqual(getConfig()['general'][key], value)

class LoadConfigTests(unittest.TestCase):
    def test_generateConfig_fresh_file(self):
        """Testing generateConfig when it does not have to overwrite a file"""
        if os.path.isfile(configAddress):
            os.remove(configAddress)
        test_generateConfig(self)

    def test_generateConfig_no_config_folder(self):
        """Tests that generateConfig works when there is no directory to store the config file in"""
        if os.path.isdir(configAddress + "/.."):
            shutil.rmtree(configAddress + "/..")
        test_generateConfig(self)

    def test_generateConfig_overwrite_file(self):
        """Tests that generateConfig works when there is already a config file"""
        if os.path.isfile(configAddress):
            os.remove(configAddress)
        open(configAddress, "w").close()
        if not os.path.isfile(configAddress):
            raise Exception
        test_generateConfig(self)

    def test_getConfig_when_there_is_a_config_file(self):
        """Tests that getConfig works when its values are the defaults"""
        generateConfig()
        self.assertEqual(getConfig()['general'], defaults)

    def test_getConfig_but_there_is_no_config_file(self):
        """Tests getConfig when there is no config file"""
        if os.path.isfile(configAddress):
            os.remove(configAddress)
        self.assertEqual(getConfig()['general'], defaults)

    def test_getConfig_with_missing_keys_in_config_file(self):
        """Tests that getConfig will rewrite the config file if the config file does not contain all the keys in acceptedValues.keys()"""
        #Write the bad config file
        if not os.path.isdir(configAddress + "/.."):
            os.mkdir(configAddress + "/..")
        parser = configparser.ConfigParser()
        badDefaults = copy.deepcopy(defaults)
        badDefaults.pop('size')
        parser['general'] = badDefaults
        with open(configAddress, 'w') as configfile:
            parser.write(configfile)

        #Read the bad config file
        config = getConfig()['general']
        self.assertEqual(config, defaults)

    def test_getConfig_with_extra_keys_in_config_file(self):
        """Tests that getConfig will rewrite the config file if the config file contains keys that aren't in acceptedValues.keys()"""
        #Write the bad config file
        if not os.path.isdir(configAddress + "/.."):
            os.mkdir(configAddress + "/..")
        parser = configparser.ConfigParser()
        badDefaults = copy.deepcopy(defaults)
        badDefaults['soize'] = 'starndard'
        parser['general'] = badDefaults
        with open(configAddress, 'w') as configfile:
            parser.write(configfile)

        #Read the bad config file
        config = getConfig()['general']
        self.assertEqual(config, defaults)
    
    def test_updateValues(self):
        """Test that updateValue works for every key with a valid value"""
        generateConfig()
        test_updateValue(self, 'size', 'large')
        test_updateValue(self, 'datacenter', 'Light')
        test_updateValue(self, 'universalisupdatefrequency', '5')   
        
    def test_updateValues_with_bad_values(self):
        """Test that updateValue raises ValueError when given bad values for any key"""
        generateConfig()
        with self.assertRaises(ValueError):
            updateValue('size', 'Chaos')
        with self.assertRaises(ValueError):
            updateValue('datacenter', '5')
        with self.assertRaises(ValueError):
            updateValue('universalisupdatefrequency', "standard")

    def test_updateValues_with_bad_key(self):
        """Tests that updateValue raises a KeyError when given a key that isn't in acceptedValues.keys()"""
        generateConfig()
        with self.assertRaises(KeyError):
            updateValue('boogaloo', 'Chaos')