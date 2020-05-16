import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_xml_data(fname):
    game_schedule = ET.parse(fname).getroot()[1]
    out = {}
    for game in game_schedule:
        out[str(game.attrib['gameKey'])] = game.attrib
    return out

def parse_json_data(fname):
    with open(fname, 'r') as f:
        game_schedule = json.load(f)['gameSchedules']
        out = {}
        for game in game_schedule:
            out[str(game['gameKey'])] = game
        return out

def load_ground_truth(data_dir):
    out = {}
    for file in os.listdir(data_dir):
        if file.endswith('json'):
            out.update(parse_json_data(data_dir + file))
        elif file.endswith('xml'):
            out.update(parse_xml_data(data_dir + file))
    return out

def load_schedule_json(fname):
    with open(fname, 'r') as f:
        data = json.load(f)
        out = {}
        for game in data['games']:
            game_data = game[1]
            out[game_data['gamekey']] = game_data
        return out

def check_correctness(ground_truth, schedule_data):
    if schedule_data['away'] != ground_truth['visitorTeamAbbr']:
        return "Incorrect Away Team"
    if schedule_data['day'] != int(ground_truth['gameDate'].split('/')[1]):
        return "Incorrect Day"
    if schedule_data['eid'] != str(ground_truth['gameId']):
        return "Incorrect Game ID"
    if schedule_data['home'] != ground_truth['homeTeamAbbr']:
        return "Incorrect Home Team"
    if schedule_data['month'] != int(ground_truth['gameDate'].split('/')[0]):
        return "Incorrect Month"
    if schedule_data['season_type'] != ground_truth['seasonType']:
        return "Incorrect Season Type"
    
    ground_truth_date = datetime.strptime(ground_truth['gameTimeEastern'], "%H:%M:%S")
    if schedule_data ['meridiem'] != None:
        schedule_date = datetime.strptime(schedule_data['time'] + "," + schedule_data['meridiem'], "%I:%M,%p")
        if schedule_date != ground_truth_date:
            schedule_date = datetime.strptime(schedule_data['time'] + "," + "PM", "%I:%M,%p") # meridiem issue
            if schedule_date != ground_truth_date:
                return "Incorrect Date"
            else:
                return "Incorrect Meridiem"
    else:
        return "Missing Meridiem"
    schedule_weekday = datetime.strptime(schedule_data['wday'], "%a")
    if schedule_weekday.weekday() != ground_truth_date.weekday():
        return "Incorrect Weekday"
    
    schedule_week = schedule_data['week']
    if schedule_data['season_type'] == 'POST': # postseason
        schedule_week += 17
        if schedule_data['week'] == 4: # super bowl
            schedule_week += 1
    if int(schedule_week) != int(ground_truth['week']):
        return "Incorrect Week"
    if int(schedule_data['year']) != int(ground_truth['season']):
        return "Incorrect Year"
    
    return "Correct"


def main():
    ground_truth = load_ground_truth("ground_truth/")
    schedule_json = load_schedule_json("schedule.json")

    regular, preseason, pro_bowl, postseason, incorrect = [], [], [], [], []

    for game_key, game in ground_truth.items():
        if game_key in schedule_json:
            schedule_game = schedule_json[game_key]
            reason = check_correctness(game, schedule_game)
            if reason != "Correct":
                incorrect.append((str(game['gameId']), reason))
        else:
            if game['seasonType'] == 'REG':
                regular.append(str(game['gameId']))
            elif game['seasonType'] == 'PRO':
                pro_bowl.append(str(game['gameId']))
            elif game['seasonType'] == 'PRE':
                preseason.append(str(game['gameId']))
            elif game['seasonType'] == 'POST':
                postseason.append(str(game['gameId']))

    print("Missing regular season games:", regular)
    print("Missing preseason games:", preseason)
    print("Missing pro bowl games:", pro_bowl)
    print("Missing postseason games:", postseason)
    print("Incorrect games:", incorrect)

if __name__ == "__main__":
    main()
