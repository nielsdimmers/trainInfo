import const
import requests
#from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def getOldMessages(file):
	oldMessages = []
	with open(file) as pastMessages:
			for line in pastMessages:
					oldMessages.append(line.strip())				
	pastMessages.close()
	return oldMessages
	
def saveOldMessage(file, key):
	savedMessages = open(file,'a')
	savedMessages.write(str(key)+'\n')
	savedMessages.close()
	
def sendTelegramMessage(message):
	return str(requests.get(const.TELEGRAM_URL+message))
	