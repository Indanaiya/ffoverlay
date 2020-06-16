import datetime
import time

def getEorzeaTime():
    """Created using code provided by /u/Clorifex https://www.reddit.com/r/ffxiv/comments/2pbl8p/eorzea_time_formula/cmvijkz?utm_source=share&utm_medium=web2x
    Returns a tuple of the type (int, int), representing hours and minutes in eorzean time (On EU servers anyway)
    """
    localEpoch = time.time()
    eorzeaEpoch = localEpoch * 20571.428571428573
    eorzeaMinutes = int((eorzeaEpoch / (1000 * 60)) % 60)
    eorzeaHours = int((eorzeaEpoch / (1000 * 60 * 60)) % 24)
    return (eorzeaHours, eorzeaMinutes)
