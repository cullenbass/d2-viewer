import requests
import zipfile
import os
import sqlite3
import json
import csv
from pprint import pprint

sess = requests.Session()

# sess.headers.update({'X-Api-Key' : api_key})
# nah, start way the hell down at the __main__ if

#todo: make this actually functional; disk cache sure, but return raw sqlite database?
# can the connector even connect to an in-memory db? ¯\_(ツ)_/¯
def grab_manifest():
	res = sess.get('https://www.bungie.net/Platform/Destiny2/Manifest/')
	manifest = res.json()
	res = sess.get('https://bungie.net' + manifest['Response']['mobileWorldContentPaths']['en'])

	with open('temp.zip', 'wb') as f:
		f.write(res.content)

	with zipfile.ZipFile('temp.zip') as zf:
		filename = zf.namelist()[0]
		zf.extractall()
	os.rename(filename, 'Manifest.sqlite')
	os.remove('temp.zip')

# aay lmao same as above- more function, less helper
def get_item_hashes():
	db = sqlite3.connect('Manifest.sqlite')
	cur = db.cursor()

	weps = {}
	cur.execute('SELECT json FROM DestinySandboxPerkDefinition UNION SELECT json FROM DestinyInventoryItemDefinition')
	for item_json in cur:
		item = json.loads(item_json[0])
		weps[item['hash']] = item
	cur.close()
	db.close()
	return weps

# hey, this one's actually somewhat functional!
def get_names(hashes):
	name_search = {}
	for _, perk in hashes.items():
		if 'name' in perk['displayProperties'] and 'icon' in perk['displayProperties']:
			name_search[perk['displayProperties']['name']] = perk['hash']

	return name_search

# here we go
if __name__ == '__main__':
	if not os.path.isfile('Manifest.sqlite'):
		print('Cant find manifest, downloading...')
		grab_manifest()

	hashes = get_item_hashes()
	names = get_names(hashes)

	print(f'Hashes: {len(hashes)}')

	print(f'Names: {len(names)}')

	weapons = []
	with open('destinyWeapons.csv', 'r') as f:
		vault = csv.reader(f)
		next(vault)
		for wep in vault:
			w_name = wep[0]
			w_hash = wep[1]
			w_ele = wep[9]
			w_cat = wep[8]
			w_type = wep[5]
			perks = []
			weapon_perks = [p.replace('*', '') for p in wep[-18:]]
			print(weapon_perks)
			for p in weapon_perks:
				if p in names:
					perks.append(names[p])
			for h in perks:
				print(hashes[h])
			exit()

