import const
import requests
#from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
	
def sendTelegramMessage(message):
	return str(requests.get(const.TELEGRAM_URL+message))
	