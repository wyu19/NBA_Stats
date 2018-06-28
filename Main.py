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


def extract_info(roster, skip):   #gives the 1st and 8th element  of the input list
    info_list = roster[0::skip]
    return info_list


def create_player_keys(roster):
    d = Vividict()
    player_names = extract_info(roster, 15)
    for i in player_names:
        if i == ("Totals"):   #total is left after cutting off the strings but not sure if i should do the if statement or just have an constant number
            print(d)
            return d
        else:
            d[i]
    print(d)
    return d

def create_stats_keys(dict, stats):
    for i in dict:
        for j in stats:
            dict[i][j]
    return dict

def sort_stats(stats, matr, indices, row):  #how to efficiently get the stats i want, check if its a number,

    if len(stats) == 0 or row >=15:
        return 0;

    m_index = 0
    for j, info in enumerate(stats, 0):
        if j > 15:
            break;
        if j in indices:
            matr[row][m_index] = info
            m_index += 1
    row += 1
    sort_stats(stats[15:], matr, indices, row)


def add_salaries(matr, player_sal): #names arent part of the stats yet so i need to attach the stats to it
    for i in player_sal:
        for k, j in enumerate(matr,0):
            if i == j:
                matr[k][len(matr)] = j.values()


#team_dict[teams][player][stats]
#reused variables
url_dict = {}
# team_initials = ['gs', 'bos', 'atl', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'hou',
#                   'ind', 'lac', 'mem', 'mia', 'mil', 'nop', 'nyk', 'okc', 'orl', 'phi', 'phx',
#                  'por', 'sac', 'sas', 'tor', 'uta', 'was'
#                  ]
team_initials = ['gs']
roster_link = 'http://www.espn.com/nba/team/roster/_/name/'
stats_link = 'http://www.espn.com/nba/team/stats/_/name/'
stats_list = ["GP","Min", "PPG", "RPG", "APG", "SPG", "BPG", "Salary"]
team_dict = Vividict()


#add salary to the end of all the stats list.
#accesses all the nba roster links and infos
for init in team_initials:
    roster_url = roster_link+init
    stat_url = stats_link+init
    roster_req = connect(roster_url, name="test", email="test_mail")
    stat_req = connect(stat_url, name="test", email="test_mail")
    stat_html = stat_req.text
    roster_html = roster_req.text

    stat_soup = BeautifulSoup(stat_html, "html.parser")        #scrape all the info from the stats link and splits the info
    stat_info = stat_soup.find_all('td')
    all_stats = strip_tags(str(stat_info)).strip('] [')
    all_stats = all_stats.split(', ')
    print("stat:")
    print(all_stats)

    roster_soup = BeautifulSoup(roster_html, "html.parser")    #scrape all the info from the roster link and splits the info
    roster_info = roster_soup.find_all('td')
    roster = strip_tags(str(roster_info)).strip('] [')
    roster = roster.split(', ')
    print("roster")
    print(roster)

    players = extract_info(roster[10:], 8)              #sort out the players and salaries from the roster link
    salaries = extract_info(roster[16:], 8)
    player_salaries = dict(zip(players, salaries))
    print("player_salaries: {}".format(player_salaries))
    team_table(roster)

    stats_matrix = [[None for x in range(8)] for y in range(15)]    # begin building the stats matrix
    stat_indices = [0, 2, 3, 6, 7, 8, 9]
    row = 0
    sort_stats(all_stats[17:], stats_matrix, stat_indices, row)
    print(stats_matrix)
    add_salaries(stats_matrix, player_salaries)
    print("added salaries ------------")
    print(stats_matrix)
    stats_dict = create_player_keys(all_stats[15:])
    stats_dict = create_stats_keys(stats_dict, stats_list)
    print(stats_dict)


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