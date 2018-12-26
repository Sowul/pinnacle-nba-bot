teams_abrv = [
 'ATL',
 'BOS',
 'BRK',
 'CHI',
 'CHO',
 'CLE',
 'DAL',
 'DEN',
 'DET',
 'GSW',
 'HOU',
 'IND',
 'LAC',
 'LAL',
 'MEM',
 'MIA',
 'MIL',
 'MIN',
 'NOP',
 'NYK',
 'OKC',
 'ORL',
 'PHI',
 'PHO',
 'POR',
 'SAC',
 'SAS',
 'TOR',
 'UTA',
 'WAS']

teams_full = [
 'Atlanta Hawks',
 'Boston Celtics',
 'Brooklyn Nets',
 'Chicago Bulls',
 'Charlotte Hornets',
 'Cleveland Cavaliers',
 'Dallas Mavericks',
 'Denver Nuggets',
 'Detroit Pistons',
 'Golden State Warriors',
 'Houston Rockets',
 'Indiana Pacers',
 'Los Angeles Clippers',
 'Los Angeles Lakers',
 'Memphis Grizzlies',
 'Miami Heat',
 'Milwaukee Bucks',
 'Minnesota Timberwolves',
 'New Orleans Pelicans',
 'New York Knicks',
 'Oklahoma City Thunder',
 'Orlando Magic',
 'Philadelphia 76ers',
 'Phoenix Suns',
 'Portland Trail Blazers',
 'Sacramento Kings',
 'San Antonio Spurs',
 'Toronto Raptors',
 'Utah Jazz',
 'Washington Wizards'
]

teams_covers = [
 'Atlanta',
 'Boston',
 'Brooklyn',
 'Chicago',
 'Charlotte',
 'Cleveland',
 'Dallas',
 'Denver',
 'Detroit',
 'Golden State',
 'Houston',
 'Indiana',
 'L.A. Clippers',
 'L.A. Lakers',
 'Memphis',
 'Miami',
 'Milwaukee',
 'Minnesota',
 'New Orleans',
 'New York',
 'Oklahoma City',
 'Orlando',
 'Philadelphia',
 'Phoenix',
 'Portland',
 'Sacramento',
 'San Antonio',
 'Toronto',
 'Utah',
 'Washington'
]

teams_emoji = [
 '#TrueToAtlanta',
 '#Celtics',
 '#BrooklynGrit',
 '#BullsNation',
 '#BuzzCity',
 '#DefendTheLand',
 '#MFFL',
 '#MileHighBasketball',
 '#DetroitBasketball',
 '#DubNation',
 '#Rockets',
 '#GoPacers',
 '#ItTakesEverything',
 '#LakeShow',
 '#GrindCity',
 '#HEATIsOn',
 '#OwnTheFuture',
 '#PowerOfThePack',
 '#Pelicans',
 '#Knicks',
 '#ThunderUp',
 '#LetsGoMagic',
 '#MADEinPHILA',
 '#WeArePHX',
 '#RipCity',
 '#SacramentoProud',
 '#GoSpursGo',
 '#WeTheNorth',
 '#TakeNote',
 '#DCFamily'
]

teams_abrv2full = dict()
teams_full2abrv = dict()
teams_covers2full = dict()
teams_abrv2emoji = dict()

for a, b in zip(teams_abrv, teams_full) :
    #print('{} - {}'.format(a, b))
    teams_abrv2full[a] = b

for a, b in zip(teams_abrv, teams_full) :
    #print('{} - {}'.format(a, b))
    teams_full2abrv[b] = a

for a, b in zip(teams_covers, teams_full) :
    #print('{} - {}'.format(a, b))
    teams_covers2full[a] = b

for a, b in zip(teams_abrv, teams_emoji) :
    #print('{} - {}'.format(a, b))
    teams_abrv2emoji[a] = b
