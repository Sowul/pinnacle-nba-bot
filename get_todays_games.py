from datetime import date, datetime, timedelta
import re
import string
import sys
import time
from urllib.request import urlopen

from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('AlgoNBA-488be4605440.json', scope)
gc = gspread.authorize(credentials)
sh = gc.open('4FACTORS_1617.xlsx')

def get_todays_games(today=date.today()):
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

        #Open the webpage with the 2016-2017 NBA stats, use 2nd year in below code ie. 2017
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
        print(time_zone)
        print(today)
        for score in scores:
            temp = re.findall('(?<=time">).+(?=</td>)', str(score))[0]
            separator = temp.index('<')
            start_time = today + ' ' + temp[:separator].replace(' ', '').upper()
            datetime_object = datetime.strptime(start_time, '%Y%m%d %I:%M%p')
            #print(datetime_object)
            datetime_object = datetime_object - timedelta(minutes=15)
            #print(datetime_object)
            datetime_object = local_tz.localize(datetime_object).astimezone(pytz.UTC)
            #print(datetime_object)
            teams = re.findall('(?<=csk=").{16}(?=")', str(score))
            #print(teams)
            games.append({'starts': datetime_object,
                          'away': teams[0][:3],
                          'home':teams[1][:3],
                          'game_id': teams[0][4:]})
        from operator import itemgetter
        games = sorted(games, key=itemgetter('starts'))

        ws = sh.worksheet("bety_clean")
        row = [elem for elem in ws.col_values(1) if elem]
        row = len([elem for elem in row if elem])+1

        if (ws.acell("K3").value == "UPDATED"):
            for i in range(1, row):
                #clear ws
                ws.update_cell(i, 1, '')
                ws.update_cell(i, 2, '')
                ws.update_cell(i, 3, '')
                ws.update_cell(i, 4, '')
                ws.update_cell(i, 5, '')
                ws.update_cell(i, 6, '')
                ws.update_cell(i, 7, '')
            #wyciągnąć dane i wrzucić do arkusza
            #ustawić crona
            i = 1
            for game in games:
                worksheet_A = sh.worksheet(game['away'])
                row_A = [elem for elem in worksheet_A.col_values(17) if elem]
                row_A = len([elem for elem in row_A if elem])
                worksheet_H = sh.worksheet(game['home'])
                row_H = [elem for elem in worksheet_H.col_values(17) if elem]
                row_H = len([elem for elem in row_H if elem])
                worksheet_i = sh.worksheet('Input')
                row_i = [elem for elem in worksheet_i.col_values(1) if elem]
                row_i = len([elem for elem in row_i if elem])+1
                ###
                worksheet_i.update_cell(row_i, 1, game['game_id'])
                worksheet_i.update_cell(row_i, 2, game['away'])
                worksheet_i.update_cell(row_i, 3, game['home'])
                #updating Input
                worksheet_i.update_cell(row_i, 4, worksheet_A.cell(row_A, 1).value)
                worksheet_i.update_cell(row_i, 5, worksheet_A.cell(row_A, 2).value)
                worksheet_i.update_cell(row_i, 6, worksheet_A.cell(row_A, 3).value)
                worksheet_i.update_cell(row_i, 7, worksheet_A.cell(row_A, 4).value)
                worksheet_i.update_cell(row_i, 8, worksheet_A.cell(row_A, 5).value)
                worksheet_i.update_cell(row_i, 10, worksheet_A.cell(row_A, 7).value)
                worksheet_i.update_cell(row_i, 11, worksheet_A.cell(row_A, 8).value)
                #
                worksheet_i.update_cell(row_i, 12, worksheet_H.cell(row_H, 1).value)
                worksheet_i.update_cell(row_i, 13, worksheet_H.cell(row_H, 2).value)
                worksheet_i.update_cell(row_i, 14, worksheet_H.cell(row_H, 3).value)
                worksheet_i.update_cell(row_i, 15, worksheet_H.cell(row_H, 4).value)
                worksheet_i.update_cell(row_i, 16, worksheet_H.cell(row_H, 5).value)
                worksheet_i.update_cell(row_i, 18, worksheet_H.cell(row_H, 7).value)
                worksheet_i.update_cell(row_i, 19, worksheet_H.cell(row_H, 8).value)
                #worksheet_i.update_cell(row_i, 20, ) -> elospread, liczony
                #worksheet_i.update_cell(row_i, 22, ) -> spread z pinka
                #updating ws
                ws.update_cell(i, 1, worksheet_i.cell(row_i, 8).value)
                ws.update_cell(i, 2, worksheet_i.cell(row_i, 16).value)
                ws.update_cell(i, 3, worksheet_i.cell(row_i, 20).value)
                #ws.update_cell(i, 4, )
                ws.update_cell(i, 5, 0)
                ws.update_cell(i, 6, worksheet_i.cell(row_i, 2).value)
                ws.update_cell(i, 7, worksheet_i.cell(row_i, 3).value)
                i += 1
        else:
            pass

if __name__ == '__main__':
    start_time = time.time()
    get_todays_games()
    print(round((time.time() - start_time)/60, 2))
