import os
import re
import datetime

"""this module holds the class and functions for searching episodes"""

hide_chars = ['e', 'l', 'o']
space_chars = ['.',' ','_']


class Searcher(object):
    """class for searching for an individual episode"""
    def __init__(self, episode_id, episode_code, link, directory, attempts=0):
        self.episode_id = episode_id
        self.episode_code = episode_code
        self.link = link
        self.found = False
        self.directory = directory
        self.retrieved = False
        self.search_list = []
        self.attempts = attempts
        self.regex_name = ''

    def __str__(self):
        return '%s %s' % (self.search_list[0], self.episode_code)

    @staticmethod
    def populate_searcher(episodes, config):
        search_episodes = []
        for e in episodes:
            search_episodes.append(Searcher.populate_episode(e, config.tv_parent_directory))

        return search_episodes

    @staticmethod
    def populate_episode(episode, parent_dir):

        # remove dates from show names (2014), (2009) for accurate string searches
        # also replaces single quotes with nothing and removes extra spaces & lowers text
        edited_show_name = re.sub(r'[\(][0-9]{4}[\)]', '',
                                  episode.show.show_name).replace('\'','').strip().lower()

        episode_id_string = 's%se%s' % (str(episode.season_number).zfill(2),
                                        str(episode.episode_number).zfill(2))

        show_dir = parent_dir + episode.show.show_directory
        if not os.path.exists(show_dir):
            os.makedirs(show_dir)
            
        search_episode = Searcher(episode.id, episode_id_string, '', show_dir, episode.attempts)
        search_episode.regex_name = make_show_regex(episode.show.show_name)

        return search_episode

    def search_me(self, link_text):
        is_found = False
        return re.findall(self.regex_name, link_text)
        if self.episode_code in link_text:
            is_found = re.findall(self.regex_name, link_text)
            # might need to add global checks on the outside of the text for wildcards 
            # since the leading and trailing regex could be something unexpected
        return is_found

    @staticmethod
    def list_completed(list_of_shows):
        items = [item for item in list_of_shows if item.found is False]
        return len(items) == 0


def make_show_regex(episode):
    """get variants that have hidden characters"""
    regex_name = episode #episode.show.show_name

    for char in hide_chars:
        regex_name = regex_name.replace(char, '[a-zA-Z0-9]')

    for char in space_chars:
        regex_name = regex_name.replace(char, '[\s\.\\_]')
    
    for a in ['&', 'and']:
        regex_name = regex_name.replace(a, '(and)&')

    return regex_name


bcs = 'Better Call Saul'
p = 'Preacher'
ns = 'Nonsense Sally Edge'

names = make_show_regex(bcs)
