import codecs
import json
import os
from datetime import datetime, timedelta
from functools import total_ordering
from json import JSONEncoder

from dateutil import parser
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz

from core.models import Data

class CustomJSONEncoder(JSONEncoder):
    """JSON serializer to serialize OutputEntry and datetime objects properly"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(settings.ENTRY_DATE_FORMAT)
        elif isinstance(obj, OutputEntry):
            return obj.__dict__
        else:
            return super(CustomJSONEncoder, self).default(obj)

@total_ordering
class OutputEntry(object):
    date = None
    title = None
    url = None
    css_class = None
    hidden = False
    is_billable = False

    def __init__(self, date, title, url, mouseover, css_class='', hidden=False, is_billable=False):
        self.date = date
        self.title = title
        self.url = url
        self.mouseover = mouseover
        self.css_class = css_class
        self.hidden = hidden
        self.is_billable = is_billable

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '%s : %s' % (self.date.isoformat(), self.title)

    def __eq__(self, other):
        return self.date == other.date

    def __lt__(self, other):
        return self.date < other.date

class Command(BaseCommand):
    args = '<start_date end_date>'
    help = ''
    facility = None
    output_dir = None


    def _round_time(self, tm):
        discard = timedelta(minutes=tm.minute % 15,
                            seconds=tm.second,
                            microseconds=tm.microsecond)
        tm -= discard
        if discard >= timedelta(minutes=7.5):
            tm += timedelta(minutes=15)
        return tm

    def _get_group_date(self, date):
        return date + timedelta(days=-date.weekday())

    def handle(self, start_date, end_date, **options):
        tz = pytz.timezone(settings.HOURS_TZ)
        timezone.activate(tz)
        start_date = tz.normalize(datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz))
        end_date = tz.normalize(parser.parse('%s 23:59:59' % end_date).replace(tzinfo=tz))
        entries = {}
        for data in Data.objects.filter(date__range=(start_date, end_date)):
            data_date = tz.normalize(data.date.astimezone(tz))
            group_date = (data_date + timedelta(days=-data_date.weekday())).strftime(settings.FILE_DATE_FORMAT)
            entry_date = data_date.strftime(settings.FILE_DATE_FORMAT)
            entries.setdefault(group_date, {})
            entries[group_date].setdefault(entry_date, [])
            entries[group_date][entry_date].append(
                OutputEntry(date=data_date,
                            title=data.title,
                            url=data.url,
                            mouseover=data.mouseover,
                            css_class=data.css_class)
            )
        outdir = os.path.join(settings.BASE_DIR, 'out')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for filedate in sorted(entries.keys()):
            with codecs.open(os.path.join(outdir, '%s.js' % filedate), 'w', encoding='UTF-8') as fd:
                data = {
                    'entries': [],
                    'dates': [],
                }
                for entry_date in sorted(entries[filedate]):
                    data['entries'].append({
                        'date': entry_date,
                        'entries': entries[filedate][entry_date],
                    })
                    data['dates'].append(entry_date)
                fd.write('var hours = %s' % json.dumps(data, cls=CustomJSONEncoder, indent=2))
