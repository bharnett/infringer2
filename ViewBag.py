import Models
from Models import AddableShow, Show, Episode, Movie
import datetime


class ViewBag(object):
    def __init__(self):
        self.premiers = []
        self.popular = []
        self.movies = []
        self.this_week = []
        self.db = Models.connect()

    def populate_addables(self):
        self.premiers = self.db.query(AddableShow).filter(AddableShow.addable_type == 'premier').all()
        self.popular = self.db.query(AddableShow).filter(AddableShow.addable_type == 'popular').all()
        self.movies = self.db.query(Movie).filter(Movie.status == 'Ready').all()

        #get only for this week:
        today = datetime.date.today()
        dates = [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        self.this_week = self.db.query(Episode).filter(dates[0] <= Episode.air_date <= dates[6]).all()


vb = ViewBag()
vb.populate_addables()
