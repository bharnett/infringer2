from Models import Config, ActionLog, Show, Episode
import Models
import os
import time
import datetime
from urllib.parse import urlparse, urljoin
import LinkInteraction


class Search(object):
    def __init__(self, db=None):
        self.movie_types = ['movies', 'both']
        self.tv_types = ['tv', 'both']
        self.shows_to_download = []
        if db is None:
            database = Models.connect()
            self.db = database
        else:
            self.db = db
        self.get_episode_list()

    def get_episode_list(self):
        list_of_shows = []

        for s in self.db.query(Show).filter(Show.is_active).all():
            episodes = s.episodes.filter(Episode.air_date <= datetime.date.today() - datetime.timedelta(days=1)).filter(
                Episode.status == 'Pending').all()

            if len(episodes) > 0:
                list_of_shows.extend(episodes)

        if len(list_of_shows) > 0:
            all_tv = ', '.join(str(s) for s in list_of_shows)
        else:
            all_tv = 'no shows'

        self.db.commit()

        ActionLog.log('Searching for: %s.' % all_tv)

        self.shows_to_download = list_of_shows

    @staticmethod
    def j_downloader_check(config):
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

    def is_completed(self):
        downloaded_shows = [x for x in self.shows_to_download if x.is_downloaded]
        return len(downloaded_shows) == len(self.shows_to_download)

    def check_link(self, link, source):
        # this checks the individual link to see if it matches the regex
        # of a given episode (show name) and episode code.
        link_text = link.text.lower().strip()
        if link.text != '':
            if source.media_type in self.movie_types:
                # check if this is a movie link (regex search)
                if LinkInteraction.process_movie_link(self.db, link):
                    return False
            if source.media_type in self.tv_types:  # search for all shows
                if self.is_completed():  # takes care of 'both' media type sources
                    return False
                else:
                    for episode in [x for x in self.shows_to_download if not x.is_downloaded and not x.is_found]:
                        if episode.episode_in_link(link_text):
                            episode.parent_download_page = source.url
                            episode.url_download_source = urljoin(source.domain, link.get('href'))
                            episode.is_found = True
                            # ActionLog.log('"%s" found @ %s' % (episode, episode.url_download_source))
                            return episode.is_found

    def open_links(self, browser, config, source):
        for episode in [s for s in self.shows_to_download if not s.is_downloaded]:
            if not episode.is_found:
                ActionLog.log("%s not found in soup" % str(episode))
                continue
            else:
                tv_response = browser.get(episode.url_download_source)
                if tv_response.status_code == 200:
                    episode_soup = tv_response.soup
                    episode_links = LinkInteraction.get_download_links(episode_soup, config, source.domain)
                    if LinkInteraction.is_valid_links(episode_links, browser, episode):
                        episode.is_found = True
                        episode.download_links = ' | '.join(episode_links)
                        LinkInteraction.process_tv_link(self.db, config, episode, episode_links)
                    else:
                        episode.is_found = False
                        # TODO give a reason why the show isn't 'found' even though we did find it in the
                        # previous section




