"""Imports"""
import argparse
import csv
import json
import re
from urllib.parse import quote
import requests
from sqlite import create_db, insert_records
from validators import validate_player_name, validate_season_year

## Backend recruitment task for Profil Software 02/2022 - by Sebastian Kołacki
## As for the pylint PEP8 issues in this file:
## I have chosen to leave these in as they are all "line too long", bar two.
## All critical issues have been resolved as far as I'm concerned.

## Team class

class Team:
    """Team class based on available API data"""
    def __init__(self, id_, abbr, city, conference, division, full_name, name):
        self.id_ = id_
        self.abbr = abbr
        self.city = city
        self.conference = conference
        self.division = division
        self.full_name = full_name
        self.name = name

## Team Manager class used to perform all operations related to the Team class

class TeamManager:
    """TeamManager class to manage all team-related methods"""
    def __init__(self):
        pass

    ## This method grabs all the teams from the API and creates objects for each
    def get_teams(self):
        """GET teams from the API endpoint"""
        teams_json = requests.get("https://www.balldontlie.io/api/v1/teams").json()
        divisions = []
        team_list = []

        for team in teams_json['data']:
            team_list.append(
                Team(
                    id_=team['id'],
                    abbr=team['abbreviation'],
                    city=team['city'],
                    conference=team['conference'],
                    division=team['division'],
                    full_name=team['full_name'],
                    name=team['name']
                    )
                )
            divisions.append(team['division'])

        team_list.sort(key=lambda x: x.division)
        divisions = set(divisions)
        print("Teams created")
        return team_list, divisions

    ## This method groups teams by their divisions and prints them out already formatted
    def grouped_teams(self):
        """grouped_teams function returns all teams grouped by division"""
        team_list, divisions = self.get_teams()
        print("Grouping teams by division...")
        for division in divisions:
            print(division)
            for team in team_list:
                if team.division == division:
                    print(f'    {team.full_name} ({team.abbr})')
                else:
                    continue

    ## This method grabs all available stats for a given season (passed from get_team_stats method)
    def get_all_stats(self, season):
        """Access the API and get all possible stats for a given season"""
        all_stats = []
        ## Grab first page
        stats_data = requests.get(f"https://www.balldontlie.io/api/v1/games/?seasons[]={season}&postseason=false&per_page=100").json()
        all_stats += stats_data['data']

        ## Loop through all the remaining pages
        print(f"Gathering records. Please be patient, there is {stats_data['meta']['total_count']} records.")

        while stats_data['meta']['next_page'] is not None and stats_data['meta']['total_pages'] != 1:
            stats_data = requests.get(f"https://www.balldontlie.io/api/v1/games/?seasons[]={season}&postseason=false&per_page=100&page={stats_data['meta']['next_page']}").json()

            all_stats += stats_data['data']

        print('Gathering records complete.')

        return all_stats

    def printer(self, output, season_games):
        """Printer method for team-stats result output"""

        if output == 'stdout':
            for entry in season_games:
                new_line='\n'
                tab = '\t'
                print(
                    f"{entry['team_name']}{new_line}"
                    f"{tab}won games as home team: {entry['won_games_as_home_team']}{new_line}"
                    f"{tab}won games as visitor team: {entry['won_games_as_visitor_team']}{new_line}"
                    f"{tab}lost games as home team: {entry['lost_games_as_home_team']}{new_line}"
                    f"{tab}lost games as visitor team: {entry['lost_games_as_visitor_team']}{new_line}"
                )

        elif output == 'csv':

            header = [
                'Team name',
                'Won games as home team',
                'Won games as visitor team',
                'Lost games as home team',
                'Lost games as visitor team'
                ]
            with open('team-stats.csv', 'w', encoding='UTF8', newline='') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"')
                writer.writerow(header)
                for team in season_games:
                    writer.writerow([f'{team["team_name"]}',
                    f'{team["won_games_as_home_team"]}',
                    f'{team["won_games_as_visitor_team"]}',
                    f'{team["lost_games_as_home_team"]}',
                    f'{team["lost_games_as_visitor_team"]}'])

            print('CSV file created.')
        elif output == 'json':
            with open('team-stats.json', 'w', encoding='UTF8') as file:
                json.dump(season_games, file, indent=4)
            print('JSON file created.')
        elif output == 'sqlite':
            create_db()
            insert_records(season_games)

    ## This method calculates stats for each team and and passes the results into the printer method
    def get_team_stats(self, season, output):
        """Gets all stats for a team"""
        all_stats = self.get_all_stats(season)
        team_list = self.get_teams()[0]
        team_list.sort(key=lambda x: x.id_)

        season_games = []

        for team in team_list:
            team_stats = {
                'team_name' : 'team_name',
                'won_games_as_home_team' : 0,
                'won_games_as_visitor_team' : 0,
                'lost_games_as_home_team' : 0,
                'lost_games_as_visitor_team' : 0,
            }
            team_stats['team_name'] = team.city + ' ' + team.name + ' ' + '('+team.abbr+')'

            for entry in all_stats:
                if entry['home_team']['id'] == team.id_ and entry['home_team_score'] > entry['visitor_team_score']:
                    team_stats['won_games_as_home_team'] += 1
                elif entry['home_team']['id'] == team.id_ and entry['home_team_score'] < entry['visitor_team_score']:
                    team_stats['lost_games_as_home_team'] += 1
                elif entry['visitor_team']['id'] == team.id_ and entry['home_team_score'] < entry['visitor_team_score']:
                    team_stats['won_games_as_visitor_team'] += 1
                elif entry['visitor_team']['id'] == team.id_ and entry['home_team_score'] > entry['visitor_team_score']:
                    team_stats['lost_games_as_visitor_team'] += 1

            team_stats_copy = team_stats.copy()
            season_games.append(team_stats_copy)

        self.printer(output, season_games)
        return season_games


