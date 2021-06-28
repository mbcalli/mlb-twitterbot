#!/usr/bin/env python3
import sys
import time
import datetime
from datetime import datetime
import csv

import statsapi
from twython import Twython
from twython import TwythonError
import mlb_grapher
import config


# Reads in which team to analyze from the Cron job;  example: 'atl'
team_code = sys.argv[1]

# Gets the team id from the team_code
team_lookup = statsapi.lookup_team(team_code)
for team in team_lookup:
    teamCode = team['fileCode']
    if teamCode == team_code:
        team_id = team['id']

# Filepath to the team info which stores team name, colors, etc.
mlb_team_info_filepath = '/home/pi/twitterbot/mlb_team_info.csv'

# Get team info for each team -- easier than looking for specific team
mlb_team_info = []
with open(mlb_team_info_filepath, mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    for row in reader:
        mlb_team_info.append(list(row))

# Get the schedule for the team on a given date
def schedule_on_date(team_id, date):
    sch = statsapi.schedule(team=team_id, start_date=date, end_date=date)
    return sch

# Get the home and away team win probability at the moment the function is called
def get_win_probs(game_id):
    data = statsapi.get('game_contextMetrics', {'gamePk': game_id})
    win_prob = round(data['homeWinProbability'], 2) # Win probability of the home team

    return win_prob, 100-win_prob


# Get the win probability string (which is a formatted string, ready to be posted to twitter)
def get_win_probability_string(game_id, home_name, away_name):
    home_win_prob, away_win_prob = get_win_probs(game_id)
    if home_win_prob >= 50:
        return home_name + ' have a ' + str(home_win_prob) + '% chance of winning.'
    else:
        return away_name + ' have a ' + str(away_win_prob) + '% chance of winning.'   

# Get the formatted inning (ready to be tweeted)
def format_inning(current_inning, inning_state):
    inning_formats = {
        1: '1st',
        2: '2nd',
        3: '3rd'
    }
    if current_inning in inning_formats:
        current_inning = inning_formats[current_inning]
    else:
        current_inning = str(current_inning) + 'th'
    inning_state = inning_state
    return inning_state + ' of the ' + current_inning


# Get the formatted score (ready to be tweeted)
def format_score(home_name, away_name, home_score, away_score):
    return home_name + '   ' + str(home_score) + '\nvs.\n' + away_name + '   ' + str(away_score)

# Start the Twython api
def twython_api_start():
    return Twython(config.CONSUMER_KEY, config.CONSUMER_SECRET, config.ACCESS_KEY, config.ACCESS_SECRET)


# Use Twython to update twitter status
def twython_update_status(api, text):
    api.update_status(status=text)

# Update twitter status with formatted strings
def update_status(text, game_id, formatted_inning):
    api = twython_api_start()
    try:
        twython_update_status(api, text)
        print(team_code + ' --> ' + game_time)
    except TwythonError:
        print('Tweet already posted: ' + text)
        
# Writes the win probability to a csv file so that historical info can be retrieved by mlb_grapher.py
def write_win_probability(win_prob_filepath, game_id, time, home_name, away_name, inning_state):
    home_win_prob, away_win_prob = get_win_probs(game_id)
    with open(win_prob_filepath, mode='a') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([time, home_win_prob, away_win_prob, home_name, away_name, inning_state])

# Writes the win probability to a csv file so that historical info can be retrieved by mlb_grapher.py
def write_win_prob_end_of_game(win_prob_filepath, game_id, time, home_name, away_name, home_team_won):
    with open(win_prob_filepath, mode='a') as file:
        writer = csv.writer(file, delimiter=',')
        if home_team_won:
            writer.writerow([time, 100, 0, home_name, away_name])
        else:
            writer.writerow([time, 0, 100, home_name, away_name])

# Converts UTC time to Local time
def datetime_from_utc_to_local(utc_datetime):
    utc_datetime = datetime.strptime(utc_datetime, '%H:%M:%S')
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    est_time =  utc_datetime + offset
    return datetime.strftime(est_time, '%I:%M %p')

# Select the correct hashtags for tweet
def get_formatted_hashtags(home_name, away_name, mlb_team_info):
    home_hashtags = ''
    away_hashtags = ''
    for team in mlb_team_info:
        team_name = team[1]
        if team_name == home_name:
            home_hashtags += team[2] + ' ' + team[3]
        elif team_name == away_name:
            away_hashtags += team[2] + ' ' + team[3]
    return home_hashtags, away_hashtags

# Get the relevant info for today's game
now = datetime.now()
today = now.strftime("%m/%d/%Y")
game_time = now.strftime("%H:%M:%S")
schedule = schedule_on_date(team_id, today)

# If no game today
if len(schedule) == 0:
    pass
# If game today
else:
    # Loop through each game that team is playing today (may be double header)
    for game in schedule:

        # Get game info from api
        game_id = game['game_id']
        is_home_team = game['home_id'] == team_id
        inning_state = game['inning_state']
        current_inning = game['current_inning']
        home_name = game['home_name']
        away_name = game['away_name']
        home_score = game['home_score']
        away_score = game['away_score']

        # Determine if team is home or away team
        if is_home_team:
            my_team_name = home_name
            other_team_name = away_name
        else:
            my_team_name = away_name
            other_team_name = home_name

        # Gets hashtags for today's game
        home_hashtags, away_hashtags = get_formatted_hashtags(home_name, away_name, mlb_team_info)

        # Determine if game is currently in progress
        if game['status'] == 'In Progress':

            # Get win probability and write to csv
            win_probability_string = get_win_probability_string(game_id, home_name, away_name)
            write_win_probability('/home/pi/twitterbot/win_probs/' + str(game_id) + '.csv', game_id, game_time, home_name, away_name, inning_state)
            
            # Generate updated graph using mlb_grapher.py
            mlb_grapher.generate_graph(str(game_id))
            
            # If ballgame has just ended
            if inning_state == 'End':

                # Get info and tweak string to match end of game scenario then tweet
                formatted_inning = format_inning(current_inning, inning_state)
                formatted_score = format_score(home_name, away_name, home_score, away_score)
                text = formatted_inning + ':\n\n' + formatted_score + '\n\n' + win_probability_string + '\n\n' + '#MLB (' + str(game_id) + ')\n'  + home_hashtags + '\n' + away_hashtags
                update_status(text, game_id, formatted_inning)

        # If game is over
        elif game['status'] == 'Game Over':

            # Get info and tweak string to match end of game scenario then tweet and generate graph
            formatted_inning = 'Final'
            formatted_score = format_score(home_name, away_name, home_score, away_score)
            win_probability = get_win_probability_string(game_id, home_name, away_name)
            text = formatted_inning + ':\n\n' + formatted_score + '\n\n' + '#MLB (' + str(game_id) + ')\n' + home_hashtags + '\n' + away_hashtags
            update_status(text, game_id, formatted_inning)
            home_team_won = home_score > away_score
            write_win_prob_end_of_game('/home/pi/twitterbot/win_probs/' + str(game_id) + '.csv', game_id, game_time, home_name, away_name, home_team_won)
            mlb_grapher.generate_graph(str(game_id))

        # If game hasn't started
        elif game['status'] == 'Pre-Game':

            # Get info and tweak string to match pre game scenario then tweet
            game_datetime = game['game_datetime']
            game_datetime = game_datetime[11:19]
            game_time = datetime_from_utc_to_local(game_datetime)
            formatted_inning = 'Pre-Game'
            text = home_name + ' take on the ' + away_name + ' today at ' + game_time + '.' + '\n\n' + '#MLB (' + str(game_id) + ')\n' + home_hashtags + '\n' + away_hashtags
            update_status(text, game_id, formatted_inning)
            

