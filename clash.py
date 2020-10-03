import sqlite3
import requests
import json
import dateutil.parser as dp
import datetime
import pytz
import math

# ================================================================================
# RETRIEVE FUNCTIONS
# ================================================================================
def api_req(endpoint, **kwargs):
    '''
    Accepts endpoint, (params)
    Returns dictionary object and status code
    '''
    endp = {
            "clansearch"    : "/clans",
            "clan"          : "/clans/%23{}".format(kwargs.get('clantag', None)),
            "clanmembers"   : "/clans/%23{}/members".format(kwargs.get('clantag', None)),
            "riverrace"     : "/clans/%23{}/currentriverrace".format(kwargs.get('clantag', None)),
            "playerlog"     : "/players/%23{}/battlelog".format(kwargs.get('playertag', None))
    }
    key = ( 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi'
            '03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2'
            'FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI'
            '6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQx'
            'MDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL'
            '3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXS'
            'widHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20'
            'GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g')
    base_url = "https://proxy.royaleapi.dev/v1"
    header = {"Authorization": "Bearer %s" %key}
    req = requests.get(base_url+endp.get(f'{endpoint}'), headers=header, params=kwargs.get('params', None))
    return req.json(), req.status_code

# =================================================================================
# NEW ITERABLE DATA CREATION
# ================================================================================
def makeListOfdict_cLB(clanTag):
    dict_clanData, reqcode = api_req(endpoint='clanmembers', clantag=clanTag)
    dict_riverRaceData, reqcode = api_req(endpoint='riverrace', clantag=clanTag)
    memberCount = len(dict_clanData['items'])
    clanFame = dict_riverRaceData['clan'].get('fame')
    list_membersData = [] # new list to store new dictionaries
    for dict_m in dict_clanData['items']:
        dict_m_new = {}
                    # New               # Old
        dict_m_new['tag']       = dict_m.get('tag')
        dict_m_new['name']      = dict_m.get('name')
        dict_m_new['rank']      = dict_m.get('role').title()
        dict_m_new['lastSeen']  = dp.isoparse(dict_m.get('lastSeen')).astimezone(pytz.timezone('Asia/Singapore')).strftime("%d/%m %H:%M")
        dict_m_new['arena']     = dict_m['arena']['name']
        dict_m_new['trophy']    = dict_m.get('trophies')
        dict_m_new['donate']    = dict_m.get('donations')
        dict_m_new['received']  = dict_m.get('donationsReceived')
        dict_m_new['lvl']       = dict_m.get('expLevel')
        
        for dict_participant in dict_riverRaceData['clan']['participants']:
            if dict_m['tag'] == dict_participant['tag']:
                               # New                            # Old
                dict_m_new['fame']      = dict_participant.get('fame')
                dict_m_new['rp']        = dict_participant.get('repairPoints')
                dict_m_new['fame+rp']   = dict_participant.get('fame') + dict_participant.get('repairPoints')
                break
        list_membersData.append(dict_m_new)
    return list_membersData, memberCount, clanFame

def makeListOfdict_rRLB(clanTag):
    '''This block of code takes in raw dictionary of river race data
    and convert it to a list. This list is returned.'''
    
    '''KEY(S) ADDED TO RIVERRACE DATA: tag, name, fame, rp, trophy'''
    # Structure: [{},{},{}]
    dict_riverRaceData, reqcode = api_req(endpoint='riverrace', clantag=clanTag)
    list_riverRace = [] # new list to store new dictionaries
    for dict_clan in dict_riverRaceData['clans']:
        dict_clan_new = {}
                     # New                 # Old
        dict_clan_new['tag']    = dict_clan.get('tag')
        dict_clan_new['name']   = dict_clan.get('name')
        dict_clan_new['fame']   = dict_clan.get('fame')
        dict_clan_new['rp']     = dict_clan.get('repairPoints')
        dict_clan_new['trophy'] = dict_clan.get('clanScore')
        list_riverRace.append(dict_clan_new)
    return list_riverRace

