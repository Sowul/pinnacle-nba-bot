# -*- coding: utf-8 -*-

"""List of functions:
---pinnacle specific---
get_balance
get_fixtures
get_ids
get_lines
get_sport_odds
place_bet

---other---
create_model
get_pick
get_start_times
initiate_scheduler
load_trained_model
login_to_twitter
open_sheet
prepare_bet
prepare_training_set
prevent_inactivity
set_scheduler
shutdown
tweet
validate_spread
"""

import base64
from collections import deque
import csv
from datetime import date, datetime, timedelta
import json
import logging
from operator import itemgetter
import re
import threading
from threading import Thread
import time
import urllib.request as ulib
from urllib.request import urlopen
import uuid

from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import gspread
import nmap
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import pytz
import tweepy

from teams import teams_abrv2full, teams_full2abrv, teams_covers2full, teams_abrv2emoji

#pinnacle specific
def get_balance(base_url, username, password):
    """Returns current client balance.

    https://www.pinnacle.com/en/api/manual#GCbal

    No request parameters.

    """
    url = base_url + "/v1/client/balance"
    b64str = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    headers = {'Content-length' : '0',
               'Content-type' : 'application/json',
               'Authorization' : "Basic " + b64str.decode('utf-8')}

    req = ulib.Request(url, headers=headers)
    responseData = ulib.urlopen(req).read()
    balance = json.loads(responseData.decode('utf-8'))
    print(balance)
    return balance


def get_fixtures(base_url, username, password, sport = '4'):
    """Returns all non-settled events.

    https://www.pinnacle.com/en/api/manual#GetFixtures

    Please note that it is possible that the event is in Get Fixtures response but not in Get Odds. This happens when the odds have not been set yet for the event.
    Please note that it is possible to receive the same exact response when using "since" parameter. This is rare and can be caused by internal updates of event's properties.

    """
    #https://api.pinnaclesports.com/v1/feed?sportid=4&leagueid=487&oddsFormat=1
    url = base_url + '/v1/fixtures?sportid=' + str(sport) + '&leagueids=487'
    b64str = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    headers = {'Content-length' : '0',
               'Content-type' : 'application/json',
               'Authorization' : "Basic " + b64str.decode('utf-8')
               }

    req = ulib.Request(url, headers=headers)
    responseData = ulib.urlopen(req).read()
    fixtures = json.loads(responseData.decode('utf-8'))
    return fixtures


def get_ids(g):
    """Returns game's eventId and lineId.

    Args:
        g: List of dictionaries with games data.

    Returns:
        games: Dictionary with list of games.

    """
    logger.info('Getting eventIds and lineIds...')
    fixtures = get_fixtures(base_url, username, password)
    games = {}
    newlist = sorted(fixtures['league'][0]['events'], key=itemgetter(('starts'),('id')))
    for event in newlist:
        games[event['id']] = [event['id'], event['away'], event['home'], event['starts']]
    odds = get_sport_odds(base_url, username, password)
    for event in odds['leagues'][0]['events']:
        if 'spreads' in event['periods'][0]:
            #print(event['periods'][0]['spreads'])
            for spread in event['periods'][0]['spreads']:
                if 'altLineId' not in spread:
                    for game in g:
                        if (teams_full2abrv[games[event['id']][1]] == game['away']):
                            game['eventId'] = event['id']
                            lineId = get_lines(base_url, username, password, game['eventId'], "TEAM2", spread['hdp'])['lineId']
                            game['lineId'] = lineId
                        else:
                            pass
    logger.info('Got them')
    return games


