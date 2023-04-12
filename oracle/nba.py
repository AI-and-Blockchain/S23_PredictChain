import nba_api

from nba_api.live.nba.endpoints import scoreboard

from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2

game_id = '0022201216' # replace with the game ID you want to retrieve the box score for

box_score = BoxScoreTraditionalV2(game_id=game_id)
data = box_score.get_data_frames()

print(data[0]) # prints the team stats
print(data[1]) # prints the player stats