## Player class

class Player:
    """Player clased based on available API data"""
    def __init__(self, id_, first_name, height_feet, height_inches,\
        last_name, position, team, weight_pounds):
        self.id_ = id_
        self.first_name = first_name
        self.height_feet = height_feet
        self.height_inches = height_inches
        self.last_name = last_name
        self.position = position
        self.team = team
        self.weight_pounds = weight_pounds

    ## height method calculates player's height in metric system and returns it
    def height(self):
        """Return player's height in metric system"""
        if self.height_inches is None and self.height_feet is None:
            height = "Not found"
            return height
        else:
            height = float("{:.2f}".format(((self.height_feet * 12) + self.height_inches) * 0.0254))
            return height

    ## weight method calculates player's weight in metric system and returns it
    def weight(self):
        """Return player's weight in kilograms"""
        if self.weight_pounds is None:
            weight = "Not found"
            return weight
        else:
            weight = float("{:.2f}".format(self.weight_pounds/2.2046))
            return weight


## Player Manager class that handles all operations related to the Player class
class PlayerManager:
    """PlayerManager class to manage all player-related methods"""
    def __init__(self):
        pass

    ## This method sends a query to the API based on user input
    def get_player(self, name):

        """Get player from API endpoint based on name query"""
        ## Using regex to replace single quote mark in names with nothing
        ## Example - player "De'Marcus" - his record in the api is "demarcus"
        ## No need to validate characters other than latin letters, since the API doesn't use any
        ## We are also using quote from urllib library to handle url encoding ie. space to %20
        player_name = re.sub("'","",name)
        players_found = []
        total_players_json = []
        player_json = requests.get(f"https://www.balldontlie.io/api/v1/players/?search={quote(player_name)}&per_page=100").json()
        total_players_json = player_json['data']

        ## This loops through all pages until last page and adds the data to data list

        print('Gathering records.')
        while player_json['meta']['next_page'] is not None and player_json['meta']['total_pages'] != 1:
            player_json = requests.get(f"https://www.balldontlie.io/api/v1/players/?search={player_name}&per_page=100&page={player_json['meta']['next_page']}").json()

            total_players_json += player_json['data']

        print('Gathering records complete - formatting data.')

        ## Prune names mismatched by the API (not exact matches in last name for some reason?)
        pruned_players_found = []
        for entry in total_players_json:
            if entry['first_name'].lower() == player_name.casefold() or player_name.casefold() in entry['last_name'].casefold():
                pruned_players_found.append(entry)

        ## This for loop creates player objects for each player found matching the query

        for player in pruned_players_found:
            players_found.append(
                Player(
                    id_=player['id'],
                    first_name=player['first_name'],
                    height_feet=player['height_feet'],
                    height_inches=player['height_inches'],
                    last_name=player['last_name'],
                    position=player['position'],
                    team=player['team'],
                    weight_pounds=player['weight_pounds'],
                    )
                )
        print(f'Players found:{len(players_found)}')
        return players_found

    ## This method finds the tallest player amongst players found, who have their height on record
    def find_tallest(self, players_found):
        """Sorts players matching the query by height and returns the highest"""
        player_list = []
        for player in players_found:
            if Player.height(player) == 'Not found':
                pass
            else:
                player_list.append(player)

        if len(player_list) == 0:
            print("The tallest player: Not found")
        else:
            output_list = sorted(player_list, key=lambda x: x.height(), reverse=True)
            print(f'The tallest player: {output_list[0].first_name} {output_list[0].last_name} {output_list[0].height()} meters')

    ## This method finds the heaviest player amongst players found, who have their weight on record
    def find_heaviest(self, players_found):
        """Sorts players matching the query by weight and returns the heaviest"""
        player_list = []
        for player in players_found:
            if Player.weight(player) == 'Not found':
                pass
            else:
                player_list.append(player)
        if len(player_list) == 0:
            print("The heaviest player: Not found")
        else:
            output_list = sorted(player_list, key=lambda x: x.height(), reverse=True)
            print(f'The heaviest player: {output_list[0].first_name} {output_list[0].last_name} {output_list[0].weight()} kilograms')

    ## This method is directly called by the command line and calls all other necessary methods as well as passing the name parameter
    def player_stats(self, name):
        """This function collects all the data for queried player"""
        players_found = self.get_player(name)
        self.find_tallest(players_found)
        self.find_heaviest(players_found)


