import subprocess
import re
import glob

from .base import HoursDataSource
from lxml import etree
from lxml import objectify
from datetime import timedelta
from django.conf import settings
from django.utils.html import escape
from bs4 import BeautifulSoup
from dateutil import parser
from django.utils import timezone

class DataSource(HoursDataSource):
    def fetch(self):
        local_tz = timezone.get_current_timezone()
        print "Adium..."
        md_query = 'kMDItemFSCreationDate > $time.iso(%s)' % self.start_date.strftime('%Y-%m-%d')
        mdfind_command = ['mdfind',
                          '-onlyin',
                          settings.ADIUM_LOG_DIR,
                          md_query]
        chatlogs = subprocess.check_output(mdfind_command).split('\n')
        # Filename will be in the form of:
        # GTalk.me@mydomain.com/you@yourdomain.com/you@yourdomain.com (2014-07-27T21.08.24-0400)
        # .chatlog/you@yourdomain.com (2014-07-27T21.08.24-0400).xml
        for chatlog_dir in chatlogs:
            if not any(x in chatlog_dir
                       for x in settings.CHAT_INCLUDE):
                continue
            for chat_log in glob.glob('%s/*.xml' % chatlog_dir):
                chat_date = re.search('\(([-.\d\w]+)\)',
                                      chat_log).groups()[0].replace('.', ':')
                chat_date = parser.parse(chat_date)
                chat_date = local_tz.normalize(chat_date.replace(tzinfo=local_tz))
                # Bail out before reading the file if the date doesn't match what we want
                if not self.date_within_bounds(chat_date, give_or_take=timedelta(days=1)):
                    continue
                with open(chat_log, 'r') as fd:
                    try:
                        chat = objectify.XML(fd.read())
                    except BaseException as e:
                        print "Error on %s" % chat_log
                        continue
                has_chat_username = re.search('Logs/[.@\-\w]+/(?P<username>[.@\-\w]+)/', chat_log)
                if not has_chat_username:
                    print "No chat username: %s" % chat_log
                    continue
                chat_username = has_chat_username.group('username')
                for msg in getattr(chat, 'message', []):
                    chat_date = parser.parse(msg.attrib['time'])
                    if chat_date < self.start_date or chat_date > self.end_date: continue
                    if msg.div is None: continue
                    soup = BeautifulSoup(etree.tostring(msg.div, encoding='utf-8'))

                    for tag in soup.findChildren('div'):
                        del tag['xmlns']
                        for span in tag.find_all('span'):
                            del span['style']
                    title = '<b>%s:</b> %s' % (msg.attrib['sender'],
                                               escape(soup.div.get_text()))
                    self.add_entry(date=chat_date, title=self.truncate(title, 150),
                                   mouseover=u'{0}: {1}'.format(msg.attrib['sender'],
                                                         escape(unicode(soup.div.get_text()))),
                                   url='ADIUM: %s' % chat_username,
                                   css_class= 'chat')