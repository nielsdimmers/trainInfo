import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import telegram
import datetime
import prettytable as pt
import config

class Stations: 

	config = config.config()

	def getStation(self,update,context):
		STATIONS_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations'
		API_KEY = self.config.get_item('nsapi','NS_API_TOKEN')
		headers = {'Ocp-Apim-Subscription-Key': API_KEY}
		r = requests.get(STATIONS_URL, headers=headers)

		data = r.json()

		findString = update.message.text.split(' ')[1]
		table = pt.PrettyTable(['Code', 'Station', 'UICCode'])
		
		for stations in data['payload']:
		
		
			result = stations['code']
			result += stations['namen']['lang']
			result +=  stations['UICCode']
			
			if findString.lower() in result.lower():
				table.add_row([stations['code'],stations['namen']['lang'],stations['UICCode']])

		update.message.reply_text(f'```{table}```',quote=False,parse_mode=telegram.ParseMode.MARKDOWN_V2)

	def getDateTimeFromJSON(self,dateString):
		dateString = dateString[:-2] + ':' +  dateString[-2:]
		return datetime.datetime.fromisoformat(dateString)
			
	def getTimeFromJSON(self,dateString):
		dateTimeObject = self.getDateTimeFromJSON(dateString)
		return dateTimeObject.strftime('%H:%M')


	def getJourney(self,update,context):
		result = ""
		journey_code = update.message.text.split(' ')[1]
		headers = {'Ocp-Apim-Subscription-Key':  self.config.get_item('nsapi','NS_API_TOKEN')}		
		r = requests.get('https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/journey?train='+journey_code, headers=headers)
		data = r.json()
		
		table = pt.PrettyTable(['Station', 'actual time', 'Delay'])
		table.align = 'l'

		for station in data['payload']['stops']:
			if station['status'] == 'PASSING':
				continue		
			row = []
			row.append(station['stop']['name'])
			if len(station['departures']) > 0:
				departureTime = self.getTimeFromJSON(station['departures'][0]['actualTime'])
				
				departureDateTime = self.getDateTimeFromJSON(station['departures'][0]['actualTime'])
				
				if departureDateTime.timestamp() > datetime.datetime.now().timestamp() and not PassedCurrentStation:
					PassedCurrentStation = True
					departureTime += ' *'
				elif departureDateTime.timestamp() < datetime.datetime.now().timestamp():
					PassedCurrentStation = False
				
				
				row.append(departureTime)
				row.append(station['departures'][0]['delayInSeconds'])
			else:
				row.append('n/a')
				row.append('n/a')
			table.add_row(row)
				
		update.message.reply_text(f'```{table}```',quote=False,parse_mode=telegram.ParseMode.MARKDOWN_V2)

	def getDepartures(self,update,context):
		stationcode = update.message.text.split(' ')[1]
		headers = {'Ocp-Apim-Subscription-Key':  self.config.get_item('nsapi','NS_API_TOKEN')}
		r = requests.get('https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures?station='+stationcode, headers=headers)
		data = r.json()['payload']['departures']
		
		table = pt.PrettyTable(['Ty', 'To', 'Dprt','Delay','Tr','State','Name'])
		table.align = 'l'
		
		for departure in data:
			table_row = []
			
			table_row.append(departure['trainCategory'])
			table_row.append(departure['direction'])
			
			plannedDeparture = self.getDateTimeFromJSON(departure['plannedDateTime'])
			actualDeparture = self.getDateTimeFromJSON(departure['actualDateTime'])
			
			table_row.append(self.getTimeFromJSON(departure['actualDateTime']))
			delay = actualDeparture - plannedDeparture
			
			if delay.total_seconds() > 0:
				table_row.append('%s' % delay)
			else:
				table_row.append('')
			
			spoor = '' + departure['actualTrack']

			if departure['actualTrack'] != departure['plannedTrack']:
				spoor += ' (!)'
			
			table_row.append(spoor)
			
			
			table_row.append(departure['departureStatus'])
			
			table_row.append(departure['name'].split()[-1])

			table.add_row(table_row)
			
		update.message.reply_text(f'```{table}```',quote=False,parse_mode=telegram.ParseMode.MARKDOWN_V2)
		

	def main(self):
		updater = Updater(self.config.get_item('telegram','TELEGRAM_API_TOKEN'), use_context=True)
		dp = updater.dispatcher
		dp.add_handler(CommandHandler('station',self.getStation), True)
		dp.add_handler(CommandHandler('departures',self.getDepartures), True)
		dp.add_handler(CommandHandler('journey',self.getJourney), True)
		updater.start_polling()
		updater.idle()
	
if __name__ == '__main__':
	bot = Stations()
	bot.main()