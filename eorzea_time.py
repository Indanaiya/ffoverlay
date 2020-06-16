import datetime
import time

eorzeaEpochMultiplier = 20571.428571428573

def getEorzeaTimeDecimal():
        """
        Created using code provided by /u/Clorifex https://www.reddit.com/r/ffxiv/comments/2pbl8p/eorzea_time_formula/cmvijkz?utm_source=share&utm_medium=web2x
        Returns a tuple of the type (float, float), representing hours and minutes in eorzean time (On EU servers anyway)
        """
        localEpoch = time.time()
        eorzeaEpoch = localEpoch * eorzeaEpochMultiplier
        eorzeaMinutes = (eorzeaEpoch / (1000 * 60)) % 60
        eorzeaHours = (eorzeaEpoch / (1000 * 60 * 60)) % 24
        return (eorzeaHours, eorzeaMinutes)

def getEorzeaTime():
    """
    Returns a tuple of the type (int, int), representing hours and minutes in eorzean time (On EU servers anyway)
    """
    eorzeaHoursDecimal, eorzeaMinutesDecimal = getEorzeaTimeDecimal()
    return (int(eorzeaHoursDecimal), int(eorzeaMinutesDecimal))

def timeUntilInEorzea(targetTime):
    """
    Target time is in hours
    """
    #Need error checking to make sure that eorzeaHours is a number between 0 and 24 (not including 24)
    localEpoch = time.time()
    eorzeaHours, eorzeaMinutes = getEorzeaTimeDecimal()
    n = 1
    return (((24*n+eorzeaHours)*1000*60*60)/eorzeaEpochMultiplier)

if __name__ == "__main__":
    print(getEorzeaTimeDecimal())
    print(getEorzeaTime())
    print(timeUntilInEorzea(14))
