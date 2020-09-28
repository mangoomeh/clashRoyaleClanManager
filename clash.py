import sqlite3
import requests
import json
import dateutil.parser as dp
import datetime
import pytz
import math

# ================================================================================
# Settings for API
# ================================================================================
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQxMDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXSwidHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g'
base_url = "https://proxy.royaleapi.dev/v1"
header = {"Authorization": "Bearer %s" %key}

# ================================================================================
# RETRIEVE FUNCTIONS
# ================================================================================
def retrieve_clanOnly(clanTag):
	'''This block of code retrieves clan members data and return it as
	a dictionary.'''
	endp = f"/clans/%23{clanTag}"
	json_clanData = requests.get(base_url+endp, headers=header)
	dict_clanData = json_clanData.json()
	reqcode = json_clanData.status_code
	return dict_clanData, reqcode

def retrieve_clanData(clanTag):
	'''This block of code retrieves clan members data and return it as
	a dictionary.'''
	endp = f"/clans/%23{clanTag}/members"
	json_clanData = requests.get(base_url+endp, headers=header)
	dict_clanData = json_clanData.json()
	reqcode = json_clanData.status_code
	return dict_clanData, reqcode

def retrieve_currentRiverRace(clanTag):
	'''This block of code retrieves river race data and return it as
	a dictionary.'''
	endp = f"/clans/%23{clanTag}/currentriverrace"
	json_riverRaceData = requests.get(base_url+endp, headers=header)
	dict_riverRaceData = json_riverRaceData.json()
	reqcode = json_riverRaceData.status_code
	return dict_riverRaceData, reqcode

def retrieve_playerLog(playerTag):
	'''This block of code retrieves player battle log data and return it as
	a dictionary.'''
	endp = f"/players/%23{playerTag}/battlelog"
	json_playerLogData = requests.get(base_url+endp, headers=header)
	dict_playerLogData = json_playerLogData.json()
	reqcode = json_playerLogData.status_code
	return dict_playerLogData, reqcode

# =================================================================================
# NEW ITERABLE DATA CREATION
# ================================================================================
def makeListOfdict_cLB(dict_clanData, dict_riverRaceData):
	'''This block of code takes in raw dictionary of clan members and
	river race data and convert it to a list. This list contains consolidated
	members data in a dictionary object. This list is returned.'''
	
	'''KEY(S) ADDED TO CLAN DATA: 	tag, name, rank, lastSeen, arena, trophy, donate,
									received, lvl, fame, rp, fame+rp'''
	# Structure: [{},{},{}]
	list_membersData = [] # new list to store new dictionaries
	for dict_m in dict_clanData['items']:
		dict_m_new = {}
					# New 				# Old
		dict_m_new['tag']		= dict_m.get('tag')
		dict_m_new['name'] 		= dict_m.get('name')
		dict_m_new['rank'] 		= dict_m.get('role').title()
		dict_m_new['lastSeen'] 	= dp.isoparse(dict_m.get('lastSeen')).astimezone(pytz.timezone('Asia/Singapore')).strftime("%d/%m %H:%M")
		dict_m_new['arena'] 	= dict_m['arena']['name']
		dict_m_new['trophy'] 	= dict_m.get('trophies')
		dict_m_new['donate'] 	= dict_m.get('donations')
		dict_m_new['received'] 	= dict_m.get('donationsReceived')
		dict_m_new['lvl'] 		= dict_m.get('expLevel')
		
		for dict_participant in dict_riverRaceData['clan']['participants']:
			if dict_m['tag'] == dict_participant['tag']:
							   # New 							# Old
				dict_m_new['fame'] 		= dict_participant.get('fame')
				dict_m_new['rp'] 		= dict_participant.get('repairPoints')
				dict_m_new['fame+rp'] 	= dict_participant.get('fame') + dict_participant.get('repairPoints')
				break
		list_membersData.append(dict_m_new)
	return list_membersData

def makeListOfdict_rRLB(dict_riverRaceData):
	'''This block of code takes in raw dictionary of river race data
	and convert it to a list. This list is returned.'''
	
	'''KEY(S) ADDED TO RIVERRACE DATA: tag, name, fame, rp, trophy'''
	# Structure: [{},{},{}]
	list_riverRace = [] # new list to store new dictionaries
	for dict_clan in dict_riverRaceData['clans']:
		dict_clan_new = {}
					 # New 				   # Old
		dict_clan_new['tag'] 	= dict_clan.get('tag')
		dict_clan_new['name'] 	= dict_clan.get('name')
		dict_clan_new['fame'] 	= dict_clan.get('fame')
		dict_clan_new['rp'] 	= dict_clan.get('repairPoints')
		dict_clan_new['trophy'] = dict_clan.get('clanScore')
		list_riverRace.append(dict_clan_new)
	return list_riverRace

