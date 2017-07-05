from Models import Show, Config, Episode, ActionLog, ScanURL
import Models
import datetime
import Search
import WebInteraction






def search_sites(list_of_shows):
    ''' This is to search pages.  They can either be long pages like cardman's or search results'''
    # also this can be used to search a dynamic results page or
    db = Models.connect()
    config = db.query(Config).first()
    search = Search()
    search.j_downloader_check(config)

    for source in db.query(ScanURL).order_by(ScanURL.priority).all():
        tv_is_completed = search.is_completed(list_of_shows)

        if (tv_is_completed and source.media_type == 'tv') or source.media_type == 'search':
            # skip tv types list is completed
            continue
        browser = WebInteraction.source_login(source)
        if browser is None:
            ActionLog.log('%s could not logon' % source.login_page)
            continue
        else:
            ActionLog.log('Scanning %s for %s' % (source.domain, source.media_type))
            try:
                soup = browser.get(source.url).soup
            except Exception as ex:
                continue
            soup = soup.select(source.link_select)[:1000]

            for link in soup:
                if link.text != '':
                    if source.media_type in search.movie_types:
                        if process_movie_link(db, link):  # get movies links
                            continue
                    if source.media_type in search.tv_types:  # search for all shows
                        if tv_is_completed:  # takes care of 'both' media type sources
                            continue
                        else:
                            for show_searcher in [x for x in list_of_shows if not x.found and not x.retrieved]:
                                link_text = link.text.lower()
                                if show_searcher.search_me(link_text):
                                    show_searcher.link = urljoin(source.domain, link.get('href'))
                                    show_searcher.found = True
                                    ActionLog.log('"%s" found!' % show_searcher)

            # open links and get download links for TV
            link_browser = mechanicalsoup.Browser()  # for checking links
            for show_searcher in [l for l in list_of_shows if not l.retrieved]:
                if not show_searcher.found:
                    ActionLog.log("%s not found in soup" % str(show_searcher))
                    db_episode = db.query(Episode).filter(
                        Episode.id == show_searcher.episode_id).first()
                    db_episode.attempts += 1
                    db.commit()
                    continue
                tv_response = browser.get(show_searcher.link)
                if tv_response.status_code == 200:
                    episode_soup = tv_response.soup
                    episode_links = get_download_links(episode_soup, config, source.domain, config.hd_format)

                    links_valid = True
                    for file_share_link in episode_links:
                        try:
                            if link_browser.get(file_share_link).status_code != 200:
                                links_valid = False
                                show_searcher.found = False
                                show_searcher.retrieved = False
                                ActionLog.log('Just kidding, "%s" had a bad link or links :(' % show_searcher)

                                break
                        except Exception as ex:
                                links_valid = False
                                show_searcher.found = False
                                show_searcher.retrieved = False
                                ActionLog.log('Just kidding, "%s" had a bad link or links :(' % show_searcher)

                                break

                    if links_valid:
                        process_tv_link(db, config, show_searcher, episode_links)

            if source.media_type in movie_types:  # scan movies
                for movie in db.query(Movie).all():
                    # only movies without a movie_link set
                    if len(movie.movieurls.all()) == 0:
                        movie_link = urljoin(source.domain, movie.link_text)
                        movie_response = browser.get(movie_link)
                        if movie_response.status_code == 200:
                            movie_soup = movie_response.soup
                            movie_links = get_download_links(movie_soup, config, source.domain, '1080p')

                            if len(movie_links) == 0 or movie.name.strip() == '':
                                db.query(Movie).filter(Movie.id == movie.id).delete()
                            else:
                                for m in movie_links:
                                    db.add(MovieURL(url=m, movie=movie))
                                    db.commit()
                                    # movie.append(MovieURL(url=m))
                                movie.status = "Ready"
                                ActionLog.log('"%s" added to downloadable movies' % movie.name)
                            db.commit()
    db.remove()
