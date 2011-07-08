# settings for christchurch project.

import os
import socket
import sys

hostname = socket.gethostname()

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ../
parentdir = os.path.dirname(basedir)

DEVBOX = ('webfaction' not in hostname)
LIVEBOX = not DEVBOX

if LIVEBOX:
    from .settings_priv import PRODUCTION, STAGING

WEBSERVER_RUNNING = 'mod_wsgi' in sys.argv

if DEVBOX:
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False

if DEVBOX:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '../christchurchbradford.db',
            }
        }
else:
    from .settings_priv import DATABASES


ADMINS = (
    ('Christ Church webmaster', 'webmaster@christchurchbradford.org.uk'),
)

MANAGERS = ADMINS

TIME_ZONE = "Europe/London"

LANGUAGES = [('en', 'en')]
DEFAULT_LANGUAGE = 0

LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

USE_I18N = False

USE_L10N = False

STATIC_ROOT = os.path.join(parentdir, 'static')

if DEVBOX:
    MEDIA_ROOT = os.path.join(parentdir, 'usermedia')
else:
    from .settings_priv import MEDIA_ROOT, GOOGLE_ANALYTICS_ACCOUNT

MEDIA_URL = '/usermedia/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

from .settings_priv import SECRET_KEY

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.media.PlaceholderMediaMiddleware',
    'pagination.middleware.PaginationMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'christchurch.processors.common',
]

ROOT_URLCONF = 'christchurch.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'christchurch',
    'sermons',
    'cms',
    'menus',
    'mptt',
    'appmedia',
    'south',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',
    'cms.plugins.googlemap',
    'semanticeditor',
    'pagination',
]

CMS_TEMPLATES = (
    ('standard.html', 'Standard Template'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 262144

DEFAULT_FILE_STORAGE = 'christchurch.files.FriendlyFileSystemStorage'


#####  EMAIL  #######

if DEVBOX:
    # For e-mail testing, use fakemail
    EMAIL_HOST = 'localhost'
    EMAIL_HOST_USER = None
    EMAIL_HOST_PASSWORD = None
    EMAIL_PORT = 8025
    SEND_BROKEN_LINK_EMAILS = True

else:
    SERVER_EMAIL = "website@christchurchbradford.org.uk"
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    EMAIL_HOST = "smtp.webfaction.com"
    from .settings_priv import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

    SEND_BROKEN_LINK_EMAILS = False


SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")


if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS.append("django.core.context_processors.debug")
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    MIDDLEWARE_CLASSES.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS.append("debug_toolbar")
