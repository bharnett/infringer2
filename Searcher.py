import os
import re
import datetime

"""this module holds the class and functions for searching episodes"""

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
        hide_chars = [('e', '3'), ('l', '1'), ('o', '0')]
        # these are the characters that need to be replaced
        # this is only for the first instance of the letter in each word
        edit_chars = [('', ''), ('.', ' '), ('.', ''), ('&', 'and')]
         # first one handles initial non-char-edited name
        second_chars = [('\'', '')]
        # remove dates from show names (2014), (2009) for accurate string searches
        edited_show_name = re.sub(r'[\(][0-9]{4}[\)]', '',
                                  episode.show.show_name)
        episode_id_string = 's%se%s' % (str(episode.season_number).zfill(2),
                                        str(episode.episode_number).zfill(2))
        show_dir = parent_dir + episode.show.show_directory
        if not os.path.exists(show_dir):
            os.makedirs(show_dir)

        search_episode = Searcher(episode.id, episode_id_string, '', show_dir, episode.attempts)

        for char in edit_chars:
            char_edit_name = edited_show_name.replace(char[0], char[1]).strip().lower()
            search_episode.search_list.append(char_edit_name)
            for second in second_chars:
                edit_name = char_edit_name.replace(second[0], second[1]).strip().lower()
                search_episode.search_list.append(edit_name)

        # remove duplicates
        search_episode.search_list = list(set(search_episode.search_list))
        return search_episode

    def search_me(self, link_text):
        is_found = False
        if self.episode_code in link_text:
            for s in self.search_list:
                if s in link_text:
                    is_found = True
                    return is_found
                else:
                    continue
        return is_found

    @staticmethod
    def list_completed(list_of_shows):
        items = [item for item in list_of_shows if item.found is False]
        return len(items) == 0
    
def make_hidden_char_names(self, hide_chars, episode):
    """get variants that have hidden characters"""
    temp_name = episode #episode.show.show_name
    show_words = temp_name.split(' ')
    new_names = []

    for char in hide_chars:
        new_episode = ''
        for word in show_words:
            new_episode += word.replace(char[0], char[1])
        new_names.append(new_episode)
    
    return new_names


                    
bcs = 'Better Call Saul'
p = 'Preacher'
ns = 'Nonsense Sally Edge'
hide_chars = [('e', '3'), ('l', '1'), ('o', '0')]

names = make_hidden_char_names(hide_chars, bcs)
