import pytz
from datetime import timedelta
from dateutil import parser
from django.utils.text import Truncator
from django.db import IntegrityError

from core.models import Data

class HoursDataSource(object):

    def __init__(self, start_date, end_date):
        self.entries = []
        self.start_date = start_date
        self.end_date = end_date

    def truncate(self, text, length):
        return Truncator(text).chars(length)

    def date_within_bounds(self, date, give_or_take=None):
        start_date = self.start_date
        end_date = self.end_date
        if give_or_take is not None:
            start_date -= give_or_take
            end_date += give_or_take
        return start_date <= date <= end_date

    def get_group_date(self, date):
        return date + timedelta(days=-date.weekday())
        # return date.replace(day=1)

    def add_entry(self, date, title, mouseover, url, css_class):
        try:
            Data.objects.create(date=date, title=title, mouseover=mouseover,
                                url=url, css_class=css_class)
        except IntegrityError:
            pass

    def date_within_bounds(self, date, give_or_take=None):
        start_date = self.start_date
        end_date = self.end_date
        if give_or_take is not None:
            start_date -= give_or_take
            end_date += give_or_take
        return start_date <= date <= end_date