def get_lines(base_url, username, password, eventId, team, handicap, sport = 4):
    """Returns latest line.

    https://www.pinnacle.com/en/api/manual#Gline

    Args:
        eventId:    Game's eventId.
        team:       'TEAM1' for an away team, 'TEAM2' for a home team.
        handicap:   Game's main spread line.

    Returns:
        lines:  List of available line's information.

    """
    #https://api.pinnaclesports.com/v1/feed?sportid=4&leagueid=487&oddsFormat=1
    url = base_url + '/v1/line?sportId=' + str(sport) + '&leagueId=487&eventId=' + str(eventId) + '&periodNumber=0&betType=SPREAD&team=' + str(team) + '&handicap=' + str(handicap) + '&oddsFormat=DECIMAL'
    b64str = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    headers = {'Content-length' : '0',
               'Content-type' : 'application/json',
               'Authorization' : "Basic " + b64str.decode('utf-8')
               }

    req = ulib.Request(url, headers=headers)
    responseData = ulib.urlopen(req).read()
    lines = json.loads(responseData.decode('utf-8'))
    return lines


def get_sport_odds(base_url, username, password, sport = '4'):
    """Returns straight and parlay odds for all non-settled events.

    https://www.pinnacle.com/en/api/manual#GetOdds

    Please note that it is possible that the event is in Get Fixtures response but not in Get Odds. This is happens when the odds have not been set yet for the event.

    Returns:
        odds: List of all available odds for a given sport.

    """
    url = base_url + '/v1/odds?sportId=' + str(sport) + '&leagueids=487&oddsFormat=1'
    b64str = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    headers = {'Content-length' : '0',
               'Content-type' : 'application/json',
               'Authorization' : "Basic " + b64str.decode('utf-8')
               }

    req = ulib.Request(url, headers=headers)
    responseData = ulib.urlopen(req).read()
    odds = json.loads(responseData.decode('utf-8'))
    return odds


def place_bet(base_url, username, password, bet, stake=1.1):
    """Place bet in the system.

    Args:
        bet: Dictionary containing game's data.

    Returns:
        response: Place bet response.

    """
    url = base_url + "/v1/bets/place"
    b64str = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    headers = {'Content-length' : '1',
               'Content-type' : 'application/json',
               'Authorization' : "Basic " + b64str.decode('utf-8')}

    data = {
            "uniqueRequestId":uuid.uuid4().hex,
            "acceptBetterLine": str(True),
            "stake": str(float(stake)),
            "winRiskStake":"RISK",
            "sportId":str(4),
            "eventId":str(int(bet['eventId'])),
            "lineId":str(int(bet['lineId'])),
            "periodNumber":str(0),
            "betType":"SPREAD",
            "team":bet['team'],
            "oddsFormat":"DECIMAL"
    }

    req = ulib.Request(url, headers = headers)
    response = ulib.urlopen(req, json.dumps(data).encode("utf-8")).read().decode()
    response = json.loads(response)
    #print("Bet status:")
    #print(response)
    return response


#other
def create_model():
    # Here you can load / create your model.
    return model


def get_data(x, games, ws):
    team = ""
    odds = get_sport_odds(base_url, username, password)
    spreads = validate_spread()
    for event in odds['leagues'][0]['events']:
        if 'spreads' in event['periods'][0]:
            for spread in event['periods'][0]['spreads']:
                if 'altLineId' not in spread:
                    #print(teams_full2abrv[games[event['id']][1]])
                    if (teams_full2abrv[games[event['id']][1]] == x['away'] and teams_full2abrv[games[event['id']][2]] == x['home']):
                        #print(x)
                        if (ws.acell("K3").value == "UPDATED"):
                            team = x['away']
                            cell = ws.find(team)
                            r = cell.row
                            x['data'] = np.array([
                                float(ws.cell(r, 1).value),
                                float(ws.cell(r, 2).value),
                                float(ws.cell(r, 3).value)])
                            logger.info('%s', x)
                        else:
                            pass
                    else:
                        pass


def get_pick(input_data):
    """Returns algorithm's prediction.

    Args:
        input_data: Four-element input vector.

    Returns:
        away or home: Algo's pick - away team if avg == 1 else home team.

    """
    # Here you should use your algo to get prediction (class label). For example:
    '''
    if (avg == 1):
        away = 'TEAM1'
        print("away")
        return away
    else:
        home = 'TEAM2'
        print("home")
        return home
    #1 away 0 home
    '''


