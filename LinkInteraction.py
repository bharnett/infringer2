from Models import Episode, Movie, ActionLog
import re
import datetime
from urllib.parse import urlparse, urljoin
import TvdbInteraction


class FileLink(object):
    def __init__(self, link_text):
        self.link_text = link_text
        part_regex = re.compile('\.part.?.?\.rar')
        self.is_part = part_regex.search(self.link_text) is not None


def process_tv_link(db, config, episode, episode_links):
    save_directory = config.tv_parent_directory + episode.show.show_directory
    write_crawljob_file(str(episode), save_directory, ' '.join(episode_links), config.crawljob_directory)
    episode.is_downloaded = True
    episode.status = 'Retrieved'
    episode.retrieved_on = datetime.date.today()
    episode.download_time = datetime.datetime.now()
    db.commit()
    ActionLog.log('"%s\'s" .crawljob file created.' % str(episode))


def is_valid_links(episode_links, browser, episode):
    links_valid = True
    for file_share_link in episode_links:
        try:
            if browser.get(file_share_link).status_code != 200:
                ActionLog.log('Just kidding, "%s" had a bad link or links :(' % episode)
                links_valid = False
                break
        except Exception as ex:
            ActionLog.log('Just kidding, "%s" had a bad link or links :(' % episode)
            ActionLog.log('Link check error: %s.' % str(ex))
            links_valid = False
            break

    if len(episode_links) == 0:
        links_valid = False

    return links_valid


def process_movie_link(db, link):
    regex = re.compile(r'[sS]\d\d[eE]\d\d')
    regex_dated = re.compile(r'[0-9]{4}[\s\S][0-1][0-9][\s\S][0-3][0-9]')
    regex_season = re.compile(r'[sS]eason\s\d{1,2}')
    # TODO create code for handling seasons as new shows and/or current shows
    if link.text.strip() != '' and regex.search(link.text) is None and regex_dated.search(
            link.text) is None and regex_season.search(
            link.text) is None and ('1080p' in link.text or '720p' in link.text):
        # probably movie - no regex and 1080p or 720p so add movie db
        edited_link_text = re.sub('\[?.*\]', '', link.text).strip()

        if db.query(Movie).filter(Movie.name == edited_link_text).first() is None:
            m = Movie(name=edited_link_text, link_text=link.get('href'), status='Not Retrieved')
            db.add(m)
            db.commit()
        return True
    else:
        return False










def get_download_links(soup, config, domain, hd_format='720p'):

    return_links = []
    episode_file_links = []
    all_links = []

    if 'tehparadox.com' in domain:
        code_elements = soup.find_all(text=re.compile('Code'))
        if len(code_elements) == 0: return []
        for c in code_elements[:-1]:
            if 'code:' in c.lower():
                all_links.append(c.parent.parent.find('pre').text)
    elif 'warez-bb.org' in domain:
        code_elements = soup.select('.code span')
        if len(code_elements) == 0: return []
        for c in code_elements:
            all_links.append(c.text)
    elif 'puzo.org' in domain:
        code_elements = soup.select('.prettyprint')
        if len(code_elements) == 0: return []
        for c in code_elements:
            all_links.append(c.text)
    elif 'x264-bb.com' in domain:
        code_elements = soup.select('.codemain pre')
        for c in code_elements:
            all_links.append(c.text)
    elif 'adit-hd' in domain:
        code_elements = soup.select('code')
        if len(code_elements) == 0: return []
        for c in code_elements:
            all_links.append(c.text)
    else:
        return return_links

    check_links = '\n'.join(all_links).split('\n')

    for l in [x for x in check_links if not x.strip() == '']:
        if config.domain_link_check(l) and l[-3:].lower() != 'srt':  # ignore .srt files
            ul = FileLink(l)
            episode_file_links.append(ul)

    if len(episode_file_links) == 1:
        # only one uploaded link - return it!
        return_links.append(episode_file_links[0].link_text)
    elif len(episode_file_links) > 1:
        # multiple links - check for parts vs single extraction
        single_extraction_links = []
        part_links = []
        # filter(link for link in uploaded_links if '.mkv' in link.link_text)
        for l in episode_file_links:
            single_extraction_links.append(l) if '.mkv' in l.link_text else part_links.append(l)

        if len(single_extraction_links) == 1:
            # only one .mkv link - get it done
            return_links.append(single_extraction_links[0].link_text)
        elif len(single_extraction_links) == 2:
            # prob two episode upload, just get both
            for t in single_extraction_links:
                if hd_format.replace('p', '') in t.link_text:
                    return_links.append(t.link_text)
                elif has_hd_format(t.link_text) is False:  # handle shows without HD format in string, just add them
                    return_links.append(t.link_text)
        else:
            # get all the parts for tv and movies
            if len(part_links) == 0:
                for n in single_extraction_links:
                    return_links.append(n.link_text)
            for p in part_links:
                return_links.append(p.link_text)

    return return_links


def scan_movie_links(db, browser, source, config):
    c = TvdbInteraction.Contentor()

    for movie in db.query(Movie).all():
        # only movies without a movie_link set
        if movie.links is None or movie.links.strip() == '':
            movie_link = urljoin(source.domain, movie.link_text)
            movie_response = browser.get(movie_link)
            if movie_response.status_code == 200:
                movie_soup = movie_response.soup
                movie_links = get_download_links(movie_soup, config, source.domain, '1080p')
                movie.links = ' '.join(movie_links)

                if len(movie_links) == 0 or movie.name.strip() == '':
                    db.query(Movie).filter(Movie.id == movie.id).delete()
                else:
                    search_details = movie.get_name_and_year()
                    tmdb_movie = c.get_movie_details(search_details[0], search_details[1])
                    if tmdb_movie is None:
                        na_message = '"%s" not added.  Found at %s'% (movie.name, movie_link)
                        ActionLog.log(na_message)
                        continue
                    else:
                        movie.tmdb_id = tmdb_movie.movie['id']
                        movie.title = tmdb_movie.movie['title']
                        movie.tmdb_rating = tmdb_movie.movie['vote_average']
                        movie.poster = 'https://image.tmdb.org/t/p/w185' + tmdb_movie.movie['poster_path']
                        movie.overview = tmdb_movie.movie['overview']
                        movie.actors = ', '.join(tmdb_movie.cast)
                        movie.status = "Ready"

                        ActionLog.log('"%s" added to downloadable movies' % movie.name)
                db.commit()


def write_crawljob_file(package_name, folder_name, link_text, crawljob_dir):
    crawljob_file = crawljob_dir + '/%s.crawljob' % package_name.replace(' ', '')

    file = open(crawljob_file, 'w')
    file.write('enabled=TRUE\n')
    file.write('autoStart=TRUE\n')
    file.write('extractAfterDownload=TRUE\n')
    file.write('downloadFolder=%s\n' % folder_name)
    file.write('packageName=%s\n' % package_name.replace(' ', ''))
    file.write('text=%s\n' % link_text)
    file.close()


def has_hd_format(link_text):
    if '720' in link_text or '1080' in link_text:
        return True
    else:
        return False
