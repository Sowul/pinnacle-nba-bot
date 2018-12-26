# pinnacle-nba-bot
Quick and dirty template for Pinnacle NBA bot using Google Spreadsheet as a database and running on Heroku Free.<br>
Since our beloved polish government banned so called gambling and I can't use Pinnacle anymore ;) (but rigged lotto lottery is perfectly legal even though your odds of winning it are almost non-existent) I've decided to dump the code. It worked pretty well in 2016-17 NBA season. Enjoy.<br>
 __Warning:__ I invested about 3 man-hours into this ugly-looking code. As you can see, it's full of comments and commented out blocks of code. I was "testing" it on the fly. And somehow it worked, even though it's awfully slow. Don't use it.<br>
 __Good advice:__ If you own a server, just rewrite these scripts - cron, at and sql database are so much easier to work with than Heroku.<br>
 __Disclaimer:__ I accepts no responsibility or liability for any losses which may be incurred by any person or persons using the whole or part of the contents of this software, i.e. don't blame me for lost money.<br>

## EDIT
I don't think it works anymore, because the code relies heavily on scraping basketball-reference.com for data and the site changed its layout quite significantly since I had been using this. Hopefully, the code could serve as a starting point for building a tool for executing your bets.

## Prerequisites
```
$ pip install -r requirements.txt
```
If you want to tweet your bets, you have to authorize tweepy, check this [link](https://tweepy.readthedocs.io/en/v3.5.0/auth_tutorial.html).
To access Google Sheets, first [obtain OAuth2 credentials from Google Developers Console](https://gspread.readthedocs.io/en/latest/oauth2.html).
To place bets, you need Pinnacle Sports account with available funds.