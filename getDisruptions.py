import json
import requests
import utils
import const # constant variables


def getStationInfo(station):
	result = ""
	headers = {'Ocp-Apim-Subscription-Key': const.API_KEY}
	r = requests.get(const.DISRUPTIONS_URL+station, headers=headers)
	data = r.json()
	for disruption in data:
		result += "Disruption: "+disruption['title'] + "\n"
		result += disruption['timespans'][0]['situation']['label'] + "\n"
		if 'summaryAddtionalTravelTime' in disruption.keys():
			result += disruption['summaryAdditionalTravelTime']['label'] +" - "
		if 'expectedDuration' in disruption.keys():
			result += disruption['expectedDuration']['description'] +" "
		if 'timespans' in disruption.keys() and 'period' in disruption['timespans'][0].keys():
			result += disruption['timespans'][0]['period'] +" "
		result += "(id:"+disruption['id']+")\n\n"
	return result.strip()

message = ""
message = "DISRUPTIONS AMF AND ZL ACCORDING TO NS API\n"

message += getStationInfo('AMF') + "\n" + getStationInfo('ZL')
utils.sendTelegramMessage(message)