def makeListOfClans_rR(clanTag):
    '''This block of code takes in raw dictionary of river race data
    and convert it to a list of dictionaries containing only info about
    clans and their war participants. This list is returned.'''

    '''KEYS(S) ADDED TO RIVERRACE INDIVIDUAL'S DATA: name, fame+rp'''
     # Structure: [[{},{}], [{},{}]]
    dict_riverRaceData, reqcode = api_req(endpoint='riverrace', clantag=clanTag)
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

def makeListOfDict_battleLog(playerTag):
    '''This block of code takes in raw dictionary of player log data
    and convert it to a list. This list is returned.'''
    
    '''KEY(S) ADDED TO battleLog DATA: type, mode, clan, name'''
    # Structure: [{},{},{}]
    list_playerLog, reqcode = api_req(endpoint='playerlog', playertag=playerTag)
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
def clanLeaderboard(clanTag):
    # Initialize variables
    e = ''
    stored_e = ''
    keysToCall = [  'lastSeen', 
                    'lvl', 
                    'trophy', 
                    # 'arena', 
                    'donate', 
                    'received', 
                    # 'fame', 
                    # 'rp', 
                    'fame+rp', 
                    'rank', 
                    # 'tag', 
                    'name']
    
    # This block generates sort message
    string_sortMsg = ''
    for i in range(len(keysToCall)):
        string_sortMsg += '{}. Sort by {}\n'.format(i+1, keysToCall[i].title())
    
    # This block is the interface
    while True:
        # Get clan data
        list_membersData, memberCount, clanFame = makeListOfdict_cLB(clanTag)
        
        # Check for sort
        if e in [str(i) for i in range(1,len(keysToCall)+1)]:
            stored_e = e
        for i in range(len(keysToCall)):
            if stored_e == str(i+1):
                list_membersData = sortListOfDict(list_membersData, keysToCall[i])
                print('Sort Completed.\n')
                break

        # Print block
        print('\nMembers: {}'.format(memberCount))
        print('Fame: {}'.format(clanFame))
        print(formatString_listOfDict(list_membersData, keysToCall))
        e = input(f"<Enter> to refresh. 'e' to return to menu. Otherwise:\n{string_sortMsg}Your Choice: ")
        if e.lower() == 'e':
            break

def riverRaceLeaderboard(clanTag):
    # Initialize variables
    keysToCall = [  'fame', 
                    'rp', 
                    'trophy', 
                    'tag', 
                    'name',]

    # This block is the interface
    while True:
        # Initialize
        clanListMessage = ''
        
        # Data retrieval
        list_riverRace = makeListOfdict_rRLB(clanTag)
        list_riverRace = sortListOfDict(list_riverRace, 'fame')
        
        # Print
        for i in range(len(list_riverRace)):
            clanListMessage += '{}. {}\n'.format(i+1, list_riverRace[i].get('name'))
        print(formatString_listOfDict(list_riverRace, keysToCall))
        e = input(
            "<Enter> to refresh. 'e' to return to menu. Otherwise:"
            f"View clan in detail:\n{clanListMessage}Your Choice: "
            )
        if e.lower() == 'e':
            break
        try:
            e = int(e)
            if e in range(1,5):
                clanLeaderboard(list_riverRace[e-1].get('tag')[1:])
                return
        except ValueError:
            pass

def playerLog(clanTag):
    # Initialize variables
    e = ''
    stored_e = ''
    clan = makeListOfdict_cLB(clanTag)[0]
    keysToCall = [  'time', 
                    'mode', 
                    'type' 
                    'score', 
                    'attacker', 
                    'name', 
                    'clan',]
    
    # This block generates sort message
    string_sortMsg = ''
    for i in range(len(keysToCall)):
        string_sortMsg += '{}. Sort by {}\n'.format(i+1, keysToCall[i].title())

    # Interface
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
            listOfGames = makeListOfDict_battleLog(playerTag)
            print(formatString_listOfDict(listOfGames, keysToCall))
            e = input("<Enter> to refresh. 'e' to return to player choice. Otherwise:\n{}Your Choice: ".format(string_sortMsg))
            
            # Check if user wants to return to menu
            if e.lower() == 'e':
                break


