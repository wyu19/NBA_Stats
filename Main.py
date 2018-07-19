import requests
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
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


def sort_allstats(stats, stat_indices):
    s = []
    counter = 0
    for i in stats:
        if counter == 16:
            counter = 0
        if counter in stat_indices:
            s.append(i)
        counter += 1
    return s


def add_salaries(stats_dict, player_sal): #names arent part of the stats yet so i need to attach the stats to it
    for i in player_sal:
        for j in stats_dict:
            if i == j:           #if the players name in the stats dict matches the player name in the salary append the salary to that player.
                stats_dict[j][7] = player_sal[i]


def fill_dict(t_dict, w_stats, stats_symbols, salary):
    for p in t_dict:
        for s, i in zip(w_stats, stats_symbols):
            if i == "Salary":
                if p not in salary:              #if the player from previous season is no longer in the current roster just give them a 0
                    t_dict[p][i] = 0
                else:
                    t_dict[p][i] = salary[p]
            else:
                t_dict[p][i] = s
        w_stats = w_stats[7:]


def zero_salaries(t_dict):  #makes all the salaries that are '\xa0' = 0
    for p in t_dict:
        if t_dict[p]['Salary'] == '\xa0':
            t_dict[p]['Salary'] = 0


def create_salary_dict(roster_info):
    player = [p for i, p in enumerate(roster_info) if i% 8 == 0]
    salary = [s for i, s in enumerate(roster_info[6:]) if i% 8 == 0]
    sal_dict = dict(zip(player, salary))
    return sal_dict


def print_team(t_dict):
    for i in t_dict:
        for p in t_dict[i]:
            print("{} {}".format(p, t_dict[i][p]))


url_dict = {}
team_initials = ['gs', 'bos', 'atl', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'hou',
                  'ind', 'lac', 'mem', 'mia', 'mil', 'no', 'nyk', 'okc', 'orl', 'phi', 'phx',
                 'por', 'sac', 'sas', 'tor', 'utah', 'was'
                ]

roster_link = 'http://www.espn.com/nba/team/roster/_/name/'
stats_link = 'http://www.espn.com/nba/team/stats/_/name/'
stats_list = ["GP","Min", "PPG", "RPG", "APG", "SPG", "BPG", "Salary"]
team_dict = {}
season_type = "/seasontype/2"

for t, init in enumerate(team_initials, 0):
    print('Team {}'.format(t))
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
    player_salaries = create_salary_dict(roster[10:])        #need to cut off the extra stuff from after players

    players_dict = {p: {s: 0 for s in stats_list} for p in players}; #created the dictionary with all the players from one team
    team_dict.update({team_initials[t]: {p: {s: 0 for s in stats_list} for p in players}})
    stats_indices = [2, 4, 5, 8, 9, 10, 11]
    wanted_stats = sort_allstats(all_stats[16:], stats_indices)
    fill_dict(team_dict[team_initials[t]], wanted_stats, stats_list, player_salaries)
    zero_salaries(team_dict[team_initials[t]])
    print_team(team_dict)
    player_salaries = {p: (0 if player_salaries[p] == '\xa0' else player_salaries[p]) for p in player_salaries}   #replace all the '\xa0 with 0's

    url_dict.update({roster_url: roster_req})
    url_dict.update({stat_url: roster_req})

    if roster_req.status_code or stat_req.status_code != 200:
        if roster_req.status_code == 404:
            print("robots.txt not found for {}").format(str(roster_url))
        else:
            print("{} 's status code is {} and {} 's status code is {} ".format(roster_url, roster_req.status_code,
                                                                                stat_url, stat_req.status_code))

print(url_dict)
print(team_dict)
# Graph code ----------------------------------------------------------------

