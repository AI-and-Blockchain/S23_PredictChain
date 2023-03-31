import datetime
from GameTypes import NCAAGame
import requests
import bs4
from GameTypes import NonFinalError
from bs4 import BeautifulSoup

opening_day = datetime.date(2022,11,7)
today = datetime.date.today()

date = opening_day

_DAY = datetime.timedelta(days=1)

AKAs = {
    'FDU' : 'Fairleigh Dickinson',
    'UConn': 'Connecticut',
    "Saint Mary's (CA)" : "Saint Mary's",
    "Southern California": "USC",
    "Col. of Charleston": "Charleston"
}
def tomorrow(date):
    return date + _DAY
def gen_day_links(start_date, end_date):
	date = start_date
	day_links = []
	while date <= end_date:
	    date_txt = date.strftime("%Y/%m/%d")
	    day_link = f"https://www.ncaa.com/scoreboard/basketball-men/d1/{date_txt}/all-conf"
	    day_links.append((date,day_link))
	    
	    date = tomorrow(date)

	return day_links

def rename(Games):
	for game in Games:
	    if game.away_team in AKAs:
	        game.away_team = AKAs[game.away_team]
	    if game.home_team in AKAs:
	        game.home_team = AKAs[game.home_team]
	    if game.winner in AKAs:
	        game.winner = AKAs[game.winner]
	    if game.loser in AKAs:
	        game.loser = AKAs[game.loser]


def get_results(day_links):
	Games = []
	f = open(fd,'w')
	for date,day_link in day_links:
	    r = requests.get(day_link)
	    soup = BeautifulSoup(r.text, 'html.parser')

	    games = soup.find_all(class_="gamePod_content-pod_container")
	    if len(games) == 0:
	        continue
	    games = [g for g in games[0].children  if type(g) == bs4.element.Tag ]

	    for game in games:
	        try:
	            G = NCAAGame(game)
	            G.set_date(date)
	            Games.append(G)
	        except NonFinalError:
	            pass
	rename(Games)

	return Games

	f.close()
def main():
	start = datetime.date(2023,3,14)
	end = min(datetime.date(2023,4,3), datetime.date.today() )
	links = gen_day_links(start, end)
	write_results(links)

if __name__ == '__main__':
	main()