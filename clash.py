import requests
import json
import dateutil.parser as dp
import datetime
import pytz
import math

# Initialization
clanTag = 'L2208GR9'
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQxMDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXSwidHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g'
base_url = "https://proxy.royaleapi.dev/v1"
endp1 = f"/clans/%23{clanTag}/members"
endp2 = f"/clans/%23{clanTag}/currentriverrace"
header = {"Authorization": "Bearer %s" %key}

# Review Rubric
arenaGrade = {('Arena 7', 'Arena 8'):1,
				('Arena 9', 'Arena 10'):2,
				('Arena 11', 'Arena 12'):3,
				('Legendary Arena', 'Challenger II'):4,
				('Challenger III', 'Master I'):5,
				('Master II', 'Master III'):6,
				('Ultimate Champion', 'Royal Champion', 'Grand Champion', 'Champion'):7}
donateGrade = {900:7, 600:6, 400:5, 250:4, 120:3, 50:2, 10:1}
rrGrade = {3000:7, 2400:6, 1800:5, 1200:4, 800:3, 400:2, 100:1}

def retrieve_clanData():
	'''This block of code retrieves clan members data and return it as
	a dictionary.'''
	
	json_clanData = requests.get(base_url+endp1, headers=header)
	return json_clanData.json()

def retrieve_currentRiverRace():
	'''This block of code retrieves river race data and return it as
	a dictionary.'''
	
	json_currentRiverRace = requests.get(base_url+endp2, headers=header)
	return json_currentRiverRace.json()

def makeListOfDict_membersData(dict_clanData, dict_currentRiverRace):
	'''This block of code takes in raw dictionary of clan members and
	river race data and convert it to a list. This list contains consolidated
	members data in a dictionary object. This list is returned.'''
	
	list_membersData = []
	for dict_member in dict_clanData['items']:
		dict_member_new = {}
					   # New                     # Old
		dict_member_new['tag'] 		= dict_member['tag']
		dict_member_new['name'] 	= dict_member['name']
		dict_member_new['rank'] 	= dict_member['role']
		dict_member_new['lastSeen'] = dp.isoparse(dict_member['lastSeen']).astimezone(pytz.timezone('Asia/Singapore')).strftime("%H:%M %d/%m")
		dict_member_new['arena'] 	= dict_member['arena']['name']
		dict_member_new['trophy'] 	= dict_member['trophies']
		dict_member_new['donate'] 	= dict_member['donations']
		dict_member_new['received'] = dict_member['donationsReceived']
		dict_member_new['lvl'] 		= dict_member['expLevel']
		
		for dict_participant in dict_currentRiverRace['clan']['participants']:
			if dict_member['tag'] == dict_participant['tag']:
							   # New 						  # Old
				dict_member_new['fame'] 	= dict_participant.get('fame')
				dict_member_new['rp'] 		= dict_participant.get('repairPoints')
				dict_member_new['fame+rp'] 	= dict_participant.get('fame') + dict_participant.get('repairPoints')
				break
		for k, v in arenaGrade.items():
			if dict_member_new['arena'] in k:
				dict_member_new['ag'] = v
				break
			else:
				dict_member_new['ag'] = 0
		for k, v in donateGrade.items():
			if dict_member_new['donate'] >= k:
				dict_member_new['dg'] = v
				break
			else:
				dict_member_new['dg'] = 0
		for k, v in rrGrade.items():
			if dict_member_new.get('fame+rp') == None:
				dict_member_new['rrg'] = 0
				break
			elif dict_member_new['fame+rp'] >= k:
				dict_member_new['rrg'] = v
				break
			else:
				dict_member_new['rrg'] = 0
		dict_member_new['ovg'] = math.floor((dict_member_new['ag'] + dict_member_new['dg'] + dict_member_new['rrg'])/3)
		list_membersData.append(dict_member_new)
	return list_membersData

def makeListOfDict_riverRace(dict_riverRace):
	'''This block of code takes in raw dictionary of river race data
	and convert it to a list. This list is returned.'''
	
	list_riverRace = []
	for dict_clan in dict_riverRace['clans']:
		dict_clan_new = {}
					 # New 				   # Old
		dict_clan_new['tag'] 	= dict_clan['tag']
		dict_clan_new['name'] 	= dict_clan['name']
		dict_clan_new['fame'] 	= dict_clan['fame']
		dict_clan_new['rp'] 	= dict_clan['repairPoints']
		dict_clan_new['trophy'] = dict_clan['clanScore']
		list_riverRace.append(dict_clan_new)
	return list_riverRace

def sortListOfDict(listOfDict, keyToSortBy):
	'''This block of code sorts a dictionary by key specified.'''
	
	list_containsKeyToSortBy = [i for i in listOfDict if keyToSortBy in i.keys()]
	list_nonKeyToSortBy = [i for i in listOfDict if keyToSortBy not in i.keys()]
	list_sorted = sorted(list_containsKeyToSortBy, key=lambda i: i.get(keyToSortBy), reverse=True)
	list_sorted.extend(list_nonKeyToSortBy)
	return list_sorted

def formatString_listOfDict(listOfDict, keys_to_call):
	'''This block of code takes in a list of dictionaries object and
	a list of string objects which are keys to be called to become
	the headers of the table. The list is converted into a formatted
	string that resembles a table. This string is returned.'''
	
	dict_sizes = {} # dictionary to store no. of spaces allocated for each key for string formatting
	response = '{:>3} '.format('S/N')
	freeSpace = 3 # this is the additional spaces allocated for each key for string formatting
	i = 0
	# This loop is to set up the header and append spaces allocated for each key into dict_sizes
	for key in keys_to_call:
		max_value_size = max([len(str(e[key])) for e in listOfDict if key in e.keys()])
		if max_value_size < len(key): # if size of largest value in dictionary is shorter than key then use key instead
			max_value_size = len(key)
		dict_sizes[key] = max_value_size + freeSpace
		response += '{v:<{size}}'.format(v=key.title(), size=dict_sizes[key])

	response += '\n{v:-<{size}}\n'.format(v='', size=sum(dict_sizes.values())+3)
	
	# This loop is to set up the main body of the table, i.e. the members data
	for e in listOfDict:
		i += 1
		string_temp = ''
		for key in keys_to_call:
			if key in e.keys():
				string_temp += '{v:<{size}}'.format(v=e[key], size=dict_sizes[key])
			else:
				string_temp += '{:<{size}}'.format('n.a.', size=dict_sizes[key])
					
		response += '{:>3} {}\n'.format(str(i), string_temp)
	return response

def clanLeaderboard(keys_to_call):
	e = ''
	stored_e = ''
	string_sortMsg = ''
	i = 1
	
	list_sortCriteria = ['trophy', 'donate', 'fame', 'lvl', 'fame+rp', 'ovg']
	
	for criteria in list_sortCriteria:
		string_sortMsg += '{}. Sort by {}\n'.format(i, criteria.title())
		i += 1
	while True:
		# Retrieve Data
		clanData = retrieve_clanData()
		currentRiverRace = retrieve_currentRiverRace()
		list_membersData = makeListOfDict_membersData(clanData, currentRiverRace)
		
		# Check for sort
		if e in [str(i) for i in range(1,len(list_sortCriteria)+1)]:
			stored_e = e
		for i in range(len(list_sortCriteria)):
			if stored_e == str(i+1):
				list_membersData = sortListOfDict(list_membersData, list_sortCriteria[i])
				break

		# Print block
		print('\nMembers: {}/50'.format(len(list_membersData)))
		print(formatString_listOfDict(list_membersData, keys_to_call))
		e = input("<Enter> to refresh. 'e' to return to menu. Otherwise:\n{}Your Choice: ".format(string_sortMsg))
		if e.lower() == 'e':
			break

def riverRaceLeaderboard(keys_to_call):
	e = ''
	stored_e = ''
	string_sortMsg = ''
	i = 1
	
	list_sortCriteria = ['name', 'fame', 'rp']
	
	for criteria in list_sortCriteria:
		string_sortMsg += '{}. Sort by {}\n'.format(i, criteria.title())
		i += 1
	while True:
		#Retrieve Data
		dict_riverRace = retrieve_currentRiverRace()
		list_riverRace = makeListOfDict_riverRace(dict_riverRace)

		# Check for sort
		if e in [str(i) for i in range(1,len(list_sortCriteria)+1)]:
			stored_e = e
		for i in range(len(list_sortCriteria)):
			if stored_e == str(i+1):
				list_riverRace = sortListOfDict(list_riverRace, list_sortCriteria[i])
				break

		# Print block
		print(formatString_listOfDict(list_riverRace, keys_to_call))
		e = input("<Enter> to refresh. 'e' to return to menu. Otherwise:\n{}Your Choice: ".format(string_sortMsg))
		if e.lower() == 'e':
			break

def checkAvailableKeys():
	clanData = retrieve_clanData()
	riverRace = retrieve_currentRiverRace()

	list_membersData = makeListOfDict_membersData(clanData, riverRace)

	list_riverRace = makeListOfDict_riverRace(riverRace)

	print('Available keys for clan data:\n{}\n'.format('\n'.join(list(list_membersData[0].keys()))))
	print('Available keys for riverrace data:\n{}\n'.format('\n'.join(list(list_riverRace[0].keys()))))

def main():
	# Settings for table ---------------------------------------------------------------------------------------
	keysToCall_mD = ['lastSeen', 'trophy', 'rank',
						'lvl', 'donate', 'arena', 'fame',
						'rp', 'fame+rp', 'dg', 'ag', 'rrg', 'ovg', 'name']
	keysToCall_rR = ['fame', 'rp', 'trophy', 'tag', 'name']
	# ----------------------------------------------------------------------------------------------------------

	while True:
		option = input('1. Clan Leaderboard\n'
			'2. River Race Leaderboard\n'
			'Your Choice: ')
		if option == '3':
			print(retrieve_clanData())
		elif option == '4':
			print(retrieve_currentRiverRace())
		elif option == '5':
			checkAvailableKeys()
		elif option == '1':
			clanLeaderboard(keysToCall_mD)
		elif option == '2':
			riverRaceLeaderboard(keysToCall_rR)
		else:
			print('Invalid. Try again.')
main()