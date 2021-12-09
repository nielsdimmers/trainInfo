from google.transit import gtfs_realtime_pb2 # Reads in OV data
import requests # Imprts requests directly
import csv # Required for reading in CSV
import time # used for time parsing
import os
import logging
import const
import utils
import messagesSent

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

interestingStations = ['Amersfoort Centraal', 'Zwolle','Amersfoort Vathorst','Den Haag Centraal']

# 1: Lees routes in
with open('data/routes.txt', newline='') as csvfile:
    routes = list(csv.reader(csvfile))  
# CSV stop Data: 
# route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_color,route_text_color,route_url

# 2: Lees stops in
with open('data/stops.txt', newline='') as csvfile:
    stops = list(csv.reader(csvfile))

# CSV Top Data:
# ['stop_id', 'stop_code', 'stop_name', 'stop_lat', 'stop_lon', 'location_type', 'parent_station', 'stop_timezone', 'wheelchair_boarding', 'platform_code', 'zone_id']
# So stop name is in field 2

# 2a: Zoek uit welke stop voor mij interessant is
stationIDs = []

for stop in stops:
	if (stop[2] in interestingStations):
		stationIDs.append(str(stop[0]))

# 3: Zoek de bijbehorende routes
feed = gtfs_realtime_pb2.FeedMessage()

# Download train updates file if it's older than RETENTION_TIME_SECS, also download it if it's not there
currentTime = time.time()
if not os.path.isfile(const.DATABASE_FILE_NAME) or (currentTime - os.stat(const.DATABASE_FILE_NAME).st_mtime) > const.RETENTION_TIME_SECS:
	logger.info("Downloading new file")
	if os.path.isfile(const.DATABASE_FILE_NAME):
		os.remove(const.DATABASE_FILE_NAME) # remove old file if it's there
	r = requests.get(const.DATABASE_FILE_URL, allow_redirects=True)
	open(const.DATABASE_FILE_NAME, 'wb+').write(r.content)
else:
	logger.info("Less than "+str(const.RETENTION_TIME_SECS)+" seconds passed, using original file.")

# Read from the file
response = open(const.DATABASE_FILE_NAME, "rb")
feed.ParseFromString(response.read())
result = ""

# This data is structured this way...
for entity in feed.entity:
	if entity.HasField('trip_update') and (not messagesSent.messageExists(str(entity.id))):
		# A stop is a station receiving a notification. I'm looking for the ones I'm interested in
		for stopTime in entity.trip_update.stop_time_update:
			if str(stopTime.stop_id) in stationIDs and stopTime.departure.delay > const.DELAY_NOTIFICATION_THRESHOLD: # you can remove the delay stuff here if you'd like.   
				# Find the matching route so I can actually call it by it's name
				# Since it's a CSV, I guess this is the most efficient.
				i = 0
				while i < len(routes) and routes[i][0] != entity.trip_update.trip.route_id:
 					i += 1
				if i < len(routes):
 					result += routes[i][2] + " " +routes[i][3] + " "
				else:
 					result += "<ROUTE "+entity.trip_update.trip.route_id+" NOT FOUND>"
				
				result += const.SCHEDULE_RELATIONSHIP[entity.trip_update.trip.schedule_relationship]+ "\n"
				result += "Vertrek: "+time.strftime('%H:%M:%S', time.localtime(stopTime.departure.time)) + " (delay: "+str(stopTime.departure.delay)+" seconds or "+str(round(stopTime.departure.delay/60))+" minutes) \n"
		messagesSent.addNewMessage(str(entity.id)) # write the ID to the database, so we know we've handled this message

if result:
	logger.info("Send message response " + utils.sendTelegramMessage(result))
else:
	logger.info("result empty, not sending message.")

## example data

#trip { 
#   trip_id: "137429647"
#   start_time: "12:34:00"
#   start_date: "20211205"
#   schedule_relationship: SCHEDULED
#   route_id: "79942"
#   direction_id
#}

# stop_time_update {
#   departure {
#     delay: 148
#     time: 1638704188
#   }
#   stop_id: "134824"
#   schedule_relationship: SCHEDULED
# }

# You'll have to look a lot in this file: https://github.com/MobilityData/gtfs-realtime-bindings/blob/master/python/google/transit/gtfs_realtime_pb2.py
