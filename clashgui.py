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

root = Tk()
root.title('Clan Manager v1')

Button(root, text='Clan Leaderboard').pack()
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
		Radiobutton(root, text=text, variable=sortBy, value=mode).pack()
	Button(root, text='Sort', command=click_sort).pack()



root.mainloop()