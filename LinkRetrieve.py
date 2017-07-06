from Models import Show, Config, Episode, ActionLog, ScanURL
import Models
import Search
import WebInteraction


def search_sites():
    # This is to search pages.  They can either be long pages like cardman's or search results
    # also this can be used to search a dynamic results page or
    db = Models.connect()
    config = db.query(Config).first()
    search = Search.Search()
    search.j_downloader_check(config)
    search.db = db

    for source in db.query(ScanURL).order_by(ScanURL.priority).all():
        tv_is_completed = search.is_completed()

        if (tv_is_completed and source.media_type == 'tv') or source.media_type == 'search':
            # skip tv types list is completed
            continue
        browser = WebInteraction.source_login(source)
        # get browser and login to the source
        if browser is None:
            ActionLog.log('%s could not logon' % source.login_page)
            continue
        else:
            ActionLog.log('Scanning %s for %s' % (source.domain, source.media_type))
            # if you can login, start checking for content
            try:
                soup = browser.get(source.url).soup
            except Exception as ex:
                continue

            soup = soup.select(source.link_select)[:1000] # get dem links

            for link in soup:
                check_result = search.check_link(link, source)
                if check_result is False: # move onto new link if it doesn't match
                    continue

            # open links and get download links for TV
            search.open_links(browser, config, source)

if __name__ == "__main__":
    search_sites()