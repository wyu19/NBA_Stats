import requests
import pprint
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


def get_players(roster):   #extracts all the players name from the list of info from the roster
    players_name = []
    pname = 0;
    for i, names in enumerate(roster, 1):
        if i == 1 or i == 9:
            players_name.append(names)
        elif pname == 7:
            players_name.append(names)
            pname = 0;
        elif i > 9:
            pname += 1

    return players_name

def get_salary(roster):  #starts at index 16
    salaries = []
    for i, salary in enumerate(roster, 0):
        if i == 0 or i % 8 == 0:
            salaries.append(salary)
    return salaries







#team_dict[teams][player][stats]
#reused variables
url_dict = {}
team_initials = ['gs', 'bos', 'atl', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'hou',
                  'ind', 'lac', 'mem', 'mia', 'mil', 'nop', 'nyk', 'okc', 'orl', 'phi', 'phx',
                 'por', 'sac', 'sas', 'tor', 'uta', 'was'
                 ]
roster_link = 'http://www.espn.com/nba/team/roster/_/name/'
stats_link = 'http://www.espn.com/nba/team/stats/_/name/'
stats_list = ["Pts","Ast","Mins","Rebs","Stls","Blks","Salary"]
stats = {key: None for key in stats_list }
team_dict = Vividict()



# #accesses all the nba roster links and infos
# for init in team_initials:
#     roster_url = roster_link+init
#     stat_url = stats_link+init
#     roster_req = connect(roster_url, name="test", email="test_mail")
#     stat_req = connect(stat_url, name="test", email="test_mail")
#     stat_html = stat_req.text
#     roster_html = roster_req.text
#     stat_soup = BeautifulSoup(stat_html, "html.parser")
#     roster_soup = BeautifulSoup(roster_html, "html.parser")

cont = True
while cont:
    url = input("Enter a url to see if they are scrapable: ")
    req = connect(url, name="test_name", email="test_mail")
    html = req.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    print("\n" + title + "\n")
    roster_info = soup.find_all('td')
    team = strip_tags(str(roster_info)).strip('] [')
    team = team.split(', ')
    players = get_players(team[10:])
    salaries = get_salary(team[16:])
    print(team)
    print(players)
    print(salaries)
    team_table(team)





    url_dict.update({url: req})

    if req.status_code != 200:
        if req.status_code == 404:
            print("robots.txt not found for {}").format(str(url))
        else:
            print("There has been a error with scraping this site {}").format(str(url))

    add_more = input("Do you want to continue? Enter yes or no: ")
    if add_more == 'no':
        break;

print(url_dict)