def makeListOfClans_rR(dict_riverRaceData):
	'''This block of code takes in raw dictionary of river race data
	and convert it to a list of dictionaries containing only info about
	clans and their war participants. This list is returned.'''

	'''KEYS(S) ADDED TO RIVERRACE INDIVIDUAL'S DATA: name, fame+rp'''
	 # Structure: [[{},{}], [{},{}]]
	listOfClans = []
	for dict_clan in dict_riverRaceData['clans']:
		listOfMembers = []
		for dict_i in dict_clan['participants']:
			dict_i_new = {}
			dict_i_new['clan'] = dict_clan.get('name')
			dict_i_new['name'] = dict_i.get('name')
			dict_i_new['fame+rp'] = dict_i.get('fame') + dict_i.get('repairPoints')
			listOfMembers.append(dict_i_new)
		listOfClans.append(listOfMembers)
	return listOfClans

def makeListOfDict_battleLog(list_playerLog):
	'''This block of code takes in raw dictionary of player log data
	and convert it to a list. This list is returned.'''
	
	'''KEY(S) ADDED TO battleLog DATA: type, mode, clan, name'''
	# Structure: [{},{},{}]
	listOfGames = []
	for game in list_playerLog:
		dict_game_new = {}
		dict_game_new['type'] = game.get('type')
		dict_game_new['time'] = dp.isoparse(game.get('battleTime')).astimezone(pytz.timezone('Asia/Singapore')).strftime("%d/%m %H:%M")
		dict_game_new['mode'] = game['gameMode'].get('name')
		dict_game_new['score'] = str(game['team'][0].get('crowns')) + '-' + str(game['opponent'][0].get('crowns'))
		dict_game_new['name'] = game['opponent'][0].get('name')
		if game.get('type') == 'boatBattle':
			if game['team'][0].get('startingTrophies') == None:
				dict_game_new['attacker'] = 'no'
			else:
				dict_game_new['attacker'] = 'yes'
		if game['opponent'][0].get('clan') != None:
			dict_game_new['clan'] = game['opponent'][0]['clan'].get('name')
		
		listOfGames.append(dict_game_new)
	return listOfGames

# ================================================================================
# ITERABLE EDITTING
# ================================================================================
def sortListOfDict(listOfDict, keyToSortBy):
	'''This block of code sorts a dictionary by key specified to sort by.'''
	
	list_hasKey = [i for i in listOfDict if keyToSortBy in i.keys()] # dicts that contains the key
	list_nonKey = [i for i in listOfDict if keyToSortBy not in i.keys()] # dicts that does not contain the key
	list_sorted = sorted(list_hasKey, key=lambda i: i.get(keyToSortBy), reverse=True) # sort descending
	list_sorted.extend(list_nonKey) # add back dict that does not contain the key at the end
	return list_sorted

# Review Rubric 30 donates
def dReview(list_membersData):
	for dict_m in list_membersData:
		if dict_m['donate'] >= 30:
			dict_m['review'] = 'pass'
		else:
			dict_m['review'] = 'fail'
	return list_membersData

# Review Rubric CWG
def cwgReview(list_membersData):
	# KEY(S) ADDED: 'ag', 'dg', 'rrg', 'ovg'
	arenaGrade = {('Arena 7', 'Arena 8'):1,
				  ('Arena 9', 'Arena 10'):2,
				  ('Arena 11', 'Arena 12'):3,
				  ('Legendary Arena', 'Challenger II'):4,
				  ('Challenger III', 'Master I'):5,
				  ('Master II', 'Master III'):6,
				  ('Ultimate Champion', 'Royal Champion', 'Grand Champion', 'Champion'):7}
	donateGrade = {900:7, 600:6, 400:5, 250:4, 120:3, 50:2, 10:1}
	rrGrade = {3000:7, 2400:6, 1800:5, 1200:4, 800:3, 400:2, 100:1}

	for dict_m in list_membersData:
		for k, v in arenaGrade.items():
			if dict_m['arena'] in k:
				dict_m['ag'] = v
				break
			else:
				dict_m['ag'] = 0
		for k, v in donateGrade.items():
			if dict_m['donate'] >= k:
				dict_m['dg'] = v
				break
			else:
				dict_m['dg'] = 0
		for k, v in rrGrade.items():
			if dict_m.get('fame+rp') == None:
				dict_m['rrg'] = 0
				break
			elif dict_m['fame+rp'] >= k:
				dict_m['rrg'] = v
				break
			else:
				dict_m['rrg'] = 0
		dict_m['ovg'] = math.floor((dict_m['ag'] + dict_m['dg'] + dict_m['rrg'])/3)
	return list_membersData

