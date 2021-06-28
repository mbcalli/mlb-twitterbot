#!/usr/bin/env python3
import statsapi
from datetime import datetime
from twython import Twython


now = datetime.now()
today = now.strftime("%m/%d/%Y")

def get_standings_string(division):
    standings = statsapi.standings(division=division, date=today)
    standings = standings.splitlines()
    division_string = standings.pop(0)
    standings.pop(0)
    standings.pop()
    overall_output = division_string + ' Standings for ' + today + ':\n\n'
    for i, row in enumerate(standings):
        row = row.split(' ')
        row = [i for i in row if i]
        team_name = [x for x in row if not any(c.isdigit() for c in x)]
        team_name = [x for x in team_name if x != '-']
        numbers = list(set(row) - set(team_name))
        output_str = str(i+1) + ': '
        for word in team_name:
            output_str += word + ' '
        overall_output += output_str + '\n'
    return overall_output

def twython_api_start():
    CONSUMER_KEY = 'aORBSm8PmzdMuOZq0OgfHtIkb'
    CONSUMER_SECRET = 'ufs3qTzjisFkcP2zAYPIj0tkBEe12ASL3hibRfYksEzK4ACCm2'
    ACCESS_KEY = '1241197160173056000-KK7tvBydESxkWlw84aHmQoTb7Ytd11'
    ACCESS_SECRET = 'QPHGXoHBGe36YBVfhvAvA912GTa3ZDzTyyl68mDLQPfUu'

    return Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

def twython_update_status(api, text):
    api.update_status(status=text)

text = get_standings_string('nle')

api = twython_api_start()
twython_update_status(api, text)

print('mlb standings posted --> ' + today)

