import urllib
import cherrypy
from sqlalchemy import Column, String, Integer, ForeignKey, Date, Boolean, DateTime, create_engine, Numeric
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from cherrypy.process import wspbus, plugins
import os
import re
import datetime

hide_chars = ['e', 'l', 'o']
space_chars = ['.',' ','_']

Base = declarative_base()


class Show(Base):
    __tablename__ = 'show'
    show_id = Column(Integer, primary_key=True)
    show_name = Column(String)
    first_aired = Column(Date)
    is_active = Column(Boolean, default=True)
    banner = Column(String)
    poster = Column(String)
    thumb = Column(String)
    background = Column(String)
    large_image = Column(String)
    show_directory = Column(String)
    regex = Column(String)
    last_updated = Column(DateTime, default=datetime.datetime.now())
    overview = Column(String)
    name_override = Column(String)

    def __str__(self):
        return "%s - %s" % (self.show_name, self.show_id)

    def make_regex(self):
        regex_name = self.show_name.lower()
        for char in hide_chars:
            regex_name = regex_name.replace(char, '[a-zA-Z0-9]')

        # for char in space_chars:
        #     regex_name = regex_name.replace(char, '[\s\.\\_]')
        #
        # for a in ['&', 'and']:
        #     regex_name = regex_name.replace(a, '(and)&')
        self.regex = regex_name


class Episode(Base):
    __tablename__ = 'episode'
    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, ForeignKey('show.show_id'))
    show = relationship(Show, backref=backref('episodes', cascade='delete'))
    season_number = Column(Integer)
    episode_number = Column(Integer)
    episode_name = Column(String)
    air_date = Column(Date)
    status = Column(String, default='Retrieved') # 'Pending', 'Retrieved'
    attempts = Column(Integer, default=0)
    retrieved_on = Column(Date)
    episode_description = Column(String)
    url_download_source = Column(String)
    is_downloaded = Column(Boolean, default=False)
    is_found = Column(Boolean, default=False)
    parent_download_page = Column(String)
    download_links = Column(String)
    download_time = Column(DateTime)
    episode_image = Column(String)
    last_updated = Column(DateTime)
    is_download_validated = Column(Boolean, default=False)

    def __str__(self):
        return "%s s%se%s" % (self.show.show_name, str(self.season_number).zfill(2), str(self.episode_number).zfill(2))

    def get_episode_name(self):
        return self.episode_name

    def episode_in_link(self, link_text):
        episode_id_string = 's%se%s' % (str(self.season_number).zfill(2),
                                        str(self.episode_number).zfill(2))
        episode_id_string = episode_id_string.lower()

        if (episode_id_string in link_text) and len(re.findall(self.show.regex, link_text)) > 0:
            return True
        else:
            return False

    def reset(self):
        self.retrieved_on = None
        self.is_downloaded = False
        self.is_found = False
        self.download_time = None
        self.url_download_source = ''
        self.parent_download_page = ''
        self.download_links = ''
        self.parent_download_page = ''


class PremierShow(Base):
    __tablename__ = 'premiershow'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    poster = Column(String)
    overview = Column(String)
    first_aired = Column(Date)

class PopularShow(Base):
    __tablename__ = 'popularshow'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    poster = Column(String)
    overview = Column(String)
    first_aired = Column(Date)

class ScanURL(Base):
    __tablename__ = 'scanurl'
    id = Column(Integer, primary_key=True)
    username = Column(String, default='myusername')
    password = Column(String, default='mypassword')
    login_page = Column(String, default='http://tehparadox.com/forum/')  # 'http://tehparadox.com/forum/'
    url = Column(String, default='myurl')
    priority = Column(Integer, nullable=True)
    domain = Column(String, default='http://www.domain.com/')
    logo_image = Column(String, default='/static/forum.png')

    def __str__(self):
        return self.domain


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    tmdb_id = Column(Integer)
    name = Column(String)
    link_text = Column(String)
    status = Column(String, default='Not Retrieved')
    title = Column(String)
    tmdb_rating = Column(String)
    poster = Column(String)
    overview = Column(String)
    actors = Column(String)
    links = Column(String)
    video_format = Column(String)
    audio_format = Column(String)
    source_format = Column(String)

    def get_name_and_year(self):
        release_date_list = re.findall('[\(]?[0-9]{4}[\)]?', self.name)
        # s = re.sub('[\(][0-9]{4}[\)]', '', self.name)
        s = self.name.replace('(', '|').replace('Part', '|').replace('Season', '|')
        s = s.split('|')[0].strip()
        if len(release_date_list) > 0:
            release_date = release_date_list[0].replace('(', '').replace(')', '')
        else:
            release_date = ''

        return s, release_date

    def get_video_formats(self):
        source_formats = {'HDTV': 'HDTV', 'HD-TV':'HDTV', 'Bluray': 'BluRay', 'DVD': 'DVD', 'WEB-DL': 'WEB-DL',
                          'WEB DL':'WEB-DL', 'WEBDL': 'WEB-DL'}
        audio_formats = {'DD5': 'DD5.1', 'DD': 'DD5.1', 'AAC2': 'AAC2.0', 'AAC': 'AAC2.0', 'DTS HD': 'DTS-HD',
                         'DTS-HD':'DTS-HD', 'DTS': 'DTS', 'TrueHD':'TrueHD'}

        if '1080p' in self.name:
            self.video_format = '1080p'
        elif '720p' in self.name:
            self.video_format = '720p'
        else:
            self.video_format = 'other res'

        source = {k: v for k,v in source_formats.items() if k.lower() in self.name.lower()}
        if not source:
            self.source_format = 'other source'
        else:
            self.source_format = next(iter(source.values()))

        audio = {k: v for k,v in audio_formats.items() if k.lower() in self.name.lower()}
        if not audio:
            self.audio_format = 'other audio'
        else:
            self.audio_format = next(iter(audio.values()))