# Review Rubric RBG
def rbgReview(list_membersData):
	# KEY(S) ADDED: 'review(bool)'
	
	# Rubric Settings ===================================
	rubric = {
			  'c'	: {'d':900, 'f':5000},		# d = donate, f = fame+rp
			  'e'	: {'d':300, 'f':2500},
			  'm'	: {'d':30, 'f':500}		  
			  }
	
	review = {
			  'Coleader': {'m':'demote(m)', 	'e':'demote(e)', 	'c':'retain'},
			  'Elder'	: {'m':'demote(m)', 	'e':'retain', 		'c':'promote(co)'},
			  'Member'	: {'m':'retain', 		'e':'promote(e)', 	'c':'promote(co)'}
			  }
	# ===================================================
	
	for dict_m in list_membersData:
		d = dict_m.get('donate')
		f = dict_m.get('fame+rp')
		r = dict_m.get('rank')
		for krb, vrb in rubric.items():
			if d < rubric['m']['d'] or f < rubric['m']['f']:
				dict_m['review(bool)'] = 'fail'
				break
			elif d >= vrb['d'] and f >= vrb['f']:
				if r in review.keys():
					dict_m['review(bool)'] = review[r][krb]
					break
				else:
					dict_m['review(bool)'] = krb
					break
	return list_membersData

# ================================================================================

def formatString_listOfDict(listOfDict, keysToCall):
	'''This block of code takes in a list of dictionaries object and
	a list of string objects which are keys to be called to become
	the headers of the table. The list is converted into a formatted
	string that resembles a table. This string is returned.'''
	
	dict_sizes = {} # dictionary to store no. of spaces allocated for each key for string formatting
	response = '\n{:>3}| '.format('S/N') # initialize string and add first header
	freeSpace = 3 # this is the additional spaces allocated for each key for string formatting
	# This loop is to set up the header and append spaces allocated for each key into dict_sizes
	for key in keysToCall:
		try:
			max_value_size = max([len(str(e[key])) for e in listOfDict if key in e.keys()]) # get size of largest value
			if max_value_size < len(key): # if size of largest value in dictionary is shorter than key then use key instead
				max_value_size = len(key)
			dict_sizes[key] = max_value_size + freeSpace
		except ValueError:
			max_value_size = len(key)
			dict_sizes[key] = max_value_size + freeSpace
		response += '{v:<{size}}'.format(v=key.title(), size=dict_sizes[key])

	response += '\n{:-<{size}}\n'.format('', size=len(response))
	
	# This loop is to set up the main body of the table, i.e. the members data
	for i in range(len(listOfDict)):
		string_temp = ''
		for key in keysToCall:
			if key in listOfDict[i].keys():
				string_temp += '{v:<{size}}'.format(v=listOfDict[i][key], size=dict_sizes[key])
			else:
				string_temp += '{:<{size}}'.format('n.a.', size=dict_sizes[key])		
		response += '{:>3}| {}\n'.format(str(i+1), string_temp)
	return response

# ================================================================================
# INTERFACES
# ================================================================================
def getCLBdata(clanTag):
	# Retrieve Data
	dict_clanData = retrieve_clanData(clanTag)[0]
	dict_riverRaceData = retrieve_currentRiverRace(clanTag)[0]
	memberCount = len(dict_clanData['items'])
	clanFame = dict_riverRaceData['clan'].get('fame')

	'''KEY(S) ADDED: 	tag, name, rank, lastSeen, arena, trophy, donate,
						received, lvl, fame, rp, fame+rp'''
	list_membersData = makeListOfdict_cLB(dict_clanData, dict_riverRaceData)
	
	# KEY(S) ADDED: 'ag', 'dg', 'rrg', 'ovg', 'review(bool)', 'review'
	cwgReview(list_membersData)
	rbgReview(list_membersData)
	dReview(list_membersData)
	return list_membersData, memberCount, clanFame