if __name__ == '__main__':

    print("Script started.")

    ## Create instances of class managers
    pm = PlayerManager()
    tm = TeamManager()

    ## Create the parser and it's values
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='command', choices=['grouped-teams','player-stats','team-stats'])
    parser.add_argument('-n', '--name', help='Provide a name for the query')
    parser.add_argument('-s', '--season', help='Provide the season year for the query, range accepted ', type=int)
    parser.add_argument('-o', '--output', choices=['csv','json','sqlite','stdout'], nargs='?', default='stdout', type=str)

    args = parser.parse_args()

    ## Handle parsing
    if args.command == 'grouped-teams':
        print(f'function called:{args.command}')
        tm.grouped_teams()
    elif args.command == 'player-stats':
        if args.name is None:
            print("--name is a required parameter for player-stats, please provide one")
        else:
            if validate_player_name(args.name) is True:
                print(f'function called:{args.command}, parameters passed: {args.name}')
                pm.player_stats(args.name)
            else:
                error = validate_player_name(args.name)
                print(error)
    elif args.command == 'team-stats':
        if args.season is None:
            print("--season is a required parameter for team-stats, please provide one")
        elif args.output is None:
            print("--output cannot be empty, please provide one or ommit --output")
        else:
            if validate_season_year(args.season) is True:
                print(f'function called:{args.command}, parameters passed: season: {args.season}, output: {args.output}')
                tm.get_team_stats(args.season, args.output)
            else:
                error = validate_season_year(args.season)
                print(error)
    else:
        print("Unknown command, please refer to help(-h or --help) or the README.")
