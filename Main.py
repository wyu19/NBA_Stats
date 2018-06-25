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

def sort_stats(stats):  #how to efficiently get the stats i want, check if its a number,
    m = [[0 for x in range(8)] for y in range(15)]
    stat_indices = [0, 2, 3, 6, 7, 8, 9]
    for i in range(0,15):
        index = 0
        for j, info in enumerate(stats, 0):
            if j >= 12:

                break;
            if j in stat_indices:     #stats will keep starting at the beginning, so i should  use
                m[i][index] = info    # recursion
                index += 1

    print(m)
    return m




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
    print(roster_info)
    team = strip_tags(str(roster_info)).strip('] [')
    team = team.split(', ')
    print(team)


    all_stats = sort_stats(team[17:])  #stats matrix
    stats_dict = create_player_keys(team[15:])
    stats_dict = create_stats_keys(stats_dict, stats_list)
    print(stats_dict)


    # players = extract_info(team[10:], 8)
    # salaries = extract_info(team[16:], 8)
    # print(players)
    # print(salaries)
    # team_table(team)





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