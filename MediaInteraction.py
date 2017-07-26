import TvdbInteraction
from Models import Show, Episode, Movie, Config, ActionLog, PremierShow, PopularShow
import os
import datetime
import Models


def add_show(show_id, db):
    c = TvdbInteraction.Contentor()
    series = c.get_show(show_id)
    # episodes = series.episodes()
    # artwork = c.get_show_images(show_id)

    new_show = Show(show_id=series['id'],
                    show_name=series['name'],
                    first_aired=datetime.datetime.strptime(series['first_air_date'], '%Y-%m-%d'),
                    is_active=series['status'] != 'Ended',
                    overview=series['overview'],
                    banner="",
                    poster='https://image.tmdb.org/t/p/w185' + series['poster_path'],
                    thumb="",
                    background='https://image.tmdb.org/t/p/original' + series['backdrop_path'],
                    large_image='')

    new_show.make_regex()

    # create folder based on show name:
    new_show.show_directory = '/' + new_show.show_name.replace('.', '').strip()
    phys_directory = db.query(Config).first().tv_parent_directory + new_show.show_directory
    if not os.path.exists(phys_directory):
        os.makedirs(phys_directory)

    # add show before adding all the episodes
    db.add(new_show)
    db.commit()
    ActionLog.log('"%s" added.' % new_show.show_name)

    #add episodes
    for s in series['seasons']:
        season_number = s['season_number']
        if season_number == 0:
            continue
        else:
            season_detail = c.tmdb.TV_Seasons(series['id'], season_number).info()
            for e in season_detail['episodes']:
                add_episode(e, new_show, db, s)

    # for e in episodes:
    #     add_episode(e, new_show, db, c, artwork)

    db.commit()


def add_episode(tmdb_episode, db_show, db, season):
    # if c is None:
    #     c = TvdbInteraction.Contentor()
    #
    # if artwork is None:
    #     artwork = c.get_show_images(db_show.id)

    if tmdb_episode['season_number'] >= 1 and tmdb_episode['episode_number'] >= 1:
        first_aired = None if tmdb_episode['air_date'] is None else datetime.datetime.strptime(tmdb_episode['air_date'], '%Y-%m-%d')

        if first_aired is not None and first_aired >= datetime.datetime.now() + datetime.timedelta(days=-2):
            episode_retrieved = 'Pending'
        elif first_aired is None:
            episode_retrieved = 'Pending'
        else:
            episode_retrieved = 'Retrieved'

        if season['poster_path'] is not None:
            episode_art = 'https://image.tmdb.org/t/p/w185' + season['poster_path']
        else:
            episode_art = db_show.poster
        # try:
        #     if len(artwork.seasons_posters) > 0 and len(artwork.seasons_posters) >= tvdb_episode.airedSeason - 1:
        #         # get first season poster
        #         episode_art = artwork.seasons_posters[tvdb_episode.airedSeason - 1]
        #     else:
        #         episode_art = artwork.show_poster
        # except:
        #     episode_art = artwork.show_poster

        new_episode = Episode(id=tmdb_episode['id'],
                              season_number=tmdb_episode['season_number'],
                              episode_number=tmdb_episode['episode_number'],
                              air_date=first_aired,
                              episode_name=tmdb_episode['name'],
                              status=episode_retrieved,
                              show=db_show,
                              episode_description=tmdb_episode['overview'],
                              episode_image=episode_art,
                              last_updated=None,
                              )

        db.add(new_episode)


def update_episodes(tmdb_episodes, db_show, season, db, c=None):
    if c is None:
        c = TvdbInteraction.Contentor()
    # artwork = c.get_show_images(db_show.show_id)

    for e in tmdb_episodes:
        # check if episode is in db
        update_episode = db.query(Episode).filter(Episode.id == e['id']).first()
        if update_episode is None:
            add_episode(e, db_show, db, season)
        else:
            #update episode with episode data
            first_aired = None if e['air_date'] is None else datetime.datetime.strptime(e['air_date'], '%Y-%m-%d')


            update_episode.first_aired = first_aired
            update_episode.episode_name = e['name']
            update_episode.overview = e['overview']
            # update_episode.last_updated = e.lastUpdated
            if season['poster_path'] is not None:
                episode_art = 'https://image.tmdb.org/t/p/w185' + season['poster_path']
            else:
                episode_art = db_show.poster

    db.commit()

def update_one(id, db, c=None):
    if c is None:
        c = TvdbInteraction.Contentor()

    show = db.query(Show).filter(Show.show_id == id).first()
    update_show(id, show, db, c)


def update_all(database=None):
    if database is None:
        db = Models.connect()
    else:
        db = database
    c = TvdbInteraction.Contentor()

    shows = db.query(Show).all()
    for show in shows:
        update_show(show.show_id, show, db, c)
    add_addables(db)


def update_show(id, show, db, c):
    series = c.get_show(show.show_id)
    for s in series['seasons']:
        season_number = s['season_number']
        if season_number == 0 or s['episode_count'] == 0:
            continue
        else:
            season_detail = c.tmdb.TV_Seasons(series['id'], season_number).info()
            update_episodes(season_detail['episodes'], show, s, db, c)


def add_addables(db):
    #clean out current tables
    db.query(PopularShow).delete()
    db.query(PremierShow).delete()
    db.commit()

    c = TvdbInteraction.Contentor()
    premiers = c.get_upcoming_premiers()
    popular = c.get_popular()

    create_addables(premiers, 'premier', db)
    create_addables(popular, 'popular', db)

    db.commit()


def create_addables(shows, type, db):
    for s in shows:
        poster = '/static/tmdb-stacked.png' if s['poster_path'] is None else 'http://image.tmdb.org/t/p/w154' + s['poster_path']
        if type == 'premier':
            db_show = PremierShow(name=s['name'],
                                  poster=poster,
                                  overview=s['overview'],
                                  first_aired=datetime.datetime.strptime(s['first_air_date'], '%Y-%m-%d'),
                                  id=s['id'])
        else:
            db_show = PopularShow(name=s['name'],
                                  poster=poster,
                                  overview=s['overview'],
                                  first_aired=datetime.datetime.strptime(s['first_air_date'], '%Y-%m-%d'),
                                  id=s['id'])
        # db_show.name = ['name']
        # db_show.poster ='https://image.tmdb.org/t/p/w185' + s['poster_path']
        # db_show.overview = s['overview']
        # db_show.first_aired = datetime.datetime.strptime(s['first_air_date'], '%Y-%m-%d')
        # db_show.id = s['id']

        db.add(db_show)
