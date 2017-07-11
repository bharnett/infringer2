import TvdbInteraction
from Models import Show, Episode, Movie, Config, ActionLog, AddableShow
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
                    is_active=series['status'] == 'Returning Series',
                    overview=series['overview'],
                    banner="",
                    poster='https://image.tmdb.org/t/p/w185' + series['poster_path'],
                    thumb="",
                    background='https://image.tmdb.org/t/p/original' + series['poster_path'],
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

        episode_art = 'https://image.tmdb.org/t/p/w185' + season['poster_path']

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


def update_episodes(tvdb_episodes, db_show, db, c=None):
    if c is None:
        c = TvdbInteraction.Contentor()
    artwork = c.get_show_images(db_show.show_id)

    for e in tvdb_episodes:
        # check if episode is in db
        update_episode = db.query(Episode).filter(Episode.epsode_id == e.id).first()
        if update_episode is None:
            add_episode(e, db_show, db, c, artwork)
        else:
            #update episode with episode data
            if update_episode.last_updated < e.lastUpdated:
                first_aired = None if e.firstAired is None else e.firstAired

                update_episode.first_aired = first_aired
                update_episode.episode_name = e.episodeName
                update_episode.last_updated = e.lastUpdated

    db.commit()


def update_all(database=None):
    if database is None:
        db = Models.connect()
    else:
        db = database
    c = TvdbInteraction.Contentor()
    db = Models.connect()
    shows = db.query(Show).all()
    for s in shows:
        show_changes = c.tmdb.TV(s.show_id).latest()  #c.get_show(s.show_id)
    add_addables(db)


def add_addables(db):
    #clean out current tables
    db.query(AddableShow).delete()

    c = TvdbInteraction.Contentor()
    premiers = c.get_upcoming_premiers()
    popular = c.get_popular()

    create_addables(premiers, 'premier', db)
    create_addables(popular, 'popular', db)

    db.commit()


def create_addables(resp_and_ids, type, db):
    resp = resp_and_ids[0]
    ids = resp_and_ids[1]
    for i in range(len(resp_and_ids[0])):
        if ids[i] == 0:
            continue
        else:
            tmdb_show = resp[i]
            db_show = AddableShow(name=tmdb_show['name'],
                                  poster='https://image.tmdb.org/t/p/w185' + tmdb_show['poster_path'],
                                  overview=tmdb_show['overview'],
                                  addable_type=type,
                                  first_aired=datetime.datetime.strptime(tmdb_show['first_air_date'], '%Y-%m-%d'),
                                  id=ids[i])
            db.add(db_show)


#preacher is 300472

# database = Models.connect()
# # show = database.query(Show).filter(Show.show_id == 300472).first()
# # if show is not None:
# #     database.delete(show)
# #     database.commit()
# #
# # add_show(300472, database)
#
# add_addables(database)
