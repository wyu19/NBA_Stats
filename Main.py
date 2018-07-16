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

#make a player:salary dictionary so i can call it to fill in the salary part.


def create_salary_dict(roster_info):
    player = [p for i, p in enumerate(roster_info) if i% 8 == 0]
    salary = [s for i, s in enumerate(roster_info[6:]) if i% 8 == 0]
    sal_dict = dict(zip(player, salary))
    return sal_dict


def print_team(t_dict):
    for i in t_dict:
        for p in t_dict[i]:
            print("{} {}".format(p, t_dict[i][p]))


#team_dict[teams][player][stats]
#reused variables

url_dict = {}
# team_initials = ['gs', 'bos', 'atl', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'hou',
#                   'ind', 'lac', 'mem', 'mia', 'mil', 'no', 'nyk', 'okc', 'orl', 'phi', 'phx',
#                  'por', 'sac', 'sas', 'tor', 'utah', 'was'
#                 ]

team_initials = ['gs', 'bos']

roster_link = 'http://www.espn.com/nba/team/roster/_/name/'
stats_link = 'http://www.espn.com/nba/team/stats/_/name/'
stats_list = ["GP","Min", "PPG", "RPG", "APG", "SPG", "BPG", "Salary"]
team_dict = {}
season_type = "/seasontype/2"

#add salary to the end of all the stats list.
#accesses all the nba roster links and infos

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
            print("{} 's status code is {} and {} 's status code is {} ".format(roster_url, roster_req.status_code, stat_url, stat_req.status_code))

    # add_more = input("Do you want to continue? Enter yes or no: ")
    # if add_more == 'no':
    #     break

print(url_dict)
print(team_dict)
# Graph code ----------------------------------------------------------------

app = dash.Dash()
app.layout = html.Div(
                      [html.H1('NBA Statistics'),
                       html.Label('Select a team'),
                       dcc.Dropdown(
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

                       ),

                       dcc.Graph(id='player_salary',                                     #----beginning of code for 1st graph
                                 figure={
                                    'data': [
                                        {'x': list(player_salaries.keys()),
                                         'y': list(player_salaries.values()),
                                         'type': 'line', 'name': 'player_salary'}
                                        ]
                                 }),

                       html.Div(children=[                                  #---- beginning of code for drop down buttons for x and y values
                        html.Div([
                         html.Label('Select the data for the Y-axis'),
                         dcc.Dropdown(
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

                         )], style={'display': 'inline-block'}),
                        html.Div([
                           html.Label('Select the data for the X-axis'),
                           dcc.Dropdown(
                               id ='x-values',
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

                           )], style={'display': 'inline-block', 'margin-left': '10px'})],
                           style={'display': 'inline-block'}),

                        dcc.Graph(id='scatter',    #try just having the id of graph without anything in it                      #--- beginning of code for scatter plot
                                  figure={
                                     'data': [
                                         go.Scatter(
                                             x=[team_dict[i][s]['Salary'] for s in team_dict[i]],
                                             y=[team_dict[i][s]['PPG'] for s in team_dict[i]],

                                             text=[p for p in team_dict[i]],
                                             mode='markers',
                                             opacity=0.7,
                                             marker={
                                                 'size': 15,
                                                 'line': {'width': .5, 'color': 'black'}
                                             },
                                             name=i
                                         )for i in team_initials


                                     ],
                                     'layout': go.Layout(
                                         xaxis={'type': 'log', 'title': 'Salary'},       #make x and y variables
                                         yaxis={'type': 'log', 'title': 'Points'},
                                         margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                         legend={'x': 0, 'y': 1},
                                         hovermode='closest'

                                     )
                                  })
                       ])

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


if __name__ == '__main__':
    app.run_server(debug=True)
