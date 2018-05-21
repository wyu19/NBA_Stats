
import requests
import re
from bs4 import BeautifulSoup
from html.parser import HTMLParser

# TAG_RE = re.compile('r<[^>]+>a')
#
# def remove_tags(text):
#     return TAG_RE.sub('', text)


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
    user_agent = 'python-requests/4.82 (Compatible; wen; mailto: yuw321@gmail.com)'
    if kwargs:
        user_agent = 'python-request/4.8.2 (Compatible, {}, mailto:{})'.format(kwargs['name'], kwargs['email'])

    response = requests.get(link, headers={'User-Agent': user_agent}, timeout=10)

    return response

url_dict = {}

cont = True
while cont:
    url = input("Enter a url to see if they are scrapable: ")
    req = connect(url, name="test_name", email="test_mail")
    html = req.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    print(title)
    td = soup.find_all('td')

    # td = strip_tags(str(td))
    # print(td)

    notag_soup = BeautifulSoup(str(td), "html.parser")
    print(notag_soup.get_text())

    # a = remove_tags(str(a))
    # print(a)

    #http://www.espn.com/nba/team/roster/_/name/gs/index  scrape this!
    url_dict.update({url: req})  #remove all tags regular expression is not working

    if req.status_code != 200:
        if req.status_code == 404:
            print("robots.txt not found for {}").format(str(url))
        else:
            print("There has been a error with scraping this site {}").format(str(url))

    add_more = input("Do you want to continue? Enter yes or no: ")
    if add_more == 'no':
        break;

print(url_dict)