def get_start_times(today=date.today()):
    """Sets time for scheduler to place bet.

    Returns:
        games: List of dicitonaries with games' data.

    """
    logger.info('Getting start times...')
    season = 2017
    if(season == today.year):
        if(today.month >= 10):
            season = season + 1
        else:
            pass
    else:
        pass
    month = '-'+today.strftime("%B").lower()
    today = today.strftime("%Y%m%d")

    url = 'http://www.basketball-reference.com/leagues/NBA_'+\
        str(season)+'_games'+str(month)+'.html'
    f1 = urlopen(url).read().decode('utf-8')
    f2 = f1.split('\n')
    url_list = []

    soup = BeautifulSoup(f1, "lxml")
    scores = soup.find("div", attrs={"id":"all_schedule"}).find("tbody").findAll("tr")
    scores = [str(score) for score in scores if today in str(score)]
    games = []
    local_tz = pytz.timezone('US/Eastern')
    is_dst = bool(time.localtime().tm_isdst)
    time_zone = time.tzname[is_dst]
    #print(time_zone)
    #print(today)
    for score in scores:
        temp = re.findall('(?<=time">).+(?=</td>)', str(score))[0]
        separator = temp.index('<')
        start_time = today + ' ' + temp[:separator].replace(' ', '').upper()
        datetime_object = datetime.strptime(start_time, '%Y%m%d %I:%M%p')
        datetime_object = datetime_object - timedelta(minutes=30)
        #datetime_object = datetime_object - timedelta(hours=3)
        datetime_object = local_tz.localize(datetime_object).astimezone(pytz.UTC)
        teams = re.findall('(?<=csk=").{16}(?=")', str(score))
        games.append({'starts': datetime_object,
                      'away': teams[0][:3],
                      'home': teams[1][:3],
                      'game_id': teams[0][4:],
                      'eventId': 0,
                      'lineId': 0,
                      'hdp': 0,
                      'team': "",
                      'data': 0})
    from operator import itemgetter
    games = sorted(games, key=itemgetter('starts'))
    logger.info('Got start times')
    return games


def initiate_scheduler():
    """Initiates scheduler.

    Returns:
        sched: BlockingScheduler from APScheduler module.

    """
    logger.info('Initiating scheduler...')
    sched = BlockingScheduler(timezone='UTC')
    logger.info('Scheduler initiated')
    return sched


def load_trained_model(weights_path):
   model = create_model()
   model.load_weights(weights_path)
   return model


def login_to_twitter(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    ret = {}
    ret['api'] = api
    ret['auth'] = auth
    return api


def open_sheet():
    """Opens Google Sheets spreadsheet containing input data.

    Returns:
        ws: Input data sheet ('beaty_clean').

    """
    logger.info('Opening sheet...')
    scope = ['https://spreadsheets.google.com/feeds']
    JSON_WITH_CREDS = 'AlgoNBA-488be4605440.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_WITH_CREDS, scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET = '4FACTORS_1617.xlsx'
    sh = gc.open(SPREADSHEET)
    ws = sh.worksheet("bety_clean")
    logger.info('Sheet opened')
    return ws


def prepare_bet(x, games, sched):
    """Prepares data for algo to pick the winner.

    Args:
        x:      Dictionary containing game data.
        games:  List of raw games' info.
        sched:  BlockingScheduler.
        count:  Number of games.

    """
    logger.info('Preparing bet...')
    global count
    team = ""
    #print(x)
    odds = get_sport_odds(base_url, username, password)
    spreads = validate_spread()
    for event in odds['leagues'][0]['events']:
        if 'spreads' in event['periods'][0]:
            for spread in event['periods'][0]['spreads']:
                if 'altLineId' not in spread:
                    if (teams_full2abrv[games[event['id']][1]] == x['away'] and teams_full2abrv[games[event['id']][2]] == x['home']):
                        #TUTAJ
                        if (x['lineId'] is None):
                            #print(x['lineId'])
                            lineId = get_lines(base_url, username, password, x['eventId'], "TEAM2", spreads[games[event['id']][1]])['lineId']
                            x['lineId'] = lineId
                            #print(x['lineId'])
                        x['hdp'] = str(-float(spread['hdp']))
                        if (spreads[games[event['id']][1]] == "pk"):
                            x['hdp'] = "0"
                        elif (spreads[games[event['id']][1]] != x['hdp']):
                            x['hdp'] = str(-float(spreads[games[event['id']][1]]))
                        else:
                            pass

                        hdp = np.array([float(x['hdp'])])
                        x['data'] = np.append(x['data'], hdp)
                        #print(x['away'])
                        #print(x['data'])
                        #x['data'] = x['data'].append(float(x['hdp']))
                        team = get_pick(x['data'].reshape(1, -1))
                        x['team'] = team
                        if (team == 'TEAM1'):
                            pass
                        else:
                            if (x['hdp'] == "0"):
                                pass
                            else:
                                x['hdp'] = str(-float(x['hdp']))
    logger.info('%s', x)
    #response = place_bet(base_url, username, password, x)
    ##response = dict()
    ##response['status'] = 'ACCEPTED'
    ##response['price'] = 1.917
    #logger.info('%s', response)
    pick = x['away'] if x['team'] == 'TEAM1' else x['home']
    line = x['hdp'] if float(x['hdp'])<0 else '+'+x['hdp']
    message = '#NBA #algo picked {} {} {}'.format(pick, line, teams_abrv2emoji[pick])
    tweet(message)
    count -= 1
    '''if (response['status'] == 'ACCEPTED'):
        pick = x['away'] if x['team'] == 'TEAM1' else x['home']
        line = x['hdp'] if float(x['hdp'])<0 else '+'+x['hdp']
        message = '#NBA #algo picked {} {} @ {} {}'.format(pick, line, response['price'], teams_abrv2emoji[pick])
        tweet(message)
        count -= 1
    else:
        x['data'] = x['data'][:-1]
        sched.add_job(prepare_bet, trigger='date', run_date=datetime.now()+timedelta(minutes=5)-timedelta(hours=1), args=(x, games, sched,))'''
    #print(x)
    #dać jakieś zabezpieczenie na wypadek złego beta
    if count == 0:
        thread = Thread(target = shutdown, args=(sched,))
        thread.start()
        thread.join()


def prepare_training_set(train_set):
    """Prepares sets for algo to be trained on.

    Args:
        train_set: Training data (seasons 2003-2016).

    Returns:
        X_train: Inputs.
        Y_train: Outputs.

    """
    logger.info('Preparing data sets...')
    l = []
    with open(train_set, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            l.append(row)
    inputs = []
    labels = []
    for row in l:
        ostatni = row.pop()
        if ostatni == "1":
            labels.append(1)
        else:
            labels.append(0)
        rest = [float(elem) for elem in row]
        inputs.append(rest)
    X_train = np.array(inputs)
    Y_train = np.array(labels)
    logger.info('Data sets prepared')
    return X_train, Y_train


def prevent_inactivity():
    t = threading.Timer(1200, prevent_inactivity)
    t.start()
    global count
    if (count > 0):
        #deleted path to nmap
        nm = nmap.PortScanner()
        n = nm.scan(hosts='algonba.herokuapp.com', arguments='-sP')
        #logger.info('%s', n)


def set_scheduler(games, raw, sched):
    """Sets scheduler.

    Args:
        sched: BlockingScheduler.
        games: List of dictionaries with game data.

    """
    logger.info('Setting scheduler...')
    i = 5
    for game in games:
        if (bool(time.localtime().tm_isdst) == False):
            #czas zimowy
            run_time = datetime.now()+timedelta(seconds=i)-timedelta(hours=1)
        else:
            #czas letni
            run_time = datetime.now()+timedelta(seconds=i)-timedelta(hours=2)
        #run_time = game['starts']+timedelta(seconds=i)
        #sched.add_job(prepare_bet, args=(game, raw, sched, count,))
        #sched.add_job(prepare_bet, trigger='date', run_date=run_time, args=(game, raw, sched, count,))
        sched.add_job(prepare_bet, trigger='date', run_date=run_time, args=(game, raw, sched,))
        #i += 1
        i += 15
    logger.info('Scheduler set')
    logger.info('%s', sched.print_jobs())
    #sched.print_jobs()
    #sched.start()


def shutdown(sched):
    """Shutdowns scheduler.

    Args:
        sched: BlockingScheduler.

    """
    logger.info('All bets placed, exiting...')
    #print("All bets placed, exiting...")
    sched.shutdown(wait=False)
    logger.info('Scheduler stopped')
    #print("Scheduler stopped.")


def tweet(message):
    consumer_key        = 'YOUR CONSUMER KEY'
    consumer_secret     = 'YOUR CONSUMER SECRET'
    access_token        = 'YOUR ACCESS TOKEN'
    access_token_secret = 'YOUR ACCESS TOKEN SECRET'

    #message = "Hello,\nHow are you doing today"

    api = login_to_twitter(consumer_key, consumer_secret, access_token, access_token_secret)
    logger.info('%s', message)
    ret = api.update_status(status=message)


def validate_spread():
    """Validates spreads using covers website (because Pinnacle's api sometimes gives wrong data).

    Returns:
        spreads: Dictionary with keys: away team name and spread as a value.

    """
    url = 'http://www.covers.com/odds/basketball/nba-spreads.aspx'
    f1 = urlopen(url).read().decode('utf-8')
    f2 = f1.split('\n')
    url_list = []
    soup = BeautifulSoup(f1, "lxml")
    scores = soup.find("div", attrs={"class":"CustomOddsContainer"})
    scores = scores.find("table").findAll('tr')
    #teamy dobrze
    teams = re.findall('<strong>(.*?)<', str(scores))
    #print(teams)
    teams = [x.strip('@') for x in teams]
    #print(teams)
    #print(teams[::2])
    teams = deque(teams[::2])
    #for link in scores.findAll('a', href=True, text='http://www.covers.com/WhereToPlay/SportsbookRedirect?sportsbookId=37&location=Covers Featured Odds'):
    #    print(link)
    spreads = dict()
    #spreads = []
    for link in soup.findAll('a', href=True):
        if(link['href'] == 'http://www.covers.com/WhereToPlay/SportsbookRedirect?sportsbookId=37&location=Covers Featured Odds'):
            if (link.find("div", attrs={"class":"offshore"})):
                #wyciągam oddsy z pinka, działa
                #print(link.find("div", attrs={"class":"offshore"}).contents[0].strip())
                spreads[teams_covers2full[teams.popleft()]] = link.find("div", attrs={"class":"offshore"}).contents[0].strip()
                #spreads.append({'away': teams.popleft(), 'spread': link.find("div", attrs={"class":"offshore"}).contents[0].strip()})
    #for elem in spreads:
        #print(elem)
    return spreads


if __name__ == "__main__":
    global count
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('Script started')
    base_url = 'https://api.pinnaclesports.com'
    username = 'YOUR PINNACLE USERNAME'
    password = 'YOUR PINNACLE PASSWORD'
    stake = 0

    sched = initiate_scheduler()
    ws = open_sheet()
    training_sheet = 'z_nd_nba_train_set_0316.csv'
    X_train, Y_train = prepare_training_set(training_sheet)

    games = get_start_times()
    count = len(games)

    games_ids = get_ids(games)
    for game in games:
        get_data(game, games_ids, ws)

    set_scheduler(games, games_ids, sched)

    #t = threading.Timer(1200, prevent_inactivity)
    #t.start()

    sched.start()
