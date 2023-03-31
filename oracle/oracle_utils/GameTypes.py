import pandas as pd

class NonFinalError(Exception):
    "Raised when the input game is not complete."
    pass
        

class NCAAGame:
    def __init__(self, html=None,game=None):
        if game is not None:
            self.copy_constructor(game)
            return
        if html.find(class_='gamePod-status').text not in ["FINAL (OT)", "FINAL"]:
            raise NonFinalError
        teams = html.find_all(class_='gamePod-game-team-name')
        scores = html.find_all(class_='gamePod-game-team-score')
        
        teams = [t.text for t in teams]
        scores = [int(s.text) for s in scores]
        
        self.away_team = teams[0]
        self.away_score = scores[0]
        
        self.home_team = teams[1]
        self.home_score = scores[1]
        
        self.winner, self.loser = (teams[0],teams[1]) if scores[0] > scores[1] else (teams[1],teams[0])
        
        self.link = html.find(class_="gamePod-link").attrs['href']
        self.id = self.link[-7:]
        
        self.date = None
        
    def copy_constructor(self,game):
        self.away_team = game.away_team
        self.home_team = game.home_team
        
        self.away_score = game.away_score
        self.home_score = game.home_score
        
        self.link = game.link
        self.date= game.date
        
        self.winner, self.loser =  (self.away_team, self.home_team) if self.away_score > self.home_score else (self.home_team, self.away_team)
        
    def set_date(self, date):
        self.date = date
        
    def __str__(self):
        return f"{self.date}\n{self.away_team}: {self.away_score} \n{self.home_team}: {self.home_score}"

    def __repr__(self):
        return self.__str__()

class StatsGame(NCAAGame):
    def __init__(self, html, id_):
        dfs = pd.read_html(html)

        if len(dfs) == 6:
            self.info = dfs.pop(1).loc[0,0]
        
        #get Play by Play link
        dom = etree.HTML(html)
        self.pbp_id = dom.xpath('/html/body/div[2]/div[3]/div/div/ul/li[3]/a')[0].attrib['href'][-7:]
        self.id_ = id_
        # 1: Time, Location, Attendence
        df = dfs[1]
        df = df.set_index(0).T
        try:
            self.date = df.loc[1,'Game Date:']
            self.date = datetime.datetime.strptime(self.date, '%m/%d/%Y %I:%M %p')
        except:
            self.date = None
        try:
            self.attendence = int(df.loc[1,'Attendance:'])
        except:
            self.attendence = None
        try:
            self.location = df.loc[1,'Location:']
        except:
            self.location = None    
        del df
        # 2: Officials - dfs not used
        officials = "".join(dom.xpath('/html/body/div[2]/table[4]')[0].getchildren()[0].getchildren()[0].getnext().itertext())
        self.officials = officials.strip().split('\n        \n        ')

        # 3: Away Stats
        away_df = dfs[3]
        self.away_team = away_df.loc[0,0]
        away_df.columns = away_df.loc[1]
        away_df.drop([0,1], inplace=True)
        away_df.reset_index(inplace=True, drop=True)
        self.away_df = away_df
        
        # 3: Home Stats
        home_df = dfs[4]
        self.home_team = home_df.loc[0,0]
        home_df.columns = home_df.loc[1]
        home_df.drop([0,1], inplace=True)
        home_df.reset_index(inplace=True, drop=True)
        self.home_df = home_df
        
        # 0: Scoring By Half 
        df = dfs[0]
        df.columns = df.loc[0]
        df.drop(0, inplace=True)
        df.iloc[0,0] = away_team
        df.iloc[1,0] = home_team
        df.set_index(df.columns[0])
        df[df.columns[1:]] = df[df.columns[1:]].astype(int)
        self.half_scores = df
        del df
        
        self.away_score = self.half_scores.loc[1,'Total']
        self.home_score = self.half_scores.loc[2,'Total']
        
        self.winner, self.loser =   (self.away_team, self.home_team) if self.away_score > self.home_score else (self.home_team, self.away_team)
        
class Team:
    def __init__(self, name):
        self.games = []
        self.name = name

        self.conference = None

    def add_game(self, game):
        assert(self.name in [game.home_team, game.away_team])

        self.games.append(game)