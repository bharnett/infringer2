from Models import Show, Config, Episode, ActionLog, ScanURL
import Models
import Search
import WebInteraction
import LinkInteraction
import time
import mechanicalsoup


def search_all(db=None):
    browser = mechanicalsoup.Browser()

    if db is None:
        db = Models.connect()
    search_sites(browser, db)
    search_forums(browser, db)


def search_sites(browser, db=None):
    # This is to search pages.  They can either be long pages like cardman's or search results
    # also this can be used to search a dynamic results page or
    if db is None:
        db = Models.connect()

    config = db.query(Config).first()
    search = Search.Search(db)
    search.j_downloader_check(config)

    for source in db.query(ScanURL).filter(ScanURL.scan_type == 'static').order_by(ScanURL.priority).all():
        tv_is_completed = search.is_completed()

        browser_status = WebInteraction.source_login(source, browser)
        # get browser and login to the source
        if browser_status is False:
            ActionLog.log('%s could not logon' % source.login_page)
            continue
        else:
            ActionLog.log('Scanning %s for the STATIC page %s.' % (source.domain, source.url), db)
            # if you can login, start checking for content
            try:
                soup = browser.get(source.url).soup
            except Exception as ex:
                continue

            # soup = soup.select(source.link_select)[:1000] # get dem links
            soup = soup.select('a')[:2000] # get dem links
            # let's try doing this with out the link selection, since we can parse them fast with
            # the regex, we don't necessarily need it.

            for link in soup:
                check_result = search.check_link(link, source)
                if check_result is False: # move onto new link if it doesn't match
                    continue

            # open links and get download links for TV
            search.open_links(browser, config, source)

            LinkInteraction.scan_movie_links(db, browser, source, config)


def search_forums(browser, db=None):
    if db is None:
        db = Models.connect()
    config = db.query(Config).first()
    search = Search.Search(db)
    # search.j_downloader_check(config)  prob dont' need this since it will be run after 'search_sites'

    for source in db.query(ScanURL).filter(ScanURL.scan_type == 'search').order_by(ScanURL.priority).all():
        tv_is_completed = search.is_completed()

        if tv_is_completed:
            break

        browser_status = WebInteraction.source_login(source, browser)
        if browser_status is False:
            ActionLog.log('%s could not logon' % source.login_page)
            continue
        else:
            ActionLog.log('Searching via the search form on %s.' % source.domain, db)
            # we invert the search format and check for each show, not each link in the page

        for s in search.shows_to_download:
            ActionLog.log('Searching for %s.' % str(s), db)
            response_links = WebInteraction.source_search(source, str(s), browser)
            correct_links = [l for l in response_links if s.episode_in_link(l.text.lower())]
            ActionLog.log('Found %s links for %s on %s' % (str(len(correct_links)), str(s), source.domain), db)
            search.process_search_result(correct_links, s, browser, source, config)
            time.sleep(15)  # wait five seconds between searches for warez-bb.org


if __name__ == "__main__":
    database = Models.connect()
    search_all(database)