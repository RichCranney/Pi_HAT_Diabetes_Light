from datetime import datetime
import sys
import time
import math
from colorsys import hsv_to_rgb
from unicornhatmini import UnicornHATMini
from pydexcom import Dexcom
from decimal import Decimal, getcontext
import json
import webcolors
from webcolors import name_to_rgb


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


def dexcomConnect(username, password):
    try:
        dexcom = Dexcom(username, password, ous=True)
    except Exception as e:
         print("Error in authenticaiton: " + str(e))
         sys.exit

    return dexcom


def getDexcomValues(dexcom):
    readings = dexcom.get_glucose_readings(max_count=2)

    latestTime = readings[0].time
    previousTime = readings[1].time

    trendDiff = latestTime - previousTime
    trendTime = divmod(trendDiff.total_seconds(), 60)

    if trendTime[0] >= 3 and trendTime[0] <= 7:
        trend = Decimal(readings[0].mmol_l) - Decimal(readings[1].mmol_l)
        trendStr = '{0:+}'.format(trend)
    else:
        trend = 0
        trendStr = "--"

    LatestMinsAgo = divmod(trendDiff.total_seconds(), 60)
    LatestMinsAgo = int(LatestMinsAgo[0])

    return json.dumps({"mmol": readings[0].mmol_l, "mmol_str": str(readings[0].mmol_l), "delta": trend, "delta_str": trendStr, "time": latestTime, "delta_time": LatestMinsAgo}, cls=DecimalEncoder)
    

def clear_unicorn():
    uh.clear()


def set_unicorn(bloodGlucoseColour, deltaRateColour, deltaArrowType, bright):
    bg_r, bg_g, bg_b = name_to_rgb(bloodGlucoseColour)
    dr_r, dr_g, dr_b = name_to_rgb(deltaRateColour)
    width, height = uh.get_shape()

    uh.clear()
    uh.set_brightness(bright)
    uh.set_all(bg_r, bg_g, bg_b)
    
    if deltaArrowType == "up":
        deltaArrow = [
            [16, 3],
            [15, 2], [15, 3], [15, 4],
            [14, 1], [14, 2], [14, 3], [14, 4], [14, 5],
            [13, 0], [13, 1], [13, 2], [13, 3], [13, 4], [13, 5], [13,6]
        ]
    elif deltaArrowType == "down":
        deltaArrow = [
            [13, 3],
            [14, 2], [14, 3], [14, 4],
            [15, 1], [15, 2], [15, 3], [15, 4], [15, 5],
            [16, 0], [16, 1], [16, 2], [16, 3], [16, 4], [16, 5], [16,6]
        ]
    else:
        deltaArrow = [
            [15, 1], [15, 2], [15, 3], [15, 4], [15, 5],
            [14, 1], [14, 2], [14, 3], [14, 4], [14, 5],
            [13, 1], [13, 2], [13, 3], [13, 4], [13, 5]
        ]

    for x, y in deltaArrow:
        uh.set_pixel(x, y, dr_r, dr_g, dr_b)

    uh.show()


# Set Decimal place
getcontext().prec = 1

bloodGlucose = [
    [0.0, 3.9, "red"],
    [4.0, 4.5, "orange"],
    [4.6, 10.0, "green"],
    [10.0, 13.9, "blue"],
    [14.0, 99.9, "purple"]
]

deltaRates = [
    [-5, -1, "red", "down"],
    [-0.9, -0.3, "orange", "down"],
    [-0.2, 0.2, "green", "steady"],
    [0.3, 0.9, "yellow", "up"],
    [1.0, 5, "purple", "up"]
]

# Get Dexcom username and password (this should be stored in secret management)
Dexcom_username = 'richardcranney'
Dexcom_password = 'Wycombe!23'

# Connect to the Unicorn HAT
uh = UnicornHATMini()
# Connect to Dexcom
dexcom = dexcomConnect(Dexcom_username, Dexcom_password)

while True:

    # Get the CGM Values from Dexcom
    dexcomResponse = json.loads(getDexcomValues(dexcom))
    # Lets work out what values are returned and then we can choose its range
    bloodGlucoseColour = bloodGlucose[[int(dexcomResponse["mmol"] * 10) in range(int(start * 10), int(end * 10) + 1) for start, end, colour in bloodGlucose].index(True)][2]
    deltaRateColour = deltaRates[[int(Decimal(dexcomResponse["delta"]) * 10) in range(int(start * 10), int(end * 10) + 1) for start, end, colour, trendDirection in deltaRates].index(True)][2]
    trendDirection = deltaRates[[int(Decimal(dexcomResponse["delta"]) * 10) in range(int(start * 10), int(end * 10) + 1) for start, end, colour, trendDirection in deltaRates].index(True)][3]

    print(str(dexcomResponse["mmol"]) + " - " + bloodGlucoseColour)
    print(str(dexcomResponse["delta"]) + " - " + deltaRateColour)

    set_unicorn(bloodGlucoseColour, deltaRateColour, trendDirection, 0.3)

    time.sleep(60)