app = dash.Dash()
app.layout = html.Div(
                      [html.Div([
                       html.Img(src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAYsAAAB/CAMAAAApSh4CAAABelBMVEX///'
                                    '8ZR3sAPafeADH///3//v/8//8cRngWR37T3OoAOWz///sbRnv6//////oAPXkZSHeLnrMOQ3wAOnn19vSHmbBOa5KirsFac5f98'
                                    '/TgJ0TeAC3iM0wAOKVFZL29ydoAKZ/M1+10i8IAPqT/+v/m7vUANWxvhKhHZZEzWYoAP3YAPawAMXDy//8AOXkAM6H52uAAP58AMqzWBDHgACU/'
                                    'X4YAMJzkACsrT4AcRIDXACeuvs8ZSHMANHYAM2jjAB7h6e3///BCZbUAQZoAMa4AJJ3tpLBQdJPnACFwiqddc5zqtb/K3eYAJ6wpTauTsczOPln+'
                                    'u8ntmKLmWXbqiJvkO2JJZ4csVanld464zunlBD94k7E8YaiouMOFncrQ2N+VpL3zwtLkw8ZngL7ScIHtO15ccLzC1PYAHamPn8eit+T22dSsxOSite'
                                    '5Xd7SBkMrUZHhwi7hQergAS58AMIPlnp9pgpVtgq/WAADxiJzcFEz0cotHcMHnYoZ7/ItJAAAfXElEQVR4nO1d/1/bRpoem5mRbGkkIdsY4romkSWCj'
                                    'G1s7ICxASchSd0Quk0a0oQS02bbLRzXbHfvervt7f9+M5IN1jdbMrD7ua6f/ADBsjQzz8z7bd55BZAEBAgAJIm7biQQAEvfrl+CAIAwFOiPGW4FEkIIC'
                                    'NlPl5/sL4/gyZMfP+j0Y/jd3N/2bPyt8f1zgjEC8F/d5t8rMHoI39ZeaFp8FCXtwbkk0Y8RKb7LzdnINfZ+/ZKU4YyLW4IA4Mcn+TjjYpSO6iMCmTDCpL'
                                    'z0B5uMHP2R23sJZuvitiCh8ydxL+pnQMCDS9Ybc1dovCToX9rg3zPu/uhDRXz5AsAhF+BSSjFsfvevbO3vG9/kNR8uniQEQRhecmfzkomNudzrmYy6Jdx9'
                                    'ES95qcg/6QqCZF2AQDGX27haF7nGtwDN6LgNvK9rbi5KWv6wUAaWWoCkWP5ye3OEi7nGbwRJM51xC3jkXRUlrfqBeYBMX5AiKr/anBvlIvcaYGHGxS2gppU'
                                    '8+qJW/wFA242gXKBfN+dGkbuzxDy+GW4cWs3DBV0phzpAtoxChLzanss5uUCzOMhtwMeGoiul/vPgY0rFei7nXhdgti5uA37ORelx9ePgY0TwK6eImnFxa/BdF7Xq+eBjDKmEmnHxz4FTUbCwVIli+S37DCMMnjc2Zlz8k+CwnzSmtzVNW37M4uUIE7TkMqJmXNwiHOuiXq/uPzn84cP7xCBeTl7lHE73jIvbxCgVy2/unV/c1SUBWLEoTM1ZKqE2cjMu/jkYWRS1C2ufCEqUCeZz0wH/x15jc+OG7Cg4Cvp9PPkrvxcgAAVBGPad/h/5bshdGk+1+IHrI4xIef0PjRuSURBgTHmWJNYKgf4U/m0CjMiO7QnOznuH8HJZVA/cY4NREQHy970bkVEQCpIw8n+E0L8LGZCuiKuZBwXWd99I95CL6kep6PoIwXKZDvrLvev73daTy4l+od3OnpycFPrd8tXff+9gypfoB7Tv7Tbt+0G/a4WQBM+FtnMXz7/x5hRgWCxigYD1O46geRQuoIABYg9NZHtN05Rlk/5LpVKViswvZApWpglC2LFChG7iGiDuXkD6r+ADz4Xs0dd5csLzZIgx40EvHDeTtO+s96lKiv1cXcn2saVCAb7iZLAs6heQeIkaNvHVdm7KdYGohgDdTCeZUmNibARiTK3sJJvzCSo+ofNuvbXktFgzdW8bYH/Xe+VuH0J3JzDY2jWmfXSl6X4uJoIEyu37yaTs7LwoijEzafYKBDCN7uCipMU/papEChpQFqrNTcmFAArNXZPnWyIXc4ITeU6Vd5ttt6TqyS1+SrRiXi4gmDdjHpg94MPFamzqJ7cWPA8WgL6ya7ZU3jkNB51vyYYyr4ORbTlbRlULEAfmPVGXj7y+CtZG0xeF1bUWT3kQPc1RKGIir65tFZxs9ExuSiixju7phYBXVe/YqatpjyWD4SoXm/bZ6pGn73rPUHn6ERt5V+dbKtehf5V3M+Wr6y0u8ocA4UARBaiqWd+LzAUUEJ0XBmuMSHvomZn2mMQUjjcWdTBiVfVU78UhoW551gWEfVP0gpcLHsuBrgvPoIUEz/H3h7dhOz+ILops0hRpv3k6At6ZGOPpcolxMVmh7YDkkot4/RxMwutLKRV6XSChz/lIBx+YrcKVvQ1XTGW6AaFcKJ51gcGxXyNE+Rc/LqadBU4umL2gLxpeAjzgeJUujcEysNZFtQwm4emlzxd6XYDsWitkV1prp5cjc8NcQH3Ld0zEjmcJ3RAXlhXb7chhlhjlIlY50q+4qP7k4wS6sLS3EXVdnK61wg6qou4cD2MiN8wFKMi+A6zI7dvighosCcUMJ+2Y9JK3utb3tFIpXi8IgTbU8PbkXTQuEDxd6yghVqndIkVJ9Qi1H26BixXZ91JOfXZLXFD7rCuqsdC3Ulpyp8usWE2LVx+BibnjiHy/HYULCNu7EbuTPCbW8rxhLnRF9Z0RHK90b4cLKhabarSvm1us3fGatlwA0sRgBP6tEYULoVuJ3K3/OrkNLtqGr7AQedHI3hIX+JedqPepMIv4cSn/DUDSpAA2Bi8jcYE/D2dBjSCVSYNbkFGL/tJCVEV18Za4OJH5sMJ5ALOZoDa9Fl9+C6GvjEKQUFN5/TvGEwT/HZoLRBAorHVGpyOdhVRLUU+DFy1TW2R+xejnVIGdgoGo7KmKx6tVY25+qNGuun04KnccXAhI6sYCdCh1McSu5IpKrYpul5822SPjOgrv8R4VfuB3Y0FfVZ2KksUDFFG1G8Ip9FdXOCh5X2ehQurnBa0JVC6WydPcK3vKhF8XCCPSVB1jx3XYf+WdlLi1RT3tlBlzOuKdVuXKqunJouIGJ7rNY1HlPFeJLUUfdVkFJGTHrE/zFDi4QGC1476pyHuCNzFVVDruR8cGfjdmIRfOEfSgs4ZXZdmIbW1txYxKRaWEO6jd+Z+09d1a/TzQhsJg/XWj8QmJyAUEQsFouaZGK5VayBS63a7e7fbbvftJxxilOv2r7/cqshspk/OsC8WUU+7LKpzDaUAQL4yRFuKCM/8RgS3T/eyU7DVOOdHzZIomsbnQm+4oA6+aW712v8vQL2QWY7KDjJ35QVg2/qAcpLcxwq8bc7mGta9R/jI0FwKCi2ZLGTUlRNU8KhDmBLG9RnpNOpHZki+HyWwejPjdJ/M+OPKOSMbvurRjoguJcQYNb/aFUaGApNN5n5s2PV9c9Xt01hpQDNq0X46ZI6rJrD7ou5VI0G0vGpdTUZSzYKCu8/eC47P4Ozb+e+tUWEGyNIxITeYC6BW6SB1RYvOZzrTB8GvsZ/qkk2LRW443F7sjzqZ/XCzj9hJE1X8Ojf4VC6fyaDOovHEsL/nUeULa/46Lbj5VT0j2quGCz+VcH4ARlcw2LQqLVBCzD1tcAQw7v/w2MCaI8G+bdPwbTwFBBIO58FycpNzNWdWRVy3pPYPnRT7Z89l0cAJDHy7SwTsul11wGvq8c3Fx6v30pDvQe/hxEegDQH3LvYKNtpdlSLKUI44ztxJXf3xAgs+1LL1jh8K2/055o4P/h83Q+sIzcHQCerjA0kOSTfJiMjN5q3VaLvqmU12IzjisaLrzLXwQkYt+0sWF2LH2Fp2gTe835ZZ8pMOrTvwFCIE9evoZ5WJz4zXGzLgdKu/J60JYcLfeoNajWxRCzGxfg4rL2+Pi2PktZcEZvBblzOQd90hcQNB2G25mxocL9pduc2cxDUaOFf0F+m380sFGgLy2wx4NgiEulp/ubVjb3pPXBXFvQIhc13/AJdAujB2IYXOic2FZCKtXOwfUphcXC5XRceVFZTUNJsVFI3HBIvQuy43FID2bQ5ZT2513yoqqHiCjEF6f27Di5HvrGFIJs84itblQXLhDAJQL/2GDEIfKBZlmXdDFX6jELk0ILsan2iDpsCi4WKUAJqUGReRixcNFFgq+8x250/WqFw9970uK5KvGgIunQCiWi+T1ZyH1RXrN7R4lC/7RR2pdTA6FgSm5kMCKfOUhKjFxLQ1+cUgQjpdXgATHn7KKyMWimwuTPgL7ciG5xHb+f31NCeZz/2MvZ+XSNv5MhVoZke/2LFNqcjzKy4W6iKDfwGHBkwDg38XoXNDud7eUFj9sisibC0BqG6NUUL261Z20MK/LRczQBd+ZSJlwrsl4Na8dlgq+9/66YZmxG5tpYvl7r629vcnrouzhQjSPqe5GVsLcNPlpU3CBsHPgY1zlBAhpw3Ub+cJ/0o7cKAoXiMoot03Ld3Qo0bXHcljHPioez8fzDxIP/QZA+MQ2Y7f/TizJ9nwv1LqAxLvTKyYXEkwkIUymyWmeSkbRKergwtA9f7MkyE2uCz8uqF5qW8nNwRarjTglY/9AcOdv2vcdmLG5bds9Ldu1cibbtFvu1sR4tZVaZCaTFEo/uDGNjJK6TgNWPWLT8sR1H2ZWjJ8d0biAZ6Yn7MK3jNU2mwgTzIQ4q8MCkW8cZHiE1apUxGLhv22H4+Jzb0CO42JmMrnSnuhi+2IKLoiUTTmaIWcliAV9zXUbOTuhUlw0X0+4SLov5zlFbMnJhZPuhF7W4vG6DnzrGGBUtE6IUWsqR+2ochE8/ywUF3C+4uFiMAnlndV5FiSELOk9fIL0NP4FXnB8RV3rWgN41HLsHojy4gQhFY0Lqbvjv2Eiqsk1/viELQ9gxUe9vdfi+UMg+deUIFR7W7o713hJjVxsZ6yFiIEU1nybw9ASzZ3do5MEAVGyzKfRF33nBFWbtjl/4sqV4ZPd8c+OyIW+GhQa5lstObW2elooW2m03sZr+eq9IDlGyHPmeVvHxKQignhpL5Tuxih4q5LnlY6YqhjJxZNEeC0+DRcZp5aWszYXunv/m20ojkNEfQF6/nknTExzisLFVCP5LJvw83G1/P4XXg/QAgRkiTkYVETlGk/LGBHyLpSMIpJvqh4bQJFtjYoK2+mqrHWO+1aywfixYJiCi7Rra3FNt4uTwfvOoVXUhfHmTTQuEEwEccHTfrdaKserqlwxe22PY6fF94MiQoggFpLa2JjbnNv7BLDcwj//jZIRIvegmxJDZKaKpsGxxHdIMA5OrWaIyIVEp2ff4B0bOs1BXjnMOgP6imocgADjxR6GSDIKIfJMFX3Sh90wZXmB0YFGz19UE0H3xcXyy89Y0cftO8/Xy6xOy/rz77e3w+SBZORWmJQKXjWNZptAYYK1F5ELNrSZFD/aAiqibC6EhNP74Xh53iIvCBG5oLPAVL175D5QVUM8HbUrx3FBimR9k5qxja+Z0UOfgkl5/XUjDBfpTqhkcZbwrRrNAvaNkFwhIhcIURXaio1uLa51BwE6CBz7S3TUWvfH7OFE5YL5MBmTD9N5lpNQUU5Gzl/kl+8GiWyCEL6znWt8hZF1JIDKESpNvn43mQsoFDxmth/snH81dayP1xqRuYAFQ1VGxCS/Cgb5N9TiHr0VL3JUSMEx9nXEvSSMBXI/SGW4oCgdtbJwGRGrxesXYEzNuq8bjX9QUi4Tjwlef7eEJoRwrD2VSviM0pjc7LK6n4GtiMoFACuOjYrOzvxV0/ruHWD5GIwp9BpxXQBrlyhCDqdpDk9m1eKln2Dw2LIyOUvlKy5YvPblEvKNxzsggJOKGvpgiag2E+MSSSPbUe5d57UrQQzJqissoK6OiwZE5oJKhYNmhNRB0fjC/p5WKuV1KdCMIHf2/s4c5CEXmBTRUnpyjTumAAodT/g4EKpKV0ZwJmlELjBsOxQ012pe3poK24zb4jYKMNjXmYILCeiLSf+Uaj8u1F07US9eitfPpEDVSX772zpdFZfilHrfhNIxsXYzFcBQ6IY6mjNokHw0plJ6VDtKeObIxYlVrkQUFmDfiDlPM6q9m+SCHZCF+FRmTeBiPicV3T0RY8k+uyOL0/412LrGX+5NOpoxpk2k3TRUqp1DmNv2eAVu0USUUV3VYcaJRsJRc2GLd3g/nLrlPbZxdXXkdWH1HRw8S5osDTiMsBJXEZ0N7FzS8vnDoHmO1zekqQs90v6n20dJ052X5A8l1Q/c5IvKRdZ5tdhxKrhj2TlZecNzRukKU3GBBUkgiR7HjkeH6HvMOAWSfb77cMx5vV+nXhdUZwgSJP3jphFGcXByb8ytotlRC07vRs44ZVDB6ZMzIRXcjam4YDpWEIA+v5CUwygOPqkLg7OT74MGHJHXS6OTFSPC3I5JLbHA+k+YR51OZBaShqz6nSweaY6S6t6AjGIedCLpHGvjQBJGKyaRmPMkIcdbBykDEmKmklECxMTyybrZlS3DVFlchLMcKv8xYGlidsEiLSiXkVqwz/HI2FNXvEhQhJ2H4ff0Qua+IVt8BKgPTk25DwpdIgoX1DSed+Xu8UVkb7YPAHquDRaeWjIowDicbl2MQk+cLiqG3KKdV9hhdz+oW0Muls8DU1Oev6K+9lXDqFG1TiIXl6fThE4UvX3c3KV88AGmhfosyJqJIqOwVG62HDLKnHdfUzAc00FsqYv0ZrfEhVWBRS/ML5iGGbgu+N3uoDZL6Q2Bvtu+kKzvrYMrj5jlDnydRj6JyuOBMRYwq8Kit3udXdnXLeV4n2oeg6+H50JAUsJwpWreX/z888VRPHPqE1Hkja6A/NXP9dcFs2IQhIIlG5L+B+B4uW1xkS9p1QNb3binBsRLm38ogqIVHASWdHr6jiqCqFwgq3oXy0oRIElktgyeU6yTYyNQYql+gFkbhQtmJimuqg+c6nDvWpwreMdx8im4NS6oq4WZLKHrg+jZz9dMxWPnirx5PKxZVL2X0CWfKD4VXO/2XpUJoaqIsNhg+dvtT0KEQMaAeXS43THdSd8xK/XUfx8jioyC6a2IJ3rt8Q2KA93EuhgFOVjc8eYs8eLiZV21F1VqTEHsTQYH3283vl+nv1JvuwyErzY3r8mFdVtQXDFEXnHJTirY/TcyInCBqTKITgVzB/8pXEAJSqDtsfEpF6uXXDzWtENd8uRDs3Ni25vbuT9+u0QwWX95ZzuXuz4XAqGi5BfOo8fMTMCppChcwOnq7MjzAXGQG+WCRfbQQ6Htni5Up29d1X4sxes+SQjUzvu6MZeba+xtz73bbuzN5cJxwapuIrt8j8+11oEp3Rs9uwkuJJ3znD8OAa7VDAiHTcGFTSrEfgkG2PLPejLnENB0KHhH3eZqwhMjpMbr073BGZjhGbFQXEBBAmenTDkEXkvn7y2sC6lthAp/ublQ1wKE1DQxcwH0j8pWRdqAS/o7jrOlLFTp5KL+qOjWF4jgb0dfrxeWCywJoLcjF4AUGDOCJx6peSP64tmUpcDoRPBFdC5YYb9kqsfqkwXZm91Wx2nKjeoLy+Xbf++5LV1QriLa4daFUF6sdLhUwT8l0ULbsxPJcpiua0fpyagFIOyxUNStm/L1IMgaaivZwyAwVVd3nrmOKTy9qYOLUvVAIE4/DiPyVSMiF/QGgt6UlRavGG0gUdvac1yNmsjwVFYcMpPjK9f2L+gwmFNxQUfDKADoY9hGPK9HnVowb6jUMjJWCJQE7C0eSPVIV+ZcXFz5FwPkvyHe9JSlOecL9iZxgayyYrZzJe5miCBg7/Sg07/JO+YGTx2y6/rd1LlfmLJioF2a06fqYsR1QX3ZnmHLn2Sza+2qefougWzSucfEieaJ850LtXj1PfAO9MvPInIB+qI6iJTy8v0D7042Zka24XJ+RbV57f0LmAi/leiGyOl+lka0c0lYSj+T7UoyXExNZonkzesQgN5xZgzFFNHoO7nQSvHqW2/4HN0ZfX3VRC4g87auSpqohs9Zepb/rKiiw/hspTwxvMsuhuQCgvmQ6TB+MNp+m1kRZZR+ZPKxQTEgnjeaBZ+Qq77AqYojYEtllPt9SZSNNyypy8EHBt/theWC+RRUc43MePqbmez1LZ0xKEJBTT29t9ZSREd6Hdeq9INuG5YLgTizvDmVVwPQinkKU6orfgHS8FwwadRtyq3LGqisIvBas13G0No/QbZnRawAkLOWToxtpMVd0B58YClqjv0jAL7fDsmFIEl4fld1OVuiaXR67W46Tajznk4n2itrquJxyFr3A+8bkgsED1wJmqqyGIRnTbftyzbXrsEFHXDQ73hMB9FILmYTOu05/ZfWC8dbRqvlFqT82oGHC7owXnxBTbHRXmJMnjbCyihYtooVux/VUuXUmrq6QMegqewm2T6XmwqeiohrcgFdtWh50RyzeXrgDkSISb9t7/BcULdCpLaje5KxvHLDpH1fWVzYSloVcrwlqe4Dwe+dbkxlOIQUQUthucAgu+ZjyLBKybEOFZGy3FLZbjwnevaT1CMSmOEclguy5fKgqJ1K/AGFtDtnLaY+u57u7iZbvntFLGuYgvbd2ttzh0QpjLvUvvFSoZUeJyDzCS5zBVEZvM6F4wJK5SOT860rR9tjnba2ykq7q5UpCitqfd1cNaHgnAhiTEw7NrpH3xKEQMZ0Ob8xQ/exXEJzAd35J15Y4RnRuXHDcyztQsK+7zqsv+my9OBhT9lr9r66elXPeC6YveaVUZNATQ75GAe/5jWs7u45U9SYiApcalS4pxSn9cDJPjvuEdaFRDJyuBycUXC8qOjQn4t4rXqYoGbxFRcIP/8spIxifp4SOSIktszFcYn3IbnQ3ft1RnDlF9rS9GrLYVhynOp5iUUkO0qSSM9sRSWDU5MsmdifC61U1d7C4rCnyC7Mkgu1LjBd/onIG2uc2exSQ/p6uhtR99EprUU+Pf5In9xxGLacutu9BheQYOZ0R+w7Nd/adpK9HxfWS3veSkW6NjCw04bgyDsXxnIBbH9H9tcZvk2hijzV7Nr+x3W48JaXYw7DOC4KnoLG5qknJhVFXzA+MkaYI2LDzrO0h5NBaocvFxR5ak0hdLUB/m4zFBeDNpVXjAhp1i3rBRjj7hiCCwQEPel6phFQnmcI7ysAxA6engur7xLOhjwjxtCJya3C0GoNoKLEzsjAkTjhq0YELiCA7VjYYISoyhnifXmRA6G48Fgx4pY+lgsIep7ztkbielywzM3EQir0yyZSRwdAGniYQesiruWr5+Aqf+1lYyPCvh7CsPtLKlQZbVFuFmDwpouNcFwcuQbNXGEpcsF3hbCQ8qSieLYWo8WjrDAPzirhZqJpzqcBHIZyA7lg72f9mUhQsvPMv2xshl4XVqOoX7uYMlnKoo9vQ21YVeXpJzFTyaYnljYDRMrIrpfsxOS0Y9QQPNhtjX6uxIzA+NYAEhVSLqgcdhzJQYwL1zWtheA6sgPopy2qMv2KPlvxWfutRamdXnc0i3cMFzXtxU9daGcy4/W9SPt6FmA/o8qu95nZUDrsUIaoGqvZNJhY8Y8NdMYdWVDEdHG0GRI8NUc73lJ9Xp7kguAtUqAk+47m0Kn4zL0uFO9rqjx3FvTsqmFSzexNWOVYXJBV1e655soYLuLUmnr8Fj4k1mg15qLkHlgDSN36dLvHGabn4B6v0rZUlJ5dy3ninaioPN5JOVH5r7JjdgqEl82Rz+WkMSYWZQPDwlrFddudnsP9pzJnwf3onfuePDJP34sSIInM6hoL+rg632qppmwcZXV3fb9xXMQ1ak7dsyYXIoMia+G5YO8RY5kHJHHSW62ssdctDiGn1pRng3o5mCmLifpHKpxk3ZCcSZdpzwWTRBSExPulbNa5TKHgffJJiP1+xEZa6p5k7pvOvsuVtdXeiY5ZFT5Xjbvx0OL7tbtWZQX863ZUGTUCnCi0T+czx72VXu/4NFuYrozU/yOMjBDW+ydZ1vXFxZVeJtvuBx2wmMBFXNMefAASKhcvX7E3DRfD9/Ta769mxs1YA+f3BeZvDt7fzQrMM/Hm3/cJVJS0WumJLmGEMX61Of26YHnRl2CvjA2hJX43YDUfWZSeGq/M5g30eewhz+ftH24q8vlSSaufCWWpWAZPt6fnAlkZ/9h68QCxmPDJDfmdwvKeIMuklKTBSyf8DUc24nWNiqJ8qVbS6DrY1+Lxan0/XqNmlPZX+kF8OVF8iAhATxtzG9NyMUMIWDrhZ2pp/7z/KQDlmvWiN0AKh/u1/Qsm6j5WX9x9iFmK0yBnbcbFbcGSRPeoCLtYfgQeduMJplvpWrpbfbx88JCuq4vl+s+wKCFMfr2GvpghBBgX1Q8SkPTlTwWo1xMQpS8SWCBv6vUy1RMP71a1FwkkoWJ67xo27QwhYHFxD2BJevQIQL2UgELiRa0LwTf735SFt/rDMlUkj1ju//qMi1vGgAuq5t+/sbmA3XqVao1Pqx+gcJGQwKFWf3IXsYS1GRe3iwEX1NJKvBmui/w3RUmvLZ9J4P1bAD5o1fw3YLYubh9DLhJC+gdor4tigroTPz948VYAH06hdF7Vaj92ISq/m97vniEMhlzcvSuc2VxQPwyCu4/qyzoWHr0XYKKqlR5cUFP362v4ejOEwFBf/OkcJgR7XaQv7kKh/OYwDYXHH6jcimvxB3+CBD+d+Re3iyEXdx8BSRjoix+fdCX48QcAivfOEIZ/pVecCxL4DztfbcbFbUEbcJHI6wMuYDf/JAGEs4/s5L0kQel/8/HSA3b2295NmnFxW6iVtJLFxY+Fh8N1UX9xAMDZf1JfW2dvGTuvxuNPipSL7U32UrfcJ5NLBc8wDTR2MIxx8eIjHHChP/pJl+CHhAAuDmsJIL1drpUeAEqKfQqDrgswIW1jhqlwWNJsfbF8KAy4AEVCCXmTFsD7/Sdvqbm7/Hi/xrh4uW29L+l7K9t5hhvHT1QZ5Nm6eFLvAqDnu/ax/fIH5t79XF2+oNeUavU3QEBkfY/JqO1XZOpqkDOMwxf7Wjz/6PzsYzV/7/zsLH7v7OzsP99/eFP/9P3792/i9b+cvf/isFT7AUCE0a+b7FUYzyNXj5ohFPQnbO/owX5d0+r1er5Ur+5Xqw/ydLVU69VSPB+n/y/l4x8pFxD/kXkY75bwxFLBM0yF95SFeC2ulUq1mlbKa9avpRL7qcVLpXyppsW16jlkJeBe7s1tNL7CY4rAz3ANCOXDUrweZ7uspVK8ZKUbUMTzWsnOybE+Wj4X2GtsX+5tNL5PgyhvAJshPKjFpOVrlI1xySDU7wYCVd4vP2vcWZ/Zs7cFLEH9cLmkjU/NqX4EEsFLG3uv18e9KmKGawFBSXh4Hl+u5seh+kCHBP557iXBpDizaG8JVgE8gbz9+MOjR5+OwU9F+N2XAnXygg+bznBDmJA4DSe/fmSGa+L/AAw7tzwEdLS2AAAAAElFTkSuQmCC', className='logo',
                                style={'width': '500px','height': '200px','float': 'left'}),
                       ], style={
                                 'font': 'Helvetica',
                                 'font-size': '25px',
                                 'display': 'inline-block',
                                 }),
                       html.Br(),
                       html.Br(),
                       html.Label('Select teams', style={'font-family': 'Helvetica'}),
                       html.Div(
                       dcc.Dropdown(
                           id='team_dropdown',
                           options=[
                               {'label': 'Golden State Warriors', 'value': 'gs'},
                               {'label': 'Boston Celtics', 'value': 'bos'},
                               {'label': 'Atlanta Hawks', 'value': 'atl'},
                               {'label': 'Brooklyn Nets', 'value': 'bkn'},
                               {'label': 'Charlotte Hornets', 'value': 'cha'},
                               {'label': 'Chicago Bulls', 'value': 'chi'},
                               {'label': 'Dallas Mavericks', 'value': 'dal'},
                               {'label': 'Denver Nuggets', 'value': 'den'},
                               {'label': 'Detroit Pistons', 'value': 'det'},
                               {'label': 'Houston Rockets', 'value': 'hou'},
                               {'label': 'Indiana Pacers', 'value': 'ind'},
                               {'label': 'LA Clippers', 'value': 'lac'},
                               {'label': 'LA Lakers', 'value': 'lal'},
                               {'label': 'Memphis Grizzlies', 'value': 'mem'},
                               {'label': 'Miami Heat', 'value': 'mia'},
                               {'label': 'Milwaukee Bucks', 'value': 'mil'},
                               {'label': 'Minnesota Timberwolves', 'value': 'min'},
                               {'label': 'New Orleans Pelicans', 'value': 'no'},
                               {'label': 'New York Knicks', 'value': 'mia'},
                               {'label': 'Oklahoma City Thunder', 'value': 'okc'},
                               {'label': 'Orlando Magics', 'value': 'orl'},
                               {'label': 'Philadelphia 76ers', 'value': 'phi'},
                               {'label': 'Phoenix Suns', 'value': 'phx'},
                               {'label': 'Portland Trail Blazers', 'value': 'por'},
                               {'label': 'Sacramento Kings', 'value': 'sac'},
                               {'label': 'San Antonio Spurs', 'value': 'sa'},
                               {'label': 'Toronto Raptors', 'value': 'tor'},
                               {'label': 'Utah Jazz', 'value': 'utah'},
                               {'label': 'Washington Wizards', 'value': 'wsh'}

                           ],
                           multi=True

                       ), style={'width': '500px'}),
                       dcc.Graph(id='player_salary', style={'width': '1200px'}),

                       html.Hr(),
                       html.Div(children=[                                  #---- beginning of code for drop down buttons for x and y values
                        html.Div([
                         html.Label('Select the data for the Y-axis'),
                         dcc.Dropdown(                     #code for dropdown option for y-values
                          id='y-values',
                          options=[
                             {'label': 'GP', 'value': 'GP'},
                             {'label': 'Min', 'value': 'Min'},
                             {'label': 'PPG', 'value': 'PPG'},
                             {'label': 'RPG', 'value': 'RPG'},
                             {'label': 'APG', 'value': 'APG'},
                             {'label': 'SPG', 'value': 'SPG'},
                             {'label': 'BPG', 'value': 'BPG'},
                             {'label': 'Salary', 'value': 'Salary'}
                                 ],
                          value='PPG'
                         )], style={'display': 'inline-block', 'font-family': 'Helvetica', 'margin-top':'30px'}),

                        html.Div([                  #code for dropdown option for x-values
                           html.Label('Select the data for the X-axis'),
                           dcc.Dropdown(
                               id='x-values',
                               options=[
                                   {'label': 'GP', 'value': 'GP'},
                                   {'label': 'Min', 'value': 'Min'},
                                   {'label': 'PPG', 'value': 'PPG'},
                                   {'label': 'RPG', 'value': 'RPG'},
                                   {'label': 'APG', 'value': 'APG'},
                                   {'label': 'SPG', 'value': 'SPG'},
                                   {'label': 'BPG', 'value': 'BPG'},
                                   {'label': 'Salary', 'value': 'Salary'}
                               ],
                               value='Salary'
                           )], style={'display': 'inline-block', 'margin-left': '10px', 'margin-top':'30px'})],
                           style={'display': 'inline-block', 'font-family': 'Helvetica'}),

                        dcc.Graph(id='scatter', style={'width': '1200px'})   #---scatter graph

                       ], style={})


