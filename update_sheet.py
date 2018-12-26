from datetime import date, datetime, timedelta
import re
import string
import sys
import time
from urllib.request import urlopen

from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('AlgoNBA-488be4605440.json', scope)
gc = gspread.authorize(credentials)
sh = gc.open('4FACTORS_1617.xlsx')

def calc_elo(away_pts, away_elo, home_pts, home_elo, K=20):
    #https://fivethirtyeight.com/features/how-we-calculate-nba-elo-ratings/
    #https://en.wikipedia.org/wiki/World_Football_Elo_Ratings
    MOV = away_pts - home_pts
    underdog = 'A' if away_elo < home_elo else 'H'
    if (underdog == 'A'):
        elo_diff = away_elo-100-home_elo if MOV > 0 else abs(away_elo-100-home_elo)
    else:
        elo_diff = away_elo-100-home_elo if MOV > 0 else -(away_elo-100-home_elo)
    difference = (abs(MOV) + 3)**0.8/(7.5+0.006*elo_diff)
    We = 1/(10**(-elo_diff/400)+1)
    point_change = K*difference*(1-We)
    if MOV < 0:#home win
        new_away_elo = away_elo - point_change
        new_home_elo = home_elo + point_change
    else:#away win
        new_away_elo = away_elo + point_change
        new_home_elo = home_elo - point_change
    return new_away_elo, new_home_elo

#worksheet = sh.worksheet('Input')
#val = worksheet.cell(1, 3).value
#print(val)

def update_sheet(today=date.today()):
    ws = sh.worksheet("bety_clean")
    if (ws.acell("K3").value == "UPDATED"):
        print("Sheet is up to date.")
    else:
        season = 2017
        if(season == today.year):
            if(today.month >= 10):
                season = season + 1
            else:
                pass
        else:
            pass
        yesterday = today - timedelta(1)
        month = '-'+yesterday.strftime("%B").lower()
        yesterday = yesterday.strftime("%Y%m%d")

        #Open the webpage with the 2016-2017 NBA stats, use 2nd year in below code ie. 2017
        url = 'http://www.basketball-reference.com/leagues/NBA_'+\
            str(season)+'_games'+str(month)+'.html'
        f1 = urlopen(url).read().decode('utf-8')
        f2 = f1.split('\n')
        url_list = []

        #Create a list of urls with the box scores
        for i in range(len(f2)):
            if re.search("Box Score", f2[i]):
                if(yesterday in re.search('(?<=href=").{28}(?=")', f2[i]).group(0)):
                    url_list += ["http://www.basketball-reference.com"
                        + re.search('(?<=href=").{28}(?=")', f2[i]).group(0)]
        #print(url_list)

        #Navigate to each website to extract data
        for i in range(len(url_list)):
            f1 = urlopen( url_list[ i ] ).read( ).decode('utf-8')

            #Use regular expressions and soup to find and extract data
            game_id = re.search('(?<=boxscores/).+?(?=.html)', url_list[i]).group(0)

            soup = BeautifulSoup(f1, "lxml")
            scores = soup.find("div", attrs={"id":"all_line_score"})
            scores = re.findall('<strong>(.*?)<', str(scores))
            away_pts = int(scores[0])
            home_pts = int(scores[1])

            rows = soup.find("div", attrs={"id":"all_four_factors"})
            rows = re.findall('\<tr >.*?\<\/tr>', str(rows))
            cells = re.findall('>(.*?)<', str(rows))
            cells = [item for item in cells if len(item)>1]
            #delete "', '"
            del cells[7]
            #print(cells, len(cells))
            cells = [cells[:7], cells[7:]]
            #['HOU', '90.9', '.507', '12.0', '35.9', '.466', '118.8', 'LAL', '90.9', '.373', '10.3', '25.0', '.392', '99.0']
            worksheet_A = sh.worksheet(cells[0][0])
            worksheet_H = sh.worksheet(cells[1][0])

            #check which row_A, row_H
            row_A = [elem for elem in worksheet_A.col_values(17) if elem]
            away_elo = float(row_A[-1])
            row_A = len([elem for elem in row_A if elem])
            row_H = [elem for elem in worksheet_H.col_values(17) if elem]
            home_elo = float(row_H[-1])
            row_H = len([elem for elem in row_H if elem])

            new_away_elo, new_home_elo = calc_elo(away_pts, away_elo, home_pts, home_elo)

            worksheet_A.update_cell(row_A, 9, game_id)
            worksheet_A.update_cell(row_A, 11, (float(cells[0][2])-float(cells[1][2])))
            worksheet_A.update_cell(row_A, 12, (float(cells[0][3])-float(cells[1][3])))
            worksheet_A.update_cell(row_A, 13, (float(cells[0][4])-float(cells[1][4])))
            worksheet_A.update_cell(row_A, 14, (float(cells[0][5])-float(cells[1][5])))
            worksheet_A.update_cell(row_A, 15, (float(cells[0][6])-float(cells[1][6])))
            worksheet_A.update_cell(row_A, 18, away_pts+home_pts)
            worksheet_A.update_cell(row_A, 20, home_elo)
            worksheet_A.update_cell(row_A+1, 17, new_away_elo)

            worksheet_H.update_cell(row_H, 9, game_id)
            worksheet_H.update_cell(row_H, 11, -(float(cells[0][2])-float(cells[1][2])))
            worksheet_H.update_cell(row_H, 12, -(float(cells[0][3])-float(cells[1][3])))
            worksheet_H.update_cell(row_H, 13, -(float(cells[0][4])-float(cells[1][4])))
            worksheet_H.update_cell(row_H, 14, -(float(cells[0][5])-float(cells[1][5])))
            worksheet_H.update_cell(row_H, 15, -(float(cells[0][6])-float(cells[1][6])))
            worksheet_H.update_cell(row_H, 18, away_pts+home_pts)
            worksheet_H.update_cell(row_H, 20, away_elo)
            worksheet_H.update_cell(row_H+1, 17, new_home_elo)
            print(game_id)
        ws.update_acell("K2", today.strftime("%m/%d/%Y"))
        if (ws.acell("K3").value == "UPDATED"):
            print("Sheet is up to date.")
        else:
            print("Sheet has still not been up to date.")


if __name__ == '__main__':
    start_time = time.time()
    import datetime
    start = datetime.datetime.strptime("26-10-2016", "%d-%m-%Y")
    end = datetime.datetime.strptime("14-04-2017", "%d-%m-%Y")
    date_generated = (start + datetime.timedelta(days=x) for x in range(0, (end-start).days))
    for date in date_generated:
        update_sheet(date)
    #update_sheet()
    print(round((time.time() - start_time)/60, 2))
