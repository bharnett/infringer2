from datetime import datetime
import os
import os.path
import webbrowser
import tvdb_api
import LinkRetrieve
import Utils
from Models import Show, Episode, Movie, ActionLog, ScanURL, Config
import Models
import json
import cherrypy
import urllib
from urllib import request
from mako.template import Template
from mako.lookup import TemplateLookup
from webutils import AjaxResponse
from apscheduler.schedulers.background import BackgroundScheduler
import MediaInteraction
import TvdbInteraction
import LinkInteraction
import ViewBag
import jsonpickle
import mechanicalsoup

template_dir = os.path.dirname(os.path.normpath(os.path.abspath(__file__))) + '/html'
my_lookup = TemplateLookup(directories=[template_dir])
scan_refresh_scheduler = BackgroundScheduler()
# cherrypy.request.db = models.connect()


class Infringer(object):
    # @cherrypy.expose
    # def index(self):
    #     config = cherrypy.request.db.query(Config).first()
    #     if not config.is_populated():
    #         raise cherrypy.HTTPRedirect("/config")
    #     else:
    #         index_template = my_lookup.get_template('index.html')
    #         upcoming_episodes = cherrypy.request.db.query(Episode).filter(Episode.air_date != None).filter(
    #             Episode.status == 'Pending').order_by(Episode.air_date)[:25]
    #         index_shows = cherrypy.request.db.query(Show).order_by(Show.show_name)
    #         index_movies = cherrypy.request.db.query(Movie).filter(Movie.status == 'Ready').all()
    #         downloaded_shows = cherrypy.request.db.query(Episode).filter(Episode.retrieved_on is not None).order_by(
    #             Episode.retrieved_on.desc())[:50]
    #         return index_template.render(shows=index_shows, movies=index_movies, upcoming=upcoming_episodes,
    #                                      downloaded=downloaded_shows, jd_link=config.jd_link)

    @cherrypy.expose
    def index(self):
        index_template = my_lookup.get_template('index.html')
        vb = ViewBag.ViewBag()
        vb.populate_addables()
        return index_template.render(vb=vb, jd_link=vb.jd_link)

    @cherrypy.expose
    def show(self, show_id):
        show_template = my_lookup.get_template('show.html')
        current_show = cherrypy.request.db.query(Show).filter(Show.show_id == show_id).first()
        current_episodes = current_show.episodes.order_by(Episode.season_number.desc()).order_by(
            Episode.episode_number.desc()).all()
        return show_template.render(show=current_show, episodes=current_episodes)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_episode(self):
        status = 'success'
        try:
            data = cherrypy.request.json
            episode_id = data['episodeid']
            change_to_value = data['changeto']
            change_to_value = change_to_value.title()
            e = cherrypy.request.db.query(Episode).filter(Episode.id == episode_id).first()
            e.status = change_to_value
            if e.status == 'Pending':
                e.reset()
            cherrypy.request.db.commit()
        except Exception as ex:
            ActionLog.log(ex)
            status = 'error'
        return json.dumps(status)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_show(self):
        status = 'success'
        try:

            data = cherrypy.request.json
            show_id = data['showid']
            action = data['action']

            if action == 'refresh':
                Utils.add_episodes(show_id)

            if action == 'remove':
                s = cherrypy.request.db.query(Show).filter(Show.show_id == show_id).first()
                ActionLog.log('"%s" removed.' % s.show_name)
                cherrypy.request.db.delete(s)
                cherrypy.request.db.commit()

        except Exception as ex:
            # logger.exception(ex)
            status = 'error'

        return json.dumps(status)

    @cherrypy.expose
    def log(self):
        log_template = my_lookup.get_template('log.html')
        logs = cherrypy.request.db.query(ActionLog).order_by(ActionLog.time_stamp.desc()).all()
        return log_template.render(log=logs)


    @cherrypy.expose
    def config(self):
        config_template = my_lookup.get_template('config.html')
        c = cherrypy.request.db.query(Config).first()
        s = cherrypy.request.db.query(ScanURL).all()
        if c is None:
            c = Config()
            cherrypy.request.db.add(c)
            cherrypy.request.db.commit()
        return config_template.render(config=c, scanurls=s, jd_link=c.jd_link)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def ajax_config(self):
        ar = AjaxResponse('Configuration updated...')

        try:
            is_restart = False
            data = cherrypy.request.json
            c = cherrypy.request.db.query(Config).first()
            c.crawljob_directory = data['crawljob-directory']
            c.tv_parent_directory = data['tv-parent-directory']
            c.movies_directory = data['movies-directory']
            c.file_host_domain = data['file-host-domain']
            c.hd_format = data['hd-format']

            # check for changes that need a reschedule
            if c.scan_interval != int(data['scan-interval']):
                scan_refresh_scheduler.reschedule_job('scan_job', trigger='cron',
                                                      hour='*/' + str(data['scan-interval']))

            if c.refresh_day != data['refresh-day'] or c.refresh_hour != int(data['refresh-hour']):
                scan_refresh_scheduler.reschedule_job('refresh-job', trigger='cron', day_of_week=data['refresh-day'],
                                                      hour=str(data['refresh-hour']))

            c.scan_interval = data['scan-interval']
            c.refresh_day = data['refresh-day']
            c.refresh_hour = data['refresh-hour']
            c.jd_link = data['jd-link']
            c.jd_path = data['jd-path']
            #
            # if 'jdownloader_restart' in data:
            #     c.jdownloader_restart = True if data['jdownloader_restart'] == 'on' else False
            # else:
            #     c.jdownloader_restart = False

            if data['ip'] != c.ip or data['port'] != c.port:
                is_restart = True

            c.ip = data['ip']
            c.port = data['port']
            cherrypy.request.db.commit()

            if is_restart:
                cherrypy.engine.stop()
                cherrypy.server.httpserver = None
                cherrypy.config.update({
                    'server.socket_host': c.ip,
                    'server.socket_port': int(c.port),
                })
                cherrypy.engine.start()
                ar.status = 'redirect'
                ar.message = 'http://%s:%s/config' % (c.ip, c.port)

        except Exception as ex:
            ar.status = 'error'
            ar.message = str(Exception)

        return ar.to_JSON()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def config_dirs(self, **kwargs):
        try:
            test_string = [elem for elem in kwargs.values()][0]
            validation_response = os.path.isdir(test_string)
        except Exception as ex:
            validation_response = False

        return validation_response

    @cherrypy.expose
    def forums(self):
        forums_template = my_lookup.get_template('forums.html')
        data = cherrypy.request.db.query(ScanURL).all()
        config = cherrypy.request.db.query(Config).first()

        b = mechanicalsoup.Browser()
        page = b.get(data[0].domain)
        is_page_up = page.status_code in [200, 403]


        return forums_template.render(sources=data, jd_link=config.jd_link, forum_status=is_page_up)


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_scanurl(self):
        ar = AjaxResponse('Data source updated...')
        try:
            data = cherrypy.request.json
            action = data['action']
            if action == 'add':
                new_scanurl = ScanURL()
                ar.message = 'Data source added...'
                cherrypy.request.db.add(new_scanurl)
            else:
                u = cherrypy.request.db.query(ScanURL).filter(ScanURL.id == data['id']).first()
                if action == 'update':
                    setattr(u, data['propertyName'], data['propertyValue'])
                    ar.message = 'Updated %s.' % data['propertyName'].replace('_',' ')
                elif action == 'delete':
                    ar.message = 'Data source deleted...'
                    cherrypy.request.db.delete(u)
            cherrypy.request.db.commit()
        except Exception as ex:
            ar.status = 'error'
            ar.message = str(ex)

        return ar.to_JSON()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def search(self, show_search):
        try:
            c = TvdbInteraction.Contentor()
            search_results = c.search_show(show_search)
            #t = tvdb_api.Tvdb()
            #search_results_old = t.search(show_search)
            ActionLog.log('Search for "%s".' % show_search)
        except Exception as ex:
            search_results = "{error: %s}" % Exception

        return jsonpickle.encode(search_results) # json.dumps(search_results)


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def add_show(self):
        status = 'success'
        try:
            data = cherrypy.request.json
            series_id = data['series_id']
            # db = models.connect()
            if cherrypy.request.db.query(Show).filter(Show.show_id == series_id).first() is None:
                # save new show to db
                MediaInteraction.add_show(series_id, cherrypy.request.db)
            else:
                status = 'duplicate'
                # http://stackoverflow.com/questions/7753073/jquery-ajax-post-to-django-view
        except Exception as ex:
            # logger.exception(ex)
            ActionLog.log(ex)
            status = 'error'

        return json.dumps(status)



    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def refresh(self):
        status = 'success'
        try:
            data = cherrypy.request.json
            is_show_refresh = data['isshowrefresh']
            is_scan = data['isscan']

            if is_scan:
                LinkRetrieve.search_sites(cherrypy.request.db)

            if is_show_refresh:
                Utils.update_all()

        except Exception as ex:
            ActionLog.log(ex)
            status = 'error'

        return json.dumps(status)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handle_movie(self):
        ar = AjaxResponse('Movie downloading...')
        try:
            data = cherrypy.request.json
            movie_id = data['movie_id']
            action = data['movie_action']
            config = cherrypy.request.db.query(Config).first()
            if action == 'cleanup':
                cherrypy.request.db.query(Movie).filter(Movie.status == 'Ignored').delete()
                cherrypy.request.db.commit()
                ActionLog.log("DB cleanup completed")
            else:
                m = cherrypy.request.db.query(Movie).filter(Movie.id == movie_id).first()
                if action == 'ignore':
                    m.status = 'Ignored'
                else:
                    LinkInteraction.write_crawljob_file(m.title, config.movies_directory, m.links,
                                                     config.crawljob_directory)
                    ActionLog.log('"%s\'s" .crawljob file created.' % m.name)
                    m.status = 'Retrieved'
                cherrypy.request.db.commit()
        except FileExistsError as no_file_ex:
            ActionLog.log('error - ' + str(no_file_ex))
            ar.status = 'error'
            ar.message = 'Could not save to "%s" - Check your config.' % config.movies_directory
        except Exception as ex:
            ActionLog.log('error - ' + str(ex))
            ar.status = 'error'
            ar.message = str(ex)

        return ar.to_JSON()


    @cherrypy.expose
    def restart(self):
        restart()

    @cherrypy.expose
    def shutdown(self):
        shutdown_template = my_lookup.get_template('shutdown.html')
        scan_refresh_scheduler.shutdown()
        cherrypy.engine.stop()
        cherrypy.server.httpserver = None
        cherrypy.engine.exit()
        return shutdown_template.render()


def restart():
    scan_refresh_scheduler.shutdown()
    cherrypy.engine.exit()
    startup()


def startup():
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.db.on': True
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    }

    config_session = Models.connect()
    config = config_session.query(Models.Config).first()

    if config is None:
        config = Models.Config()
        config_session.add(config)
        config_session.commit()

    cherrypy.config.update({
        'server.socket_host': config.ip,
        'server.socket_port': int(config.port),
    })
    # config_session.remove()

    scan_refresh_scheduler.add_job(LinkRetrieve.search_sites, 'cron', hour='*/' + str(config.scan_interval),
                                   id='scan_job', misfire_grace_time=60)
    scan_refresh_scheduler.add_job(Utils.update_all, 'cron', day_of_week=config.refresh_day,
                                   hour=str(config.refresh_hour), id='refresh_job', misfire_grace_time=60)
    scan_refresh_scheduler.start()

    Models.SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = Models.SATool()
    cherrypy.tree.mount(Infringer(), '/', conf)
    cherrypy.engine.start()
    # webbrowser.get().open(
    #     'http://%s:%s' % (cherrypy.config['server.socket_host'], str(cherrypy.config['server.socket_port'])))
    cherrypy.engine.block()


if __name__ == '__main__':
    startup()


