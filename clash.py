import requests
import json

clanTag = 'L2208GR9'
key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6Ijc2YWYzMGJmLWFjYzgtNGE0Ny1hZmU2LWIwZjE0NzY2ZWNlYyIsImlhdCI6MTU5MjMxMzY0OSwic3ViIjoiZGV2ZWxvcGVyL2JjNzVkYTRmLTEyMGItOWU3Ny0xMTA0LWM0YmQxMDllMDc5OCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTI4LjEyOC4xMjgiXSwidHlwZSI6ImNsaWVudCJ9XX0.czFtTMv7pqaziRUiivFYyXdvwAvPQNpI7w9tNvrExj0cvzYFl20GHtdLL3LiVKM-ZUFs1wTXeSqfjXgygssT2g'
base_url = "https://proxy.royaleapi.dev/v1"
endp1 = f"/clans/%23{clanTag}/members"
endp2 = f"/clans/%23{clanTag}/currentriverrace"
header = {"Authorization": "Bearer %s" %key}

def combine_membersData(dict_membersData, dict_currentRiverRace):
	list_combinedMembersData = []
	for dict_member in dict_membersData['items']:
		for dict_participant in dict_currentRiverRace['clan']['participants']:
			if dict_member['tag'] == dict_participant['tag']:
				dict_member_new = dict_member
				for k, v in dict_participant.items():
					dict_member_new[k] = v
					list_combinedMembersData.append(dict_member_new)
	return list_combinedMembersData

def retrieve_membersData():
	json_membersData = requests.get(base_url+endp1, headers=header)
	return json_membersData.json()

def retrieve_currentRiverRace():
	json_currentRiverRace = requests.get(base_url+endp2, headers=header)
	return json_currentRiverRace.json()

