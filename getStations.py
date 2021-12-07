import requests

STATIONS_URL = 'https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/stations'
API_KEY = 'bd9343e8d7b24748ae3a15d67b9da292'
headers = {'Ocp-Apim-Subscription-Key': API_KEY}
r = requests.get(STATIONS_URL, headers=headers)

data = r.json()

for stations in data['payload']:
	result = stations['code']
	result += " - "
	result += stations['namen']['lang']
	print(result)