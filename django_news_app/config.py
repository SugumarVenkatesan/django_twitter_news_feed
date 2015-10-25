import enum


@enum.unique
class NewsList(enum.IntEnum):
    BreakingNews = 1 
    CNNBrk = 2
    CBSTopNews = 3
    BBCBreaking = 4
    WSJbreakingnews = 5
    ABCNewsLive = 6
    BuzzFeedNews = 7
    BreakingTweets = 8    
    diggtop = 9
    BreakingNewsStorm = 10
    NDTV = 11
    CNBC = 12
    starsports = 13
    
    def ui_return(self):
        return ' '.join(self.name.split('_')).lower()
    
