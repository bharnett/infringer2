from tvdbrest.client import TVDB
import requests
import json
import tmdbsimple
import datetime


class Contentor(object):
    """class for calling tvdb"""
    def __init__(self):
        self.tvdb_api_key = 'EFF4CBD618B5C756'
        self.tvdb_userkey = '3BBD3F7E1043129C'
        self.tvdb_username = 'bharnett1825'
        self.api = TVDB(self.tvdb_username, self.tvdb_userkey, self.tvdb_api_key)
        self.api.login()
        self.fanart_api_key = 'bdb9e6a92d25c43e88a7ad36d835a715'
        self.tmdb_api_key = '79f408a7da4bdb446799cb45bbb43e7b'
        self.trakt_api_key = 'e9f4942e8fbd766b00017b445af15349ead0d483521fec6cd35af40256e8d744'

    def search_show(self, show_name):
        results = self.api.search(name=show_name)
        returned_shows=[]
        for show in results:
            returned_shows.append(SearchResult(show))
        return returned_shows

    def get_show_images(self, show_id):
        # this should only be done once, when the show is added.  Any other images
        # should be part of the update process
        endpoint = 'http://webservice.fanart.tv/v3/tv/%s?api_key=%s' % (show_id, self.fanart_api_key)
        fanart_request = requests.get(endpoint)

        if (fanart_request.ok):
            arts = json.loads(fanart_request.content)
            return arts
        else:
            return None

        # hit fanart.tv for more images and pass some class back to the database.
        # get show poster, banner, thumb, season poster, season thumb, and background

    def get_season_artwork(self, show_id, season_number):
        arts = self.get_show_images(show_id)
        if arts is not None and len(arts['seasonposter']) >= season_number - 1:
            return arts['seasonposter'][season_number - 1]
        else:
            return arts['tvposter'][0]

    def get_updates(self, show_id, last_update):
        show = self.api.series(show_id)
        if show.last_updated >= last_update:
            return show.episodes()
        else:
            return []


        # epoch_time = str(last_update.timestamp()).split('.')[0]  # get epoch time without milliseconds
        # updates = self.api.updates(epoch_time)
        # for u in updates:
        #     print(u)
        # x = 'y'
        # get updates from tvdb
        # parse for series in the user's database
        # add shows that don't exist, then update existing shows with the data based on id
        # make sure to get updated show images too for new seasons
    #
    # def get_trending(self):
    #     trakt.APPLICATION_ID = self.trakt_api_key
    #     trakt.init()
    #     x = 'y'
    #
    #     # use trakt tv api for this
    #     # filter shows that are currently in the user's database so they don't show up.

    def get_popular(self):
        tmdb = tmdbsimple
        tmdb.API_KEY = self.tmdb_api_key
        tv = tmdb.TV()
        pop = tv.popular(language='en-US')
        total_pages = pop['total_pages'] + 1
        popular_list = []
        if total_pages > 39:
            total_pages = 39 # keep it under limit, we really don't need more than 40 pages of this stuff

        for i in range(2, total_pages):
            shows = pop['results']
            for show in shows:
                if show['original_language'] == 'en':
                    # add the show because it is in the future
                    popular_list.append(show)
            pop = tv.popular(language='en-US', page=i)

        return popular_list

    def get_upcoming_premiers(self):
        tmdb = tmdbsimple
        tmdb.API_KEY = self.tmdb_api_key
        tv = tmdb.TV()
        air = tv.on_the_air(language='en-US')
        total_pages = air['total_pages'] + 1
        list_of_premiers = []

        for i in range(2, total_pages):
            shows = air['results']
            for show in shows:
                if show['first_air_date'] >= str(datetime.date.today()) and show['original_language'] == 'en':
                    # add the show because it is in the future
                    list_of_premiers.append(show)
            air = tv.airing_today(language='en-US', page=i)

        return list_of_premiers
        # filter shows that are currently in the user's database after data is returned


class SearchResult(object):
    """container for search results"""
    def __init__(self, show):
        self.name = show.seriesName
        self.premier_date = show.firstAired
        self.network = show.network  # TODO handle blanks/empty values

    def __str__(self):
        return '%s on %s at %s' % (self.name, self.network, self.premier_date)




# t = tvdb()
# result = t.search_show('girl')
# images = t.get_show_images(result[0].id)

c = Contentor()
c.get_show_images(273181)

# tester = c.get_upcoming_premiers()

# time = datetime.datetime.now() - datetime.timedelta(days=7)

# c.get_updates(time, [])

#c.get_popular()





