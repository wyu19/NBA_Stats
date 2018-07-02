import requests
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from bs4 import BeautifulSoup
from html.parser import HTMLParser

class TagStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def strip_tags(html):
    s = TagStripper()
    s.feed(html)
    return s.get_data()


def connect(link,  **kwargs):
    link = link.strip()
    user_agent = 'python-requests/4.82 (Compatible; mailto: )'
    if kwargs:
        user_agent = 'python-request/4.8.2 (Compatible, {}, mailto:{})'.format(kwargs['name'], kwargs['email'])

    response = requests.get(link, headers={'User-Agent': user_agent}, timeout=10)

    return response


def team_table(roster):
    table_title = ""

    for i in roster[:9]:
        table_title += i + "  "

    print(table_title)
    player_info = "             "

    for i, info in enumerate(roster[9:], 1):

        if i % 8 != 0:
            player_info += info + "  "

        else:
            player_info += " " + info
            print(player_info)
            player_info = "             "




def extract_info(data, skip, *break_string):
    info_list = data[0::skip]
    if 'Totals' in info_list:
        index = info_list.index('Totals')
        info_list = info_list[:index]
    return info_list

def sort_stats(stats, matr, indices, row):  #how to efficiently get the stats i want, check if its a number,

    if len(stats) == 0 or row >=15:
        return 0;

    m_index = 0
    for j, info in enumerate(stats, 0):
        if j > 16:
            break;
        if j in indices:
            matr[row][m_index] = info
            m_index += 1
    row += 1
    sort_stats(stats[16:], matr, indices, row)


# def fill_stats(matr, team_dict, stats_list):  #problem is that stats dict will have the repetition of names
#     team_dict
#
#
#   # for p in team_dict:
#   #     for i,s in zip(stats_matrix, stats_list):
#   #         team_dict[p]
#   #




def add_salaries(stats_dict, player_sal): #names arent part of the stats yet so i need to attach the stats to it
    for i in player_sal:
        for j in stats_dict:
            if i == j:           #if the players name in the stats dict matches the player name in the salary append the salary to that player.
                stats_dict[j][7] = player_sal[i]




#team_dict[teams][player][stats]
#reused variables
url_dict = {}
team_initials = ['gs', 'bos', 'atl', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'hou',
                  'ind', 'lac', 'mem', 'mia', 'mil', 'nop', 'nyk', 'okc', 'orl', 'phi', 'phx',
                 'por', 'sac', 'sas', 'tor', 'uta', 'was'
                 ]

roster_link = 'http://www.espn.com/nba/team/roster/_/name/'
stats_link = 'http://www.espn.com/nba/team/stats/_/name/'
stats_list = ["GP","Min", "PPG", "RPG", "APG", "SPG", "BPG", "Salary"]
team_dict = {}
season_type = "/seasontype/2"

#add salary to the end of all the stats list.
#accesses all the nba roster links and infos
for t, init in enumerate(team_initials, 0):
    roster_url = roster_link+init
    stat_url = stats_link+init+season_type
    roster_req = connect(roster_url, name="test", email="test_mail")
    stat_req = connect(stat_url, name="test", email="test_mail")
    stat_html = stat_req.text
    roster_html = roster_req.text

    stat_soup = BeautifulSoup(stat_html, "html.parser")        #scrape all the info from the stats link and splits the info
    stat_info = stat_soup.find_all('td')
    all_stats = strip_tags(str(stat_info)).strip('] [')
    all_stats = all_stats.split(', ')

    roster_soup = BeautifulSoup(roster_html, "html.parser")    #scrape all the info from the roster link and splits the info
    roster_info = roster_soup.find_all('td')
    roster = strip_tags(str(roster_info)).strip('] [')
    roster = roster.split(', ')

    players = extract_info(all_stats[16:], 16, 'Totals')              #sort out the players and salaries from the roster link
    salaries = extract_info(roster[16:], 8)
    player_salaries = dict(zip(players, salaries))          #need to cut off the extra stuff from after players
    print(players)


    players_dict = {p: {s: 0 for s in stats_list} for p in players}  #created the dictionary with all the players from one team
    print(players_dict)
    team_dict = {t: {p: {s: 0 for s in stats_list} for p in players} for t in team_initials}
    print(team_dict)
# i just need to fill in the rest of the stats


    url_dict.update({roster_url: roster_req})
    url_dict.update({stat_url: roster_req})

    if roster_req.status_code or stat_req.status_code != 200:
        if roster_req.status_code == 404:
            print("robots.txt not found for {}").format(str(roster_url))
        else:
            print("{} 's status code is {} and {} 's status code is {} ".format(roster_url, roster_req.status_code, stat_url, stat_req.status_code))

    add_more = input("Do you want to continue? Enter yes or no: ")
    if add_more == 'no':
        break;

print(url_dict)