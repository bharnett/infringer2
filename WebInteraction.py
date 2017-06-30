import mechanicalsoup


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

        if source.domain in ['tehparadox.com', 'warez-bb.org', 'x264-bb.org']:
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

        response_page = browser.submit(login_form,login_page.url)
        print(response_page.status_code)

        return browser

    else:
        return None
