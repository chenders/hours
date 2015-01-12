from datetime import datetime
import importlib
from optparse import make_option

from dateutil import parser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import pytz

class Command(BaseCommand):
    args = '<start_date end_date>'
    help = ''

    option_list = BaseCommand.option_list + (
        make_option('--all',
                    action='store_true',
                    dest='all',
                    default=False,
                    help='Import from all data sources'),
    )

    def handle(self, start_date, end_date, **options):
        tz = pytz.timezone(settings.HOURS_TZ)
        timezone.activate(tz)
        start_date = tz.normalize(datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=tz))
        end_date = tz.normalize(parser.parse('%s 23:59:59' % end_date).replace(tzinfo=tz))
        for ds in settings.HOURS_DATASOURCES:
            mod = importlib.import_module(ds)
            datasource = mod.DataSource(start_date, end_date)
            datasource.fetch()