class ActionLog(Base):
    __tablename__ = 'actionlog'
    id = Column(Integer, primary_key=True)
    time_stamp = Column(DateTime)
    message = Column(String)

    def get_display(self):
        return '%s -- %s' % (self.time_stamp, self.message)

    @staticmethod
    def log(msg):
        # clean up the log file to keep it to the last 2000 records
        s = connect()
        l = ActionLog(time_stamp=datetime.datetime.now(), message=msg)
        s.add(l)

        all_logs = s.query(ActionLog).all()
        if len(all_logs) == 3000:
            entries_to_delete = all_logs[:2000]
            for e in entries_to_delete:
                s.delete(e)
        s.commit()


class LinkIndex(Base):
    __tablename__ = "linkindex"
    id = Column(Integer, primary_key=True)
    link_text = Column(String)
    link_url = Column(String)


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    crawljob_directory = Column(String, default='')
    tv_parent_directory = Column(String, default='')
    movies_directory = Column(String, default='')
    file_host_domain = Column(String, default='uploaded.net')  # 'uploaded.net'
    hd_format = Column(String, default='720p')  # only 720p or 1080p
    ip = Column(String, default='127.0.0.1')
    port = Column(String, default='8080')
    scan_interval = Column(Integer, default=12)
    refresh_day = Column(String, default='sun')
    refresh_hour = Column(Integer, default=2)
    jd_link = Column(String, default='')
    jd_path = Column(String, default='')
    last_update = Column(DateTime, default=datetime.datetime.now())

    @staticmethod
    def get_hours():
        return list(range(1, 25))

    @staticmethod
    def get_intervals():
        return list(range(2, 13))

    def is_populated(self):
        if not self.crawljob_directory and not self.tv_parent_directory and not self.movies_directory:
            return False
        else:
            return True

    def domain_link_check(self, link):
        domains = self.file_host_domain.split(',')
        file_host_exists = False
        for d in domains:
            if d.strip() in link:
                file_host_exists = True
                break
        return file_host_exists
        # http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html

    def refresh_day_of_week(self):
        d = {'sun':'Sunday','mon':'Monday','tue':'Tuesday','wed':'Wednesday','thu':'Thursday','fri':'Friday','sat':'Saturday'}

        return d[self.refresh_day]


def connect():
    data_file = os.path.normpath(os.path.abspath(__file__))
    print(data_file)
    data_dir = os.path.dirname(data_file)
    db_path = data_dir + '/db.sqlite3'
    print('DB Path: %s' % db_path)
    # engine = create_engine('sqlite:///db.sqlite3', connect_args={'check_same_thread':False})
    engine = create_engine('sqlite:///%s' % db_path, echo=True)
    session_factory = sessionmaker()
    session_factory.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = scoped_session(session_factory)
    return s


# http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html
class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)
        self.sa_engine = None
        self.bus.subscribe("bind", self.bind)

    def start(self):
        data_file = os.path.normpath(os.path.abspath(__file__))
        print(data_file)
        data_dir = os.path.dirname(data_file)
        db_path = data_dir + '/db.sqlite3'
        print('DB Path: %s' % db_path)
        self.sa_engine = create_engine('sqlite:///%s' % db_path, echo=True)
        Base.metadata.create_all(self.sa_engine)

    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self, session):
        session.configure(bind=self.sa_engine)


class SATool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'on_start_resource',
                               self.bind_session,
                               priority=20)
        self.session = scoped_session(sessionmaker(autoflush=True, autocommit=False))

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource', self.commit_transaction, priority=80)

    def bind_session(self):
        cherrypy.engine.publish('bind', self.session)
        cherrypy.request.db = self.session

    def commit_transaction(self):
        cherrypy.request.db = None
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.remove()
