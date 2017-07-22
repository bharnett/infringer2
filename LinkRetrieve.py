from Models import Show, Config, Episode, ActionLog, ScanURL
import Models
import Search
import WebInteraction
import LinkInteraction
import time


def search_sites(db=None):
    # This is to search pages.  They can either be long pages like cardman's or search results
    # also this can be used to search a dynamic results page or
    if db is None:
        db = Models.connect()

    config = db.query(Config).first()
    search = Search.Search(db)
    search.j_downloader_check(config)

    for source in db.query(ScanURL).filter(ScanURL.scan_type == 'static').order_by(ScanURL.priority).all():
        tv_is_completed = search.is_completed()

        browser = WebInteraction.source_login(source)
        # get browser and login to the source
        if browser is None:
            ActionLog.log('%s could not logon' % source.login_page)
            continue
        else:
            ActionLog.log('Scanning %s' % source.domain)
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


def search_forms(db=None):
    if db is None:
        db = Models.connect()
        config = db.query(Config).first()
        search = Search.Search(db)
        # search.j_downloader_check(config)  prob dont' need this since it will be run after 'search_sites'

        for source in db.query(ScanURL).filter(ScanURL.scan_type == 'static').order_by(ScanURL.priority).all():
            tv_is_completed = search.is_completed()

            browser = WebInteraction.source_login(source)
            if browser is None:
                ActionLog.log('%s could not logon' % source.login_page)
                continue
            else:
                ActionLog.log('Searching %s' % source.domain)
                # we invert the search format and check for each show, not each link in the page

            for s in search.shows_to_download:
                response_links = WebInteraction.source_search(source, str(s), browser)
                correct_links = [l for l in response_links if s.episode_in_link(l)]
                time.sleep(15)  # wait five seconds between searches for warez-bb.org


if __name__ == "__main__":
    database = Models.connect()
    search_sites(database)