import datetime
import time

#This number was provided by /u/Clorifex link is in getEorzeaTimeDecimal's description
EORZEA_EPOCH_MULTIPLIER = 20571.428571428573

def getEorzeaTimeDecimal():
        """
        Created using code provided by /u/Clorifex https://www.reddit.com/r/ffxiv/comments/2pbl8p/eorzea_time_formula/cmvijkz?utm_source=share&utm_medium=web2x
        Returns a tuple of the type (float, float), representing hours and minutes in eorzean time (On EU servers anyway)
        """
        local_epoch = time.time()
        eorzea_epoch = local_epoch * EORZEA_EPOCH_MULTIPLIER
        eorzea_minutes = (eorzea_epoch / (1000 * 60)) % 60
        eorzea_hours = (eorzea_epoch / (1000 * 60 * 60)) % 24
        return (eorzea_hours, eorzea_minutes)

def getEorzeaTime():
    """
    Returns a tuple of the type (int, int), representing hours and minutes in eorzean time (On EU servers anyway)
    """
    eorzea_hours_decimal, eorzea_minutes_decimal = getEorzeaTimeDecimal()
    return (int(eorzea_hours_decimal), int(eorzea_minutes_decimal))

def timeUntilInEorzea(target_time):
    """
    Target time is in hours
    """
    #Need error checking to make sure that eorzeaHours is a number between 0 and 24 (not including 24)
    if target_time < 0 or target_time >= 24:
        raise ValueError("targetTime must be a number greater than or equal to 0, and less than 24")
    eorzea_hours = getEorzeaTimeDecimal()[0]
    if target_time > eorzea_hours: # target is today
        seconds_until_target = (target_time-eorzea_hours)*175
    elif target_time < eorzea_hours: #target is tomorrow
        seconds_until_target = (24-eorzea_hours+target_time)*175
    else: # target is right now
        seconds_until_target = 0
    return seconds_until_target
