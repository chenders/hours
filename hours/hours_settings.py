import os
import platform
from os.path import expanduser
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VERBOSE = True

OUTPUT_DIR = os.path.join(BASE_DIR, 'out/')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates/')

DB_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
FILE_DATE_FORMAT = '%Y-%m-%d'
DATA_GROUP_DATE_FORMAT = '%Y-%m-%d %H'
ENTRY_DATE_FORMAT = '%Y-%m-%d %H:%M'

HIDDEN_KEYWORDS = {
    'url': [],
    'title': []
}

BILLABLE_KEYWORDS = {
    'url': ['python'],
    'title': []
}
VERBOSE = True
HOURS_DATASOURCES = [
    'sources.adium',
    'sources.chrome',
]

CHAT_INCLUDE = ['myworkbudz']

HOURS_TZ = 'America/New_York'

platform_name = platform.system()
DS = {}

DS['CHROME'] = {}
DS['ADIUM'] = {}
if platform_name == 'Darwin':
    DS['CHROME']['HISTORY'] = expanduser('~/Library/Application Support/Google/Chrome/Default/History')
    DS['ADIUM']['LOGS'] = expanduser('~/Library/Application Support/Adium 2.0/Users/Default/Logs')
elif platform_name == 'Windows':
    DS['CHROME']['HISTORY'] = expanduser('~/Local Settings/Application Data/Google/Chrome/User Data/Default/History')
elif platform_name == 'Linux':
    DS['CHROME']['HISTORY'] = expanduser('~/.config/chromium/Default/History')
