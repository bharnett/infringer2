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
import IndexViewBag
import jsonpickle
import mechanicalsoup
import re
from sqlalchemy.orm import subqueryload


template_dir = os.path.dirname(os.path.normpath(os.path.abspath(__file__))) + '/html'
my_lookup = TemplateLookup(directories=[template_dir])
scan_refresh_scheduler = BackgroundScheduler()
# cherrypy.request.db = models.connect()


class Infringer(object):

    @cherrypy.expose
    def index(self):
        index_template = my_lookup.get_template('index.html')
        vb = IndexViewBag.IndexViewBag()
        vb.populate_addables()
        return index_template.render(vb=vb, jd_link=vb.jd_link)

    # all for SHOW PAGES#############################################

    @cherrypy.expose
    def shows(self, show_id=0, episode_id=0):
        shows_template = my_lookup.get_template('shows.html')
        all_shows = cherrypy.request.db.query(Show).order_by(Show.show_name.asc()).all()
        if show_id == 0:
            latest_episode = cherrypy.request.db.query(Episode).filter(Episode.air_date <= datetime.today())\
                .order_by(Episode.air_date.asc()).first()
            current_show = latest_episode.show
        else:
            current_show = cherrypy.request.db.query(Show).filter(Show.show_id == show_id).first()
        return shows_template.render(shows=all_shows, current=current_show)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def show(self, id):
        try:
            show = cherrypy.request.db.query(Show).filter(Show.show_id == id).first()
            episodes = cherrypy.request.db.query(Episode).filter(Episode.show_id == show.show_id).order_by(Episode.air_date.desc()).all()
            stuff = (show, episodes)
        except Exception as ex:
            stuff = "{error: %s}" % Exception

        return jsonpickle.encode(stuff, max_depth=4, unpicklable=False)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update_episode(self):
        status = 'success'
        try:
            data = cherrypy.request.json
            episode_id = data['id']
            e = cherrypy.request.db.query(Episode).filter(Episode.id == episode_id).first()
            e.status = 'Pending' if e.status == 'Retrieved' else 'Retrieved'
            if e.status == 'Pending':
                e.reset()
            cherrypy.request.db.commit()
            status = e.status
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
            show_id = data['id']
            action = data['action']

            if action == 'refresh':
                MediaInteraction.update_one(show_id, cherrypy.request.db)

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
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def episode(self, id):
        e = cherrypy.request.db.query(Episode).filter(Episode.id == id).first()
        return jsonpickle.encode(e, max_depth=3, unpicklable=False)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def ajax_episode(self):
        ar = AjaxResponse('Links updated & download started.')
        try:
            # split by space and line return
            data = cherrypy.request.json
            links = data['episode-links-text']
            id = data['episode-detail-id-hidden']
            all_links = re.split('[\n\r\s]+', links)

            episode = cherrypy.request.db.query(Episode).filter(Episode.id == id).first();
            config = cherrypy.request.db.query(Config).first();
            LinkInteraction.process_tv_link(cherrypy.request.db, config, episode, all_links)

        except Exception as ex:
            ar.status = 'error'
            ar.message = str(Exception)

        return ar.to_JSON()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def check_links(self, **kwargs):
        try:
            links = [elem for elem in kwargs.values()][0]
            # split by space and line return
            all_links = re.split('[\n\r\s]+', links)

            b = mechanicalsoup.Browser()

            is_valid_links = True
            for l in all_links:
                if l.strip() == '':
                    continue
                else:
                    resp = b.get(l)
                    is_up = resp.status_code in [200]
                    if not is_up:
                        is_valid_links = False
                        break

            return is_valid_links

        except Exception as ex:
            return False

    # all for LOG PAGES#############################################


    @cherrypy.expose
    def log(self):
        log_template = my_lookup.get_template('log.html')
        logs = cherrypy.request.db.query(ActionLog).order_by(ActionLog.time_stamp.desc()).all()
        return log_template.render(log=logs)

    # all for config PAGES#############################################

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

    # all for Forum PAGES#############################################

    @cherrypy.expose
    def forums(self):
        forums_template = my_lookup.get_template('forums.html')
        data = cherrypy.request.db.query(ScanURL).order_by(ScanURL.priority.asc()).all()
        config = cherrypy.request.db.query(Config).first()


        return forums_template.render(sources=data, jd_link=config.jd_link)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def forum_check(self, id):
        try:
            forum = cherrypy.request.db.query(ScanURL).filter(ScanURL.id == id).first()
            b = mechanicalsoup.Browser()
            page = b.get(forum.domain)
            is_page_up = page.status_code in [200, 403]
        except Exception as ex:
            is_page_up = False
        return is_page_up


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

    # all for Index APIs #############################################

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
            action = data['action']

            if action == 'scan':
                LinkRetrieve.search_all(cherrypy.request.db)

            if action == 'refresh':
                MediaInteraction.update_all(cherrypy.request.db)
        except Exception as ex:
            ActionLog.log(str(ex))
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
    def all_episodes(self):
        all_template = my_lookup.get_template('all_episodes.html')

        all_episodes = cherrypy.request.db.query(Episode).order_by(Episode.air_date.desc()).all()
        pending_episodes = cherrypy.request.db.query(Episode).filter(Episode.status == 'Pending').order_by(Episode.air_date.asc()).all()
        downloaded_episodes = cherrypy.request.db.query(Episode).filter(Episode.status == 'Retrieved').order_by(Episode.air_date.desc()).all()
        missed_episodes = cherrypy.request.db.query(Episode).filter(Episode.status == 'Pending').filter(Episode.attempts > 0).order_by(Episode.air_date.desc()).all()

        return all_template.render(all=all_episodes, pending=pending_episodes, downloaded=downloaded_episodes, missed=missed_episodes)

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

    scan_refresh_scheduler.add_job(LinkRetrieve.search_all, 'cron', hour='*/' + str(config.scan_interval),
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


