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


def set_unicorn(r, g, b, bright):
    uh.clear()
    uh.set_brightness(bright)
    uh.set_all(r, g, b)
    uh.show()


def rainbow_unicorn(bright):
    global fileContent
    uh.clear()
    uh.set_brightness(bright)
    uh.set_rotation(0)
    width, height = uh.get_shape()

    step = 0
    counter = 0

    while True and fileContent == "Unicorn":
        step += 1
        counter += 1

        for x in range(0, width):
            for y in range(0, height):
                dx = (math.sin(step / width + 20) * width) + height
                dy = (math.cos(step / height) * height) + height
                sc = (math.cos(step / height) * height) + width

                hue = math.sqrt(math.pow(x - dx, 2) + math.pow(y - dy, 2)) / sc
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1, 1)]

                uh.set_pixel(x, y, r, g, b)

        uh.show()
        time.sleep(1.0 / 60)

        if counter == 10:
            fileContent = check_file_contents()
            counter = 0

        uh.clear()


# Set Decimal place
getcontext().prec = 1

bloodGlucose = [
    [0.0, 3.9, "red"],
    [4.0, 4.5, "orange"],
    [4.6, 10.0, "green"],
    [10.0, 13.9, "yellow"],
    [14.0, 99.9, "purple"]
]

deltaRates = [
    [-5, -1, "red"],
    [-0.9, -0.3, "orange"],
    [-0.2, 0.2, "green"],
    [0.3, 0.9, "yellow"],
    [1.0, 5, "purple"]
]

# Get Dexcom username and password (this should be stored in secret management)
Dexcom_username = 'richardcranney'
Dexcom_password = 'Wycombe!23'

# Connect to the Unicorn HAT
uh = UnicornHATMini()
# Connect to Dexcom
dexcom = dexcomConnect(Dexcom_username, Dexcom_password)
# Get the CGM Values from Dexcom
dexcomResponse = json.loads(getDexcomValues(dexcom))
# Lets work out what values are returned and then we can choose its range
bloodGlucoseColour = bloodGlucose[[int(dexcomResponse["mmol"] * 10) in range(int(start * 10), int(end * 10) + 1) for start, end, colour in bloodGlucose].index(True)][2]
deltaRateColour = deltaRates[[int(Decimal(dexcomResponse["delta"]) * 10) in range(int(start * 10), int(end * 10) + 1) for start, end, colour in deltaRates].index(True)][2]


print(str(dexcomResponse["mmol"]) + " - " + bloodGlucoseColour)
print(str(dexcomResponse["delta"]) + " - " + deltaRateColour)

set_unicorn(name_to_rgb(bloodGlucoseColour)[0],name_to_rgb(bloodGlucoseColour)[1],name_to_rgb(bloodGlucoseColour)[2],0.5)
