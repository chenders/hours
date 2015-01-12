import os
import glob
import shutil
import sqlite3

import pytz
from dateutil import parser
from django.db import IntegrityError
from django.conf import settings
from django.utils.html import escape

from .base import HoursDataSource

class DataSource(HoursDataSource):

    def fetch(self):
        if settings.VERBOSE:
            print "Chrome history..."
        if 'CHROME' not in settings.DS or 'HISTORY' not in settings.DS['CHROME']:
            raise BaseException("Chrome history location not specified.")
        start_time = self.start_date.strftime('%s')
        end_time = self.end_date.strftime('%s')
        # See http://linuxsleuthing.blogspot.ca/2011/06/decoding-google-chrome-timestamps-in.html
        query = """SELECT DATETIME((visit_time/1000000)-11644473600, 'unixepoch') AS dt,
                title, urls.url
                FROM urls, visits WHERE urls.id = visits.url
                AND (visit_time/1000000)-11644473600 > %s
                AND (visit_time/1000000)-11644473600 < %s
                ORDER BY visit_time ASC;""" % (start_time, end_time)
        copied_file = os.path.join(settings.BASE_DIR, 'data/chrome/History')
        orig_file = settings.DS['CHROME']['HISTORY']
        # Copy file if we haven't copied it before, or if it's outdated
        if not os.path.exists(copied_file) or os.stat(orig_file).st_mtime - os.stat(copied_file).st_mtime > 0:
            print "Copying history"
            shutil.copy2(orig_file, copied_file)
        conn = sqlite3.connect(copied_file)
        cursor = conn.cursor()
        db_results = cursor.execute(query)
        for date_string, url_title, url in db_results:
            date = parser.parse(date_string).replace(tzinfo=pytz.UTC)
            self.add_entry(date, escape(url_title[:80]), escape(url_title[:80]), escape(url[:80]), 'url')
        conn.close()
