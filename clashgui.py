import requests
import json
import dateutil.parser as dp
import datetime
import pytz
import math
from tkinter import *

# Settings for API ================================================================
clanTag = 'L2208GR9'
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQxMDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXSwidHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g'
base_url = "https://proxy.royaleapi.dev/v1"
endp1 = f"/clans/%23{clanTag}/members"
endp2 = f"/clans/%23{clanTag}/currentriverrace"
header = {"Authorization": "Bearer %s" %key}
# =================================================================================

def retrieve_clanData():
	'''This block of code retrieves clan members data and return it as
	a dictionary.'''
	endp = f"/clans/%23{clanTag}/members"
	dict_clanData = requests.get(base_url+endp, headers=header).json()
	return dict_clanData

def retrieve_currentRiverRace():
	'''This block of code retrieves river race data and return it as
	a dictionary.'''
	endp = f"/clans/%23{clanTag}/currentriverrace"
	dict_riverRaceData = requests.get(base_url+endp, headers=header).json()
	return dict_riverRaceData

def makeListOfdict_cLB(dict_clanData, dict_riverRaceData):
	'''This block of code takes in raw dictionary of clan members and
	river race data and convert it to a list. This list contains consolidated
	members data in a dictionary object. This list is returned.'''
	
	'''KEY(S) ADDED TO CLAN DATA: 	tag, name, rank, lastSeen, arena, trophy, donate,
									received, lvl, fame, rp, fame+rp'''

	list_membersData = []
	for dict_m in dict_clanData['items']:
		dict_m_new = {}
					# New 				# Old
		dict_m_new['tag']		= dict_m['tag']
		dict_m_new['name'] 		= dict_m['name']
		dict_m_new['rank'] 		= dict_m['role'].title()
		dict_m_new['lastSeen'] 	= dp.isoparse(dict_m['lastSeen']).astimezone(pytz.timezone('Asia/Singapore')).strftime("%H:%M %d/%m")
		dict_m_new['arena'] 	= dict_m['arena']['name']
		dict_m_new['trophy'] 	= dict_m['trophies']
		dict_m_new['donate'] 	= dict_m['donations']
		dict_m_new['received'] 	= dict_m['donationsReceived']
		dict_m_new['lvl'] 		= dict_m['expLevel']
		
		for dict_participant in dict_riverRaceData['clan']['participants']:
			if dict_m['tag'] == dict_participant['tag']:
							   # New 							# Old
				dict_m_new['fame'] 		= dict_participant.get('fame')
				dict_m_new['rp'] 		= dict_participant.get('repairPoints')
				dict_m_new['fame+rp'] 	= dict_participant.get('fame') + dict_participant.get('repairPoints')
				break
		list_membersData.append(dict_m_new)
	return list_membersData

def formatString_listOfDict(top, listOfDict, keys_to_call):
	'''This block of code takes in a list of dictionaries object and
	a list of string objects which are keys to be called to become
	the headers of the table. The list is converted into a formatted
	string that resembles a table. This string is returned.'''
	
	dict_sizes = {} # dictionary to store no. of spaces allocated for each key for string formatting
	response = '\n{:>3}| '.format('S/N') # initialize string and add first header
	freeSpace = 3 # this is the additional spaces allocated for each key for string formatting
	# This loop is to set up the header and append spaces allocated for each key into dict_sizes
	for key in keys_to_call:
		max_value_size = max([len(str(e[key])) for e in listOfDict if key in e.keys()]) # get size of largest value
		if max_value_size < len(key): # if size of largest value in dictionary is shorter than key then use key instead
			max_value_size = len(key)
		dict_sizes[key] = max_value_size + freeSpace
		response += '{v:<{size}}'.format(v=key.title(), size=dict_sizes[key])

	Label(top, text=response).pack(anchor=W)
	Label(top, text='\n{:-<{size}}\n'.format('', size=len(response))).pack(anchor=W)
	
	# This loop is to set up the main body of the table, i.e. the members data
	for i in range(len(listOfDict)):
		string_temp = ''
		for key in keys_to_call:
			if key in listOfDict[i].keys():
				string_temp += '{v:<{size}}'.format(v=listOfDict[i][key], size=dict_sizes[key])
			else:
				string_temp += '{:<{size}}'.format('n.a.', size=dict_sizes[key])		
		Label(top, text='{:>3}| {}\n'.format(str(i+1), string_temp)).pack(anchor=W)

def clanLeaderBoard():
	top = Toplevel()
	keysToCall_mD = ['lastSeen', 
					 'lvl',
					 'trophy',
					 'donate', 
					 'received', 
					 'arena', 
					 'fame+rp', 
					 'rank']
	list_membersData = makeListOfdict_cLB(retrieve_clanData(), retrieve_currentRiverRace())
	response = formatString_listOfDict(top, list_membersData, keysToCall_mD)
root = Tk()
root.title('Clan Manager v1')

Button(root, text='Clan Leaderboard', command=clanLeaderBoard).pack()
Button(root, text='Riverrace Leaderboard').pack()
Button(root, text='Exit', command=root.quit).pack()





def page_sort():
	def click_sort():
		label_sortBy = Label(root, text='Sorted By: {}'.format(sortBy.get())).pack()
	sortBy = StringVar()
	sortBy.set('trophy')
	MODES = [
		('Trophies', 'trophy'),
		('Donations', 'donate'),
		('Fame + Repair Points', 'fame+rp'),
		('Level', 'lvl')
	]
	for text, mode in MODES:
		Radiobutton(root, text=text, variable=sortBy, value=mode).pack(anchor=W)
	Button(root, text='Sort', command=click_sort).pack()



root.mainloop()