import mechanicalsoup
from urllib.parse import urlparse, urljoin
from Models import ActionLog


def source_login(source):
    # source_domain = urlparse(source.login_page).netloc
    browser = mechanicalsoup.Browser()
    try:
        login_page = browser.get(source.login_page)
    except Exception as ex:
        return None

    if login_page.status_code in [200, 403] and len(login_page.soup.select('form')) > 0:
        form_index = 0
        username_index = 0
        password_index = 0

        domain = source.domain.split('/')[2].replace('www.','')

        if domain in ['tehparadox.com', 'warez-bb.org', 'x264-bb.org', 'adit-hd.com']:
            form_index = 0
            username_index = 0
            password_index = 0
        elif 'puzo.org' in source.domain:
            form_index = 1
            username_index = 0
            password_index = 0
        else:
            return None

        login_form = login_page.soup.select('form')[form_index]
        login_form.findAll("input", {"type": "text"})[username_index]['value'] = source.username
        login_form.findAll("input", {"type": "password"})[password_index]['value'] = source.password

        response_page = browser.submit(login_form, login_page.url)
        print(response_page.status_code)

        return browser

    else:
        return None


def source_search(source, search_text, browser):
    domain = source.domain.split('/')[2].replace('www.', '')
    response_page_links = []
    form_index = 0
    search_page = browser.get(source.url)
    if domain in ['warez-bb.org', 'puzo.org', 'adit-hd.com']: # all these have a search for as the first for on the page
        search_form = search_page.soup.select('form')[form_index]
        search_form.findAll("input", {"type": "text"})[0]['value'] = search_text
        response_page = browser.submit(search_form, search_page.url)
        if response_page.status_code != '404':
            if domain in ['adit-hd.com']: # these have a bounce page and we have to grab a link off the page and redirect
                bounce_link = response_page.soup.select('a')[0]
                if 'href' in bounce_link:
                    bounce_link = urljoin(source.domain, bounce_link['href'])
                    response_page = browser.get(bounce_link)
                else:
                    ActionLog.log('There was an issue with the bounce link when searching %s.  Check you password and/or login on a browser to pass a captcha test.' % source.url)
                    return response_page_links
            response_page_links = response_page.soup.select('a')

    return response_page_links
