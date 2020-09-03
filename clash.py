import requests
import json
import dateutil.parser
import datetime
import pytz

clanTag = 'L2208GR9'
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQxMDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXSwidHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g'
base_url = "https://proxy.royaleapi.dev/v1"
endp1 = f"/clans/%23{clanTag}/members"
endp2 = f"/clans/%23{clanTag}/currentriverrace"
header = {"Authorization": "Bearer %s" %key}

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
	list_combinedMembersData = []
	for dict_member in dict_clanData['items']:
		dict_member_new = dict_member
		for dict_participant in dict_currentRiverRace['clan']['participants']:
			if dict_member['tag'] == dict_participant['tag']:
				for k, v in dict_participant.items():
					dict_member_new[k] = v
		list_combinedMembersData.append(dict_member_new)
	return list_combinedMembersData

def formatDict_combinedMembersData(list_combinedMembersData):
	'''This block of code takes in list of dictionary of consolidated members data
	and allows formatting of key names and value. The formatted dictionary
	is then reappended into a new list. This list is returned. Noted that this can
	be further broken down into more functions.'''
	new_list = []
	for dict_member in list_combinedMembersData:
		dict_member['arena'] = dict_member['arena']['name']
		dict_member['lvl'] = dict_member['expLevel']
		dict_member.pop('expLevel')
		dict_member['role'] = dict_member['role'].title()
		dict_member['rank'] = dict_member['role']
		dict_member.pop('role')
		dateTime_lastSeen = dateutil.parser.isoparse(dict_member['lastSeen'])
		dateTime_lastSeen = dateTime_lastSeen.astimezone(pytz.timezone('Asia/Singapore'))
		dict_member['lastSeen'] = dateTime_lastSeen.strftime("%H:%M %d/%m")
		new_list.append(dict_member)
	return new_list

def makeListOfDict_currentRiverRace(dict_currentRiverRace):
	'''This block of code takes in raw dictionary of river race data
	and convert it to a list. This list is returned.'''
	dict_currentRiverRace = dict_currentRiverRace['clans']
	return dict_currentRiverRace

def sortListOfDict(listOfDict, keyToSortBy):
	'''This block of code sorts a dictionary by key specified. It 
	has yet to be completed.'''
	list_containsKeyToSortBy = [i for i in listOfDict if keyToSortBy in i.keys()]
	list_nonKeyToSortBy = [i for i in listOfDict if keyToSortBy not in i.keys()]
	new_list = sorted(list_containsKeyToSortBy, key=lambda i: i.get(keyToSortBy), reverse=True)
	new_list.extend(list_nonKeyToSortBy)
	return new_list

def formatString_listOfDict(listOfDict, keys_to_call):
	'''This block of code takes in a list of dictionaries object and
	a list of string objects which are keys to be called to become
	the headers of the table. The list is converted into a formatted
	string that resembles a table. This string is returned.'''
	
	dict_sizes = {} # dictionary to store no. of spaces allocated for each key for string formatting
	response = '' # initialise an empty string to store all the strings
	freeSpace = 3 # this is the additional spaces allocated for each key for string formatting

	# This loop is to set up the header and append spaces allocated for each key into dict_sizes
	for key in keys_to_call:
		max_value_size = max([len(str(e[key])) for e in listOfDict if key in e.keys()])
		if max_value_size < len(key): # if size of largest value in dictionary is shorter than key then use key instead
			max_value_size = len(key)
		dict_sizes[key] = max_value_size + freeSpace
		response += '{v:<{size}}'.format(v=key.title(), size=dict_sizes[key])

	response += '\n{v:-<{size}}\n'.format(v='', size=sum(dict_sizes.values()))
	
	# This loop is to set up the main body of the table, i.e. the members data
	for e in listOfDict:
		string_temp = ''
		for key in keys_to_call:
			if key in e.keys():
				string_temp += '{v:<{size}}'.format(v=e[key], size=dict_sizes[key])
			else:
				string_temp += '{:<{size}}'.format('n.a.', size=dict_sizes[key])
					
		response += '{}\n'.format(string_temp)
	return response

def clanLeaderboard(keys_to_call):
	e = ''
	while True:
		# Retrieve Data
		clanData = retrieve_clanData()
		currentRiverRace = retrieve_currentRiverRace()

		# Get Clan Leaderboard
		list_combinedMembersData = makeListOfDict_membersData(clanData, currentRiverRace)
		formatDict_combinedMembersData(list_combinedMembersData)
		
		# Check for sort
		if e == '1':
			list_combinedMembersData = sortListOfDict(list_combinedMembersData, 'trophies')
		elif e == '2':
			list_combinedMembersData = sortListOfDict(list_combinedMembersData, 'donations')
		elif e == '3':
			list_combinedMembersData = sortListOfDict(list_combinedMembersData, 'fame')
		elif e == '4':
			list_combinedMembersData = sortListOfDict(list_combinedMembersData, 'lvl')

		# Print block
		print('Available Keys:\n{}\n'.format('\n'.join(list(list_combinedMembersData[0].keys()))))
		print('Members: {}/50\n'.format(len(list_combinedMembersData)))
		print(formatString_listOfDict(list_combinedMembersData, keys_to_call))

		e = input("Enter to refresh. 'e' to return to menu. Otherwise: \n"
			"1. Sort by Trophies\n"
			"2. Sort by Donations\n"
			"3. Sort by Fame\n"
			"4. Sort by Level\n"
			"Your Choice: ")
		if e.lower() == 'e':
			break

def riverRaceLeaderboard(keys_to_call):
	e = ''
	while True:
		#Retrieve Data
		currentRiverRace = retrieve_currentRiverRace()

		# Check for sort
		if e == '1':
			list_currentRiverRace = sortListOfDict(list_currentRiverRace, 'name')
		elif e == '2':
			list_currentRiverRace = sortListOfDict(list_currentRiverRace, 'fame')
		elif e == '3':
			list_currentRiverRace = sortListOfDict(list_currentRiverRace, 'clanScore')

		# Get River Race Leaderboard
		list_currentRiverRace = makeListOfDict_currentRiverRace(currentRiverRace)
		print('Available Keys:\n{}\n'.format('\n'.join(list(list_currentRiverRace[0].keys()))))
		print(formatString_listOfDict(list_currentRiverRace, keys_to_call))

		e = input("Enter to refresh. 'e' to return to menu. Otherwise: \n"
			"1. Sort by Name\n"
			"2. Sort by Fame\n"
			"3. Sort by War Trophies\n"
			"Your Choice: ")
		if e.lower() == 'e':
			break

def main():
	# Settings for table
	keys_to_call_CMD = ['lastSeen', 'donations', 'trophies', 'arena', 'fame', 'repairPoints', 'lvl', 'rank', 'name']
	keys_to_call_CRC = ['fame', 'repairPoints', 'clanScore', 'name']
	
	while True:
		option = input('1. Clan Leaderboard\n'
			'2. River Race Leaderboard\n'
			'3. Print API member raw dictionary\n'
			'4. Print API river race raw dictionary\n'
			'Your Choice: '
			)
		if option == '3':
			print(retrieve_clanData())
		elif option == '4':
			print(retrieve_currentRiverRace())
		elif option == '1':
			clanLeaderboard(keys_to_call_CMD)
		elif option == '2':
			riverRaceLeaderboard(keys_to_call_CRC)
		else:
			print('Invalid. Try again.')
main()