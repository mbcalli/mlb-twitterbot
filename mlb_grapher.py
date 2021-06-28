import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import matplotlib.dates as md
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import sys

game_id_input = sys.argv[1]


def generate_graph(game_id):
    print('generating graph for ' + game_id)
    data_filepath = '/home/pi/twitterbot/win_probs/' + game_id + '.csv'
    team_info_filepath = '/home/pi/twitterbot/mlb_team_info.csv'

    with open(data_filepath, encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=',')
        data = list(reader)

    with open(team_info_filepath, encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=',')
        team_info = list(reader)

    times = [datetime.strptime(row[0], "%H:%M:%S") for row in data]
    print(times)
    home_prob = [float(row[1]) for row in data]
    away_prob = [float(row[2]) for row in data]
    home_name = data[0][3]
    away_name = data[0][4]

    inning_states = [row[5].lower() for row in data]

    bottom_indicies = [i for i, x in enumerate(inning_states) if x == 'bottom']

    bottom_boundaries = []

    for i in range(len(bottom_indicies)):
        if i == 0:
            bottom_boundaries.append(bottom_indicies[i])
        elif bottom_indicies[i] - bottom_indicies[i-1] > 1:
            bottom_boundaries.append(bottom_indicies[i-1])
            bottom_boundaries.append(bottom_indicies[i])
        elif i == len(bottom_indicies)-1:
            bottom_boundaries.append(bottom_indicies[i])

    team_name = [row[1] for row in team_info]
    team_color = [row[4] for row in team_info]

    try:
        home_index = team_name.index(home_name)
        home_color = team_color[home_index]
    except:
        home_color = '#000000'
    
    try:
        away_index = team_name.index(away_name)
        away_color = team_color[away_index]
    except:
        away_color = '#000000'

    fig = plt.figure()
    plt.rcParams.update({'font.size': 24})
    home_plot, = plt.plot(times, home_prob, label=home_name + ' (home)', color=home_color, linewidth=6.0)
    away_plot, = plt.plot(times, away_prob, label=away_name + ' (away)', color=away_color, linewidth=6.0)
    plt.legend(loc='upper left')
    plt.ylabel('Win Probability (%)')
    plt.xlabel('Time')
    plt.title('Win Probability')
    ax=plt.gca()
    xfmt = md.DateFormatter('%I:%M %p')
    ax.xaxis.set_major_formatter(xfmt)
    print(bottom_boundaries)
    for i in range(0, len(bottom_boundaries), 2):
        plt.axvspan(times[bottom_boundaries[i]], times[bottom_boundaries[i+1]], color=(0.9, 0.9, 0.9, 0.8), label='Bottom')
        plt.axvline(times[bottom_boundaries[i+1]], color='k', linewidth=3.0)
    fig.set_size_inches(24, 14)

    gray_patch = mpatches.Patch(facecolor=(0.9, 0.9, 0.9, 0.8), label='Bottom of Inning (' + home_name.split(' ')[-1] + ' bat)', edgecolor='k')
    white_patch = mpatches.Patch(facecolor='w', label='Top of Inning (' + away_name.split(' ')[-1] + ' bat)', edgecolor='k')
    plt.legend(handles=[home_plot, away_plot, white_patch, gray_patch], loc='upper left')

    plt.savefig('/home/pi/twitterbot/graphs/' + game_id + '.png', dpi=100)
    print('graph generated')


#generate_graph(game_id_input)
