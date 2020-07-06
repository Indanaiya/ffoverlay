import configparser
import os

configAddress = "../config/config.ini"
defaults = {'size':'standard', 'datacenter':'Chaos', 'universalisupdatefrequency': '6'}
acceptedValues = {'size': ['standard', 'large'], 'datacenter':['Chaos','Light','Aether','Primal','Crystal','Elemental','Gaia','Mana'], 'universalisupdatefrequency': [str(i) for i in range(1,100)]}

def generateConfig():
    if not os.path.isdir(configAddress + "/.."):
        os.mkdir(configAddress + "/..")
    parser = configparser.ConfigParser()
    parser['general'] = defaults
    with open(configAddress, 'w') as configfile:
        parser.write(configfile)

def getConfig():
    if not os.path.isfile(configAddress):
        print("Config file not found. Writing.")
        generateConfig()
    parser = configparser.ConfigParser()
    parser.read(configAddress)
    #Getting all the keys in the ini
    parsedKeys = []
    
    for x,y in parser.items('general'):
        parsedKeys.append(x)

    #Checks that all expected options are found in config.ini, rewrites the file if not:
    if not parsedKeys == list(defaults.keys()):
        print("Not all expected keys found. Rewriting config.")
        generateConfig()
        parser = configparser.ConfigParser()
        parser.read(configAddress)

    return parser._sections

def updateValue(key, value):
    if not key in acceptedValues.keys():
        raise KeyError(f"Invalid Key. {key} is not recognised.")
    if not value in acceptedValues[key]:
        raise ValueError(f"{key} cannot take value {value}. Accepted values are: {acceptedValues[key]}")
    #Get the config file:
    parser = configparser.ConfigParser()
    parser.read(configAddress)
    #Update the value in python:
    parser['general'][key] = value
    #Rewrite the file with the updated value:
    with open(configAddress, 'w') as configfile:
        parser.write(configfile)

if __name__ == "__main__":
    generateConfig()
    print(getConfig()['general'])
