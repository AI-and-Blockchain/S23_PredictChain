import oracleUtils.PullResults as PullResults
# Class to listen for real world events and send reflexive transactions to the oracle for processing


def report(game):
	"""
	Function to report the gathered information back. TBD.
	"""
	pass


def checkNCAAEvents(events: list[str], start_date, end_date):
	links = PullResults.gen_day_links(start_date, end_date)
	games = PullResults.get_results(links)

	for game in games:
		if game.id in events:
			report(game)
