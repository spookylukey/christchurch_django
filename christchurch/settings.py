# settings for christchurch project.

import os
import socket
import sys

hostname = socket.gethostname()

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ../
parentdir = os.path.dirname(basedir)

DEVBOX = ('webfaction' not in hostname)
LIVEBOX = not DEVBOX

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
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'christchurch',
            'USER': 'christchurch',
            'PASSWORD': 'foo',
            'HOST': 'localhost',
            'PORT': 5432,
            }
        }
else:
    from .settings_priv import DATABASES

if DEVBOX:
    # Don't want to use WebFaction API from development
    WEBFACTION_PASSWORD = None
    WEBFACTION_USER = None


ADMINS = (
    ('Christ Church webmaster', 'webmaster@christchurchbradford.org.uk'),
)

MANAGERS = ADMINS

TIME_ZONE = "Europe/London"

LANGUAGES = [
    ('en', 'English'),
]
DEFAULT_LANGUAGE = 0

LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_I18N = False

USE_L10N = False


if DEVBOX:
    STATIC_ROOT = os.path.join(parentdir, 'static')
    MEDIA_ROOT = os.path.join(parentdir, 'usermedia')
else:
    from .settings_priv import STATIC_ROOT, MEDIA_ROOT, GOOGLE_ANALYTICS_ACCOUNT

MEDIA_URL = '/usermedia/'
STATIC_URL = '/static/'


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
    'pagination.middleware.PaginationMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'christchurch.processors.common',
    'sekizai.context_processors.sekizai',
]

ROOT_URLCONF = 'christchurch.urls'

INSTALLED_APPS = [
    'christchurch',  # Our templates before anyone else's
    'sermons',
    'contacts',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'cms',
    'menus',
    'mptt',
    'sekizai',
    'appmedia',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',
    'cms.plugins.googlemap',
    'semanticeditor',
    'pagination',
    'cmsplugin_gallery',
    'easy_thumbnails',
    'inline_ordering',
]

SOUTH_MIGRATION_MODULES = {
        'easy_thumbnails': 'easy_thumbnails.south_migrations',
    }


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

FILE_UPLOAD_PERMISSIONS = 0644

#####  EMAIL  #######

SEND_BROKEN_LINK_EMAILS = False

if DEVBOX:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
    SERVER_EMAIL = "website@christchurchbradford.org.uk"
    DEFAULT_FROM_EMAIL = SERVER_EMAIL
    EMAIL_HOST = "smtp.webfaction.com"
    from .settings_priv import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


## WEBFACTION API

from .settings_priv import WEBFACTION_USER, WEBFACTION_PASSWORD

SEMANTICEDITOR_MEDIA_URL = os.path.join(STATIC_URL, "semanticeditor/")


if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS.append("django.core.context_processors.debug")
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
    MIDDLEWARE_CLASSES.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS.append("debug_toolbar")