def clanManagerMenu():
    # SQLITE ==================================
    conn = sqlite3.connect('clanTags.db')
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE clanTags (
                                    tag text, 
                                    name text
                                    )""")
    except sqlite3.OperationalError:
        pass
    # =========================================
    
    # INTERFACE ===============================
    while True:
        c.execute('SELECT * FROM clanTags')
        clanTagList = c.fetchall()
        clanListText = ''
        for i in range(len(clanTagList)):
            clanListText += ' {}. {}\n'.format(i+1, clanTagList[i][1])
        
        choice = input('\nClan Manager\n'
                        '-----------------\n'
                        f'{clanListText}'
                        ' A. ADD NEW CLAN BY TAG\n'
                        ' B. ADD NEW CLAN BY SEARCH\n'
                        ' C. DELETE RECORD\n'
                        ' D. GO BACK\n'
                        'Your Choice: '
                        )
        try:
            int_choice = int(choice)
            if int_choice in range(1, len(clanTagList)+1):
                clanManager(clanTagList[int_choice-1][0])
            else:
                print('Invalid input.')
        
        except ValueError:
            
            if choice.upper() == 'A':
                e = input('\nInsert clan tag: #')
                dict_clanData, reqcode = api_req(endpoint='clan', clantag=e)
                
                if reqcode == 200:
                    c.execute("INSERT INTO clanTags VALUES(e, dict_clanData.get('name'))")
                    conn.commit()
                else:
                    print(f'CODE: {reqcode}')
            
            elif choice.upper() == 'B':
                e = input('\nSearch by clan name: ')
                request, reqcode = api_req(endpoint='clansearch', params={'name':f'{e}'})
                result = request.get('items')
                for i in range(len(result[:10])):
                    print('{}. {:10} {}'.format(i+1, result[i]['tag'], result[i]['name']))
                
                try:
                    e = int(input('\nSelect clan (1-10): '))
                    if e not in range(1, len(result)+1):
                        raise ValueError
                    c.execute("INSERT INTO clanTags VALUES(?,?)", [result[e-1]['tag'][1:], result[e-1]['name']])
                    conn.commit()
                except ValueError:
                    print('Invalid input.')

            elif choice.upper() == 'C':
                if len(clanTagList) != 0:
                    try:
                        e = int(input('\nClan entry to delete: '))
                        if e>0 and e <= len(clanTagList):
                            c.execute("DELETE from clanTags WHERE tag=?", (clanTagList[e-1][0],))
                            conn.commit()
                        else:
                            print('Invalid input.')
                    except ValueError:
                        print('Invalid input.')
                else: print('No clans available to delete!')
                
            
            elif choice.upper() == 'D':
                c.close()
                return

def clanManager(clanTag):
    while True:
    # =================================================================================
        option = input(
        '\nLeaderboards/Logs:\n'
        '------------------------\n'
        ' 1. Clan Leaderboard\n'
        ' 2. River Race Leaderboard\n'
        ' 3. Check Battle Log\n'
        ' 0. Return to Main Menu\n'
        'Your Choice: '
        )

        if option == '1':
            clanLeaderboard(clanTag)
        elif option == '2':
            riverRaceLeaderboard(clanTag)
        elif option == '3':
            playerLog(clanTag)
        elif option == '0':
            return

        else:
            print('Invalid. Try again.')

def main():
    while True:
        choice = input(
        '\nCR Manager v1.0\n'
        '----------------\n'
        ' 1. Clan Manager\n'
        ' 2. Player Manager\n'
        ' 0. Exit\n'
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