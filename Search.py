from Models import Config, ActionLog, Show, Episode
import Models
import os
import time


class Search(object):
    def __init__(self):
        self.movie_types = ['movies', 'both']
        self.tv_types = ['tv', 'both']
        self.shows_to_download = self.get_episode_list()

    def get_episode_list():
        list_of_shows = []
        db = Models.connect()
        config = db.query(Config).first()

        for s in db.query(Show).filter(Show.is_active).all():
            episodes = s.episodes.filter(Episode.air_date <= datetime.date.today() - datetime.timedelta(days=1)).filter(
                Episode.status == 'Pending').all()

            if len(episodes) > 0:
                list_of_shows = episodes

        if len(list_of_shows) > 0:
            all_tv = ', '.join(str(s) for s in list_of_shows)
        else:
            all_tv = 'no shows'

        ActionLog.log('Searching for: %s.' % all_tv)
        db.commit()

        return list_of_shows

    @staticmethod
    def j_downloader_check(self, config):
        try:
            if len(config.jd_path) > 0:
                start_command = 'open "%s"' % config.jd_path
                # start_command = 'open "/Applications/JDownloader"'
                kill_command = 'killall JavaApplicationStub'
                os.system(kill_command)
                time.sleep(10)
                os.system(start_command)
        except Exception as ex:
            ActionLog.log(
                '%s is not a valid directory for JDownloader in OSX.  JDownloader has not restarted.' % config.jd_path)

    @staticmethod
    def is_completed(shows):
        downloaded_shows = [for x in shows if not x.is_downloaded]
        return len(downloaded_shows) == len(shows)

    def check_link(self, link, source):
        if link.text != '':
            if source.media_type in self.movie_types:
                if process_movie_link(db, link):  # get movies links
                    continue
            if source.media_type in self.tv_types:  # search for all shows
                if Search.is_completed():  # takes care of 'both' media type sources
                    continue
                else:
                    for show_searcher in [x for x in list_of_shows if not x.found and not x.retrieved]:
                        link_text = link.text.lower()
                        if show_searcher.search_me(link_text):
                            show_searcher.link = urljoin(source.domain, link.get('href'))
                            show_searcher.found = True
                            ActionLog.log('"%s" found!' % show_searcher)