@app.callback(
    dash.dependencies.Output('scatter', 'figure'),
    [dash.dependencies.Input('x-values', 'value'),
     dash.dependencies.Input('y-values', 'value')])
def update_graph(x_values, y_values):

    return {
        'data': [go.Scatter(
            x=[team_dict[i][p][x_values] for p in team_dict[i]],
            y=[team_dict[i][p][y_values] for p in team_dict[i]],
            text=[p for p in team_dict[i]],
            mode='markers',
            marker={
                'size': 15,
                'line': {'width': .5, 'color': 'black'}
            },
            name=i
        ) for i in team_initials
        ],
        'layout': go.Layout(
           xaxis={'type': 'log', 'title': x_values},
           yaxis={'type': 'log', 'title': y_values},
           margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
           legend={'x': 0, 'y': 1},
           hovermode='closest'
        )

    }


@app.callback(
    dash.dependencies.Output('player_salary', 'figure'),
    [dash.dependencies.Input('team_dropdown', 'value')])
def update_salary_graph(teams):
    if teams is None:
        return
    else:
        return{
            'data': [{'x': [p for p in team_dict[i]], 'y':[team_dict[i][p]['Salary'] for p in team_dict[i]],
                     'type': 'bar', 'name': i} for i in teams]
        }


if __name__ == '__main__':
    app.run_server(debug=True)