def clanLeaderboard(keysToCall, clanTag):
	# Initialize variables
	e = ''
	stored_e = ''

	# This block generates sort message
	string_sortMsg = ''
	for i in range(len(keysToCall)):
		string_sortMsg += '{}. Sort by {}\n'.format(i+1, keysToCall[i].title())
	
	# This block is the interface
	while True:
		# Get clan data
		list_membersData, memberCount, clanFame = getCLBdata(clanTag)
		
		# Check for sort
		if e in [str(i) for i in range(1,len(keysToCall)+1)]:
			stored_e = e
		for i in range(len(keysToCall)):
			if stored_e == str(i+1):
				list_membersData = sortListOfDict(list_membersData, keysToCall[i])
				print('Sort Completed.\n')
				break

		# Print block
		print('\nMembers: {}/50'.format(memberCount))
		print('Fame: {}/50000'.format(clanFame))
		print(formatString_listOfDict(list_membersData, keysToCall))
		e = input(f"<Enter> to refresh. 'e' to return to menu. Otherwise:\n{string_sortMsg}Your Choice: ")
		if e.lower() == 'e':
			break

def getRRLB(clanTag):
	'''KEY(S) ADDED: 	fame, rp, trophy, tag, name'''
	list_riverRace = makeListOfdict_rRLB(retrieve_currentRiverRace(clanTag)[0])
	return list_riverRace

def riverRaceLeaderboard(keysToCall, clanTag):
	# Initialize variables
	e = ''
	stored_e = ''

	# This block generates sort message
	string_sortMsg = ''
	for i in range(len(keysToCall)):
		string_sortMsg += '{}. Sort by {}\n'.format(i+1, keysToCall[i].title())

	# This block is the interface
	while True:
		# Get Data
		list_riverRace = getRRLB(clanTag)

		# This block checks if sort is needed and sort if needed
		if e in [str(i) for i in range(1,len(keysToCall)+1)]:
			stored_e = e
		for i in range(len(keysToCall)):
			if stored_e == str(i+1):
				list_riverRace = sortListOfDict(list_riverRace, keysToCall[i])
				break

		# Print block
		print(formatString_listOfDict(list_riverRace, keysToCall))
		# textToImg(formatString_listOfDict(list_riverRace, keysToCall))
		e = input("<Enter> to refresh. 'e' to return to menu. Otherwise:\n{}Your Choice: ".format(string_sortMsg))
		
		# Check if user wants to return to menu
		if e.lower() == 'e':
			break

def riverRaceClanMembers(keysToCall, clanTag):

	# This block is the interface
	while True:
		#Retrieve Data
		dict_riverRaceData = retrieve_currentRiverRace(clanTag)[0]
		listOfClans = makeListOfClans_rR(dict_riverRaceData)

		for clan in listOfClans:
			clan = sortListOfDict(clan, 'fame+rp')
			print('\nClan: {}'.format(clan[0].get('clan')), formatString_listOfDict(clan, keysToCall))

		# Print block
		e = input("<Enter> to refresh. 'e' to return to menu.")
		
		# Check if user wants to return to menu
		if e.lower() == 'e':
			break

def playerLog(keysToCall, clanTag):
	# Initialize variables
	e = ''
	stored_e = ''
	clan = makeListOfdict_cLB(retrieve_clanData(clanTag)[0], retrieve_currentRiverRace()[0])
	# This block generates sort message
	string_sortMsg = ''
	for i in range(len(keysToCall)):
		string_sortMsg += '{}. Sort by {}\n'.format(i+1, keysToCall[i].title())

	while True:
		print(formatString_listOfDict(clan, ['tag', 'name',]))
		try:
			while True:
				choice = int(input("<Enter> to return to menu. Else, enter player choice: "))
				if choice <= len(clan) and choice >= 1:
					break
				else:
					print(f'Clan only has {len(clan)} members.')
		except ValueError:
			print('Non-integer type values detected. Quitting.')
			return
		player = clan[choice-1]
		playerTag = player['tag'][1:]
		print('Accessing player log for {}...'.format(player['name']))
		while True:
			list_playerLog = retrieve_playerLog(playerTag)[0]
			listOfGames = makeListOfDict_battleLog(list_playerLog)
			# Print block
			print(formatString_listOfDict(listOfGames, keysToCall))
			e = input("<Enter> to refresh. 'e' to return to player choice. Otherwise:\n{}Your Choice: ".format(string_sortMsg))
			
			# Check if user wants to return to menu
			if e.lower() == 'e':
				break

def printAvailableKeys(listOfDict):
	list_keys = []
	for member in listOfDict:
		list_keys.extend([key for key in member.keys() if key not in list_keys])
	print('Available Keys:')
	for i in range(len(list_keys)):
		print(f'{i+1}. {list_keys[i]}')


def clanManagerMenu():
    # SQLITE ==================================
    conn = sqlite3.connect('clanTags.db')
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE clanTags (tag)""")
    except sqlite3.OperationalError:
        pass
    # =========================================
    
    # INTERFACE ===============================
    while True:
        c.execute('SELECT * FROM clanTags')
        clanTagList = c.fetchall()
        noOfTags = len(clanTagList)
        inputText = '\nClan Manager\n' + '---------------\n'
        for i in range(noOfTags):
            dict_clanData, reqcode = retrieve_clanOnly(clanTagList[i][0])
            inputText += '{}. {}\n'.format(i+1, dict_clanData.get('name'))
        try:
            choice = int(input(inputText + '{}. ADD NEW CLAN \n0. GO BACK\n'.format(noOfTags+1) + 'Your Choice: '))
            for i in range(len(clanTagList)):
                if choice == i+1:
                    clanManager(clanTagList[i][0])
            if choice == len(clanTagList)+1:
                newClanTag = input('Insert clan tag: #')
                reqcode = retrieve_clanOnly(newClanTag)[1]
                if reqcode == 200:
                    c.execute("INSERT INTO clanTags(tag) VALUES(?)", [newClanTag])
                    conn.commit()
                else:
                    print(f'Invalid. Error code: {reqcode}\n')
            elif choice == 0:
                return
        except ValueError:
            print('Invalid Choice. Try again.\n')

def clanManager(clanTag):
	while True:
		keysToCall_mD = [	'lastSeen',
							'lvl',
							# 'tag',
							'trophy',
							'donate', 
							#'received', 
							#'arena', 
							'fame', 
							'rp', 
							'fame+rp', 
							'rank']
		# keysToCall_mD.extend(['ag', 'dg', 'rrg', 'ovg']) # CWG REVIEW 
		# keysToCall_mD.extend(['review(bool)']) # RB REVIEW
		# keysToCall_mD.extend(['review']) # 30 donates only review
		keysToCall_mD.extend(['name'])

		keysToCall_rR = [	'fame',
							'rp',
							'trophy',
							'tag',
							'name']

		keysToCall_rRI = ['fame+rp', 'name']
		keysToCall_pL = [	'time',
							#'mode',
							'type',
							#'score',
							'attacker',
							'name',
							'clan',]
	# =================================================================================
		option = input(
		'\nClash Royale Leaderboards/Tools:\n'
		'  1. Clan Leaderboard\n'
		'  2. River Race Leaderboard\n'
		'  3. River Race Clans Leaderboard\n'
		'  4. Check Battle Log\n'
		'  0. Return to Main Menu\n'
		'Maintenance Purpose:\n'
		'  5. Print raw clan data dictionary\n'
		'  6. Print raw river race data dictionary\n'
		'  7. Print available keys for CLB\n'
		'  8. Print available keys for RRLB\n'
		'Your Choice: '
		)

		if option == '1':
			clanLeaderboard(keysToCall_mD, clanTag)
		elif option == '2':
			riverRaceLeaderboard(keysToCall_rR, clanTag)
		elif option == '3':
			riverRaceClanMembers(keysToCall_rRI, clanTag)
		elif option == '4':
			playerLog(keysToCall_pL, clanTag)
		elif option == '5':
			print(retrieve_clanData(clanTag)[0])
		elif option == '6':
			print(retrieve_currentRiverRace(clanTag)[0])
		elif option == '7':
			printAvailableKeys(getCLBdata(clanTag)[0])
		elif option == '8':
			printAvailableKeys(getRRLB(clanTag))
		elif option == '0':
			break

		else:
			print('Invalid. Try again.')

def main():
	while True:
		choice = input('\nCR Manager v1.0\n'
		'----------------\n'
		'1. Clan Manager\n'
		'2. Player Manager\n'
		'0. Exit\n'
		'Your choice: '
		)
		if choice == '1':
			clanManagerMenu()
		elif choice == '2':
			playerManagerMenu()
		elif choice == '0':
			exit()
		else:
			print('Invalid choice. Try again.\n')

main()
