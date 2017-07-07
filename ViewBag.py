import Models
from Models import AddableShow, Show, Episode, Movie, Config
import datetime
from sqlalchemy import func


class ViewBag(object):
    def __init__(self):
        self.premiers = []
        self.popular = []
        self.movies = []
        self.this_week = []
        self.db = Models.connect()
        self.jd_link = ''
        self.dates =[]

    def populate_addables(self):
        self.premiers = self.db.query(AddableShow).filter(AddableShow.addable_type == 'premier').all()
        self.popular = self.db.query(AddableShow).filter(AddableShow.addable_type == 'popular').all()
        self.movies = self.db.query(Movie).filter(Movie.status == 'Ready').all()

        #get only for this week:
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(-1 - today.weekday(), 6 - today.weekday())]

        self.this_week = self.db.query(Episode).filter(dates[0] <= Episode.air_date)\
            .filter(Episode.air_date <= dates[6]).order_by(Episode.air_date).all()
        self.dates = dates
        #for the movies
        self.movies = self.db.query(Movie).filter(Movie.status == 'Ready').all()

        config = self.db.query(Config).first()
        self.jd_link = config.jd_link

# vb = ViewBag()
# vb.populate_addables()
