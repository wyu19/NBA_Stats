import requests
from bs4 import BeautifulSoup
from html.parser import HTMLParser

# maybe make it so we can see how much pts, asst, and rebounds each player gets on avg for every team.
# then write a script to automatically put in all the teams in.
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


url_dict = {}
cont = True
while cont:
    url = input("Enter a url to see if they are scrapable: ")
    req = connect(url, name="test_name", email="test_mail")
    html = req.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    print("\n"+ title + "\n")
    roster_info = soup.find_all('td')
    team = strip_tags(str(roster_info)).strip('] [')
    team = team.split(', ')
    team_table(team)



    #http://www.espn.com/nba/team/roster/_/name/gs/index  scrape this!
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