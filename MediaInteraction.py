import TvdbInteraction
from Models import Show, Episode, Movie, Config, ActionLog
import os
import datetime


def add_show(show_id, db):
    c = TvdbInteraction.Contentor()
    series = c.get_show(show_id)
    episodes = series.episodes()
    artwork = c.get_show_images(show_id)

    first_aired_date = datetime.strptime(series.firstAired, "%Y-%m-%d")
    new_show = Show(show_id=show_id,
                    show_name=series.seriesName,
                    first_aired=first_aired_date,
                    is_active=series.status == 'Continuing',
                    overview=series.overview,
                    banner=artwork.banner.url,
                    poster=artwork.show_poster.url,
                    thumb=artwork.show_thumb.url,
                    background=artwork.background.url,
                    large_image=artwork.show_large.url)


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
    for e in episodes:
        add_episode(e, show_id, db, c, artwork)


def add_episode(episode, show, db, c=None, artwork=None):
    if c is None:
        c = TvdbInteraction.Contentor()

    if artwork is None:
        artwork = c.get_show_images(show.id)

    if episode.season_number != 0:
        first_aired = None if episode.firstAired is None else datetime.datetime.\
            strptime(episode.firstAired, '%Y-%m-%d').date()

        if first_aired is not None and first_aired >= datetime.date.today() + datetime.timedelta(-2):
            episode_retrieved = 'Pending'
        elif first_aired is None:
            episode_retrieved = 'Pending'
        else:
            episode_retrieved = 'Retrieved'

        if len(artwork.seasons_posters) == episode.airedSeason - 1:
            


        new_episode = Episode(id=episode.id,
                              season_number=episode.airedSeason,
                              episode_number=episode.airedEpisodeNumber,
                              air_date=first_aired,
                              episode_name=episode.episodeName,
                              status=episode_retrieved,
                              show=show,
                              episode_description=episode.overview)
