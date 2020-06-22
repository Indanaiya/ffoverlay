import configparser
import os

configAddress = "../config/config.ini"
defaults = {'size':'standard', 'datacenter':'Chaos'}
acceptedValues = {'size': ['standard', 'large']}

def generateConfig():
    parser = configparser.ConfigParser()
    parser['general'] = defaults
    with open(configAddress, 'w') as configfile:
        parser.write(configfile)

def getConfig():
    if not os.path.isfile(configAddress):
        generateConfig()
    parser = configparser.ConfigParser()
    parser.read(configAddress)
    #Checks that all expected options are found in config.ini, rewrites the file if not:
    if not all(x in parser._sections.keys() for x in defaults.keys()):
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
