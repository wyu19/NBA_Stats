import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebPage #lets us load the page and act like a browser
import urllib.request
import requests
import re
import bs4 as bs
from bs4 import BeautifulSoup

class Client(QWebPage):

    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self.on_page_load) #probably the error
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def on_page_load(self):
        self.app.quit()

url = 'http://www.espn.com/nba/statistics'
client_response = Client(url)
source = client_response.mainFrame().toHtml()
soup = bs.BeautifulSoup(source, 'html.parser')
js_test = soup.find_all('td')
print(js_test)

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)




def connect(link,  **kwargs):
    link = link.strip()
    user_agent = 'python-requests/4.82 (Compatible; wen; mailto: yuw321@gmail.com)'
    if kwargs:
        user_agent = 'python-request/4.8.2 (Compatible, {}, mailto:{})'.format(kwargs['name'], kwargs['email'])

    response = requests.get(link, headers={'User-Agent': user_agent}, timeout=10)

    return response


url_dict = {}
# url_main = input("Enter the url you want to scrape and then enter a space and enter to submit: ")
# req = connect(url_main,  name="fake name", email="yuw321@gmail.com")
# html = req.text
#
# bs = BeautifulSoup(html, "html.parser")
# titles = bs.find_all(attrs={'listingsignupbar__title'})
# titles = str(titles)
# titles = remove_tags(titles)
# print(titles)
# url_dict.update({url_main: req})
# print(url_dict)

cont = True
while cont:
    url = input("Enter a url to see if they are scrapable: ")
    req = connect(url, name="test_name", email="test_mail")
    html = req.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    print(title)

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