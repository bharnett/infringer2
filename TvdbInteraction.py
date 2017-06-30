from tvdbrest.client import TVDB
import pytvmaze


class tvdb(object):
    """class for calling tvdb"""
    def __init__(self):
        self.api_key = 'EFF4CBD618B5C756'
        self.userkey = '3BBD3F7E1043129C'
        self.username = 'bharnett1825'
        self.api = TVDB(self.username, self.userkey, self.api_key)
        self.api.login()
        self.tvm = pytvmaze.TVMaze()

    def search_show(self, show_name):
        results = self.api.search(name=show_name)
        returned_shows=[]
        for show in results:
            returned_shows.append(search_result(show))
        return returned_shows

    def get_show_images(self, show_id):
        # parse the TVDB banner?
        # then hit fanart.tv for more images and pass some class back to the database.
        # get show poster, banner, thumb, season poster, season thumb, and background
        show = self.tvm.get_show(tvdb_id=show_id)
        return show.image

    def get_updates(self, last_update):
        x = 'y'
        # get updates from tvdb
        # arse for series in the user's database
        # add shows that don't exist, then update existing shows with the data based on id
        # make sure to get updated show images too for new seasons

    def get_trending(self):
        x = 'y'

        # use trakt tv api for this
        # filter shows that are currently in the user's database so they don't show up.

    def get_upcoming_premiers(self):
        x = 'y'

        # use the movie database api for this, only for english
        # filter shows that are currently in the user's database so they don't show up.


class search_result(object):
    """container for search results"""
    def __init__(self, show):
        self.name = show.seriesName
        self.premier_date = show.firstAired
        self.network = show.network  # TODO handle blanks/empty values

    def __str__(self):
        return '%s on %s at %s' % (self.name, self.network, self.premier_date)

t = tvdb()
result = t.search_show('girl')
images = t.get_show_images(result[0].id)

