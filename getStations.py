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
		API_KEY = 'bd9343e8d7b24748ae3a15d67b9da292'
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

	def getDepartures(self,update,context):
		stationcode = update.message.text.split(' ')[1]
		result = "Planned departures: \n"
		headers = {'Ocp-Apim-Subscription-Key': 'bd9343e8d7b24748ae3a15d67b9da292'}
		r = requests.get('https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures?station='+stationcode, headers=headers)
		data = r.json()['payload']['departures']
		
		table = pt.PrettyTable(['Ty', 'naar', 'vertrek','vertr','spr','Status'])		
		
		for disruption in data:
			table_row = []
			
			table_row.append(disruption['trainCategory'])
			table_row.append(disruption['direction'])
			
		
			result += disruption['trainCategory'] + ' ' + disruption['direction'] + ' om '
			plantijd = disruption['plannedDateTime'][:-2] + ':' +  disruption['plannedDateTime'][-2:]
			plannedDeparture = datetime.datetime.fromisoformat(plantijd)
			vertrektijd = disruption['actualDateTime'][:-2] + ':' +  disruption['actualDateTime'][-2:]
			actualDeparture = datetime.datetime.fromisoformat(vertrektijd)
			
			
			departureHour = '%s' % actualDeparture.hour
			departureMinute = '%s' % actualDeparture.minute
			departureHour = departureHour.rjust(2,'0')
			departureMinute = departureMinute.rjust(2,'0')
			
			table_row.append('%s:%s' % (departureHour, departureMinute))
			
			result += ' %s:%s ' % (actualDeparture.hour, actualDeparture.minute)
			

			if actualDeparture != plannedDeparture:
				verschilTijd = actualDeparture - plannedDeparture
				result += ' (+%s)' % verschilTijd
				table_row.append('%s' % verschilTijd)
			else:
				table_row.append('')

			result += 'vanaf spoor: %s ' % disruption['actualTrack']
			
			spoor = '' + disruption['actualTrack']

			if disruption['actualTrack'] != disruption['plannedTrack']:
				result += '(!)'
				spoor += ' (!)'
			
			table_row.append(spoor)
			
			result += '(%s)' % disruption['departureStatus']
			
			table_row.append(disruption['departureStatus'])
			
			result += '\n'
			table.add_row(table_row)
			# 2022-12-11T21:34:00+0100
			

		update.message.reply_text(f'```{table}```',quote=False,parse_mode=telegram.ParseMode.MARKDOWN_V2)
		

	def main(self):
		updater = Updater(self.config.get_item('telegram','TELEGRAM_API_TOKEN'), use_context=True)
		dp = updater.dispatcher
		dp.add_handler(CommandHandler('station',self.getStation), True)
		dp.add_handler(CommandHandler('departures',self.getDepartures), True)
		updater.start_polling()
		updater.idle()
	
if __name__ == '__main__':
	bot = Stations()
	bot.main()