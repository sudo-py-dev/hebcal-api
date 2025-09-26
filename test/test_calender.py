from hebcal_api import Calendar

calendar = Calendar()
events = calendar.get_events(geonameid=2172797, start="2025-09-26", end="2025-09-26")
print(events.items)