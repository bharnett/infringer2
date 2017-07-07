from tvdbrest.client import TVDB
import requests
import json
import tmdbsimple
import datetime
import html
import time


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
        returned_shows = []
        for show in results:
            returned_shows.append(SearchResult(show))
        return returned_shows

    def get_show(self, show_id):
        return self.api.series(show_id)

    def get_show_images(self, show_id):
        # this should only be done once, when the show is added.  Any other images
        # should be part of the update process
        endpoint = 'http://webservice.fanart.tv/v3/tv/%s?api_key=%s' % (show_id, self.fanart_api_key)
        fanart_request = requests.get(endpoint)

        if fanart_request.ok:
            arts = json.loads(fanart_request.content.decode('latin'))
            return_arts = Artworks()
            return_arts.pop_arts(arts)
            return return_arts

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

    def get_movie_details(self, movie_text, year=''):
        tmdb = tmdbsimple
        tmdb.API_KEY = self.tmdb_api_key
        search = tmdb.Search()
        search_results = search.movie(query=html.escape(movie_text), year=year)
        if search_results['total_results'] > 0:
            movie = search_results['results'][0]
            cast = tmdb.Movies(movie['id']).credits()['cast']
        else:
            return None
        # cast_members = []
        # for member in cast[0:4]:
        #     cast_members.append(member['name'])

        return MovieDetails(movie, cast)

    def get_popular(self):
        tmdb = tmdbsimple
        tmdb.API_KEY = self.tmdb_api_key
        tv = tmdb.TV()
        pop = tv.popular(language='en-US')
        total_pages = pop['total_pages'] + 1
        popular_list = []
        if total_pages > 5:
            total_pages = 5  # keep it under limit, we really don't need more than 40 pages of this stuff

        for i in range(2, total_pages):
            shows = pop['results']
            for show in shows:
                air_date = datetime.datetime.strptime(show['first_air_date'], '%Y-%m-%d')
                if show['original_language'] == 'en' and \
                                air_date >= datetime.datetime.now() + datetime.timedelta(weeks=-624):
                    # add the show because it is in the future
                    popular_list.append(show)
            pop = tv.popular(language='en-US', page=i)

        return popular_list, self.get_tvdb_ids(tmdb, popular_list)

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

        return list_of_premiers, self.get_tvdb_ids(tmdb, list_of_premiers)
        # filter shows that are currently in the user's database after data is returned

    def get_tvdb_ids(self, tmdb, list):
        tvdb_links = []
        i = 5
        for s in list:
            if i == 5: #added in a sleep function for rate limiting on api
                time.sleep(5)
                i = 0
            tvdb_id = tmdb.TV(s['id']).external_ids()['tvdb_id']
            tvdb_links.append(tvdb_id)
            i += 1
        return tvdb_links


class SearchResult(object):
    """container for search results"""

    def __init__(self, show):
        self.name = show.seriesName
        self.premier_date = show.firstAired
        self.network = show.network  # TODO handle blanks/empty values

    def __str__(self):
        return '%s on %s at %s' % (self.name, self.network, self.premier_date)


class MovieDetails(object):
    def __init__(self, movie_response, cast_response):
        self.movie = movie_response
        self.cast = []

        for member in cast_response[0:4]:
            self.cast.append(member['name'])


class Artworks(object):
    """container for show & season artwork"""

    def __init__(self):
        self.background = ''
        self.show_poster = ''
        self.show_thumb = ''
        self.show_banner = ''
        self.show_large = ''
        self.seasons_posters = []
        # self.seasons_thumbs = []

    def pop_arts(self, art):
        self.background = art['showbackground'][0]['url'] if 'showbackground' in art.keys() else ''
        self.show_poster = art['tvposter'][0]['url'] if 'tvposter' in art.keys() else ''
        self.show_thumb = art['tvthumb'][0]['url'] if 'tvthumb' in art.keys() else ''
        self.show_banner = art['tvbanner'][0]['url'] if 'tvbanner' in art.keys() else ''
        self.show_large = art['hdclearart'][0]['url'] if 'hdclearart' in art.keys() else ''
        if 'seasonposter' in art.keys():
            for p in art['seasonposter']:
                self.seasons_posters.append(p['url'])

# t = tvdb()
# result = t.search_show('girl')
# images = t.get_show_images(result[0].id)

# c = Contentor()
# # s = c.get_show(273181)
# # c.get_show_images(273181)
# x = c.get_popular()
# y = c.get_upcoming_premiers()
#
# c.get_movie_details('kong skull island')

# tester = c.get_upcoming_premiers()

# time = datetime.datetime.now() - datetime.timedelta(days=7)

# c.get_updates(time, [])

# c.get_popular()
