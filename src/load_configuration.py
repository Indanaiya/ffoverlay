import configparser
import os

config_address = "../config/config.ini"
defaults = {'size':'standard', 'datacenter':'Chaos', 'universalisupdatefrequency': '6'}
accepted_values = {'size': ['standard', 'large'], 'datacenter':['Chaos','Light','Aether','Primal','Crystal','Elemental','Gaia','Mana'], 'universalisupdatefrequency': [str(i) for i in range(1,100)]}

def generateConfig():
    """Create a new configuration file with default values."""
    if not os.path.isdir(config_address + "/.."):
        os.mkdir(config_address + "/..")
    parser = configparser.ConfigParser()
    parser['general'] = defaults
    with open(config_address, 'w') as configfile:
        parser.write(configfile)

def getConfig():
    """Get the config file values, create a config file if one does not already exist."""
    if not os.path.isfile(config_address):
        print("Config file not found. Writing.")
        generateConfig()
    parser = configparser.ConfigParser()
    parser.read(config_address)
    #Getting all the keys in the ini
    parsed_keys = []
    
    for x,y in parser.items('general'):
        parsed_keys.append(x)

    #Checks that all expected options are found in config.ini, rewrites the file if not:
    if not parsed_keys == list(defaults.keys()):
        print("Not all expected keys found. Rewriting config.")
        generateConfig()
        parser = configparser.ConfigParser()
        parser.read(config_address)

    return parser._sections

def updateValue(key, value):
    """Change a value in the config file."""
    if not key in accepted_values.keys():
        raise KeyError(f"Invalid Key. {key} is not recognised.")
    if not value in accepted_values[key]:
        raise ValueError(f"{key} cannot take value {value}. Accepted values are: {accepted_values[key]}")
    #Get the config file:
    parser = configparser.ConfigParser()
    parser.read(config_address)
    #Update the value in python:
    parser['general'][key] = value
    #Rewrite the file with the updated value:
    with open(config_address, 'w') as configfile:
        parser.write(configfile)

if __name__ == "__main__":
    generateConfig()
    print(getConfig()['general'])
