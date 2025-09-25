from hebcal_api import Shabat
from hebcal_api.tools.types import EventType
from datetime import date

shabat = Shabat()
times = shabat.get_shabbat(geonameid=2172797)

for time in times.items:
    if time.type == EventType.CANDLES:
        print(time.candle.time.strftime("%H:%M"))
        break
    elif time.type == EventType.HAVDALAH:
        print(time.havdalah.time.strftime("%H:%M"))
        break
