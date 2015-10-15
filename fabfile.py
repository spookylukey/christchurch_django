import os
import os.path
import posixpath

from fabric.api import run, local, abort, env, put, get, task
from fabric.contrib.files import exists
from fabric.context_managers import cd, lcd, settings, hide
import psutil

#  fabfile for deploying Christ Church website
#
# == Overview ==
#
# === Development ===
#
# You need a root directory to hold everything, and the following
# sub directories:
#
#  project/    - holds a checkout of this repository
#                i.e. fabfile.py and siblings live in that dir.
#
#  usermedia/  - corresponds to MEDIA_ROOT
#
# === Bootstrapping ===
#
# Steps needed on a new server:
# - create custom app on webfaction.
# - create static app on webfaction
# - create usermedia app on webfaction
# - create database on webfaction
#
# Then deploy using this fabfile

# Remember to add password info to ~/.pgpass

# Some information here about paths has to correspond to that found in
# settings.py or settings_priv.py


USER = 'cciw'
HOST = 'cciw.co.uk'
APP_NAME = 'christchurch'
APP_PORT = 29584
GUNICORN_WORKERS = 2

# Host and login username:
env.hosts = ['%s@%s' % (USER, HOST)]

# Directory where everything to do with this app will be stored on the server.
DJANGO_APP_ROOT = '/home/%s/webapps/%s_django' % (USER, APP_NAME)

# Directory where static sources should be collected.  This must equal the value
# of STATIC_ROOT in the settings.py that is used on the server.
STATIC_ROOT = '/home/%s/webapps/%s_static/' % (USER, APP_NAME)

# This must equal the value of MEDIA_ROOT in settings.py
MEDIA_ROOT =  '/home/%s/webapps/%s_usermedia/' % (USER, APP_NAME)

# Subdirectory of DJANGO_APP_ROOT in which project sources will be stored
SRC_SUBDIR = 'src'

# Subdirectory of DJANGO_APP_ROOT in which virtualenv will be stored
VENV_SUBDIR = 'venv'

# Python version
PYTHON_BIN = "python2.7"
PYTHON_PREFIX = "" # e.g. /usr/local  Use "" for automatic
PYTHON_FULL_PATH = "%s/bin/%s" % (PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX else PYTHON_BIN

GUNICORN_PIDFILE = "%s/gunicorn.pid" % DJANGO_APP_ROOT
GUNICORN_LOGFILE = "/home/%s/logs/user/gunicorn_%s.log" % (USER, APP_NAME)

SRC_DIR = posixpath.join(DJANGO_APP_ROOT, SRC_SUBDIR)
VENV_DIR = posixpath.join(DJANGO_APP_ROOT, VENV_SUBDIR)

WSGI_MODULE = '%s.wsgi' % APP_NAME


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(THIS_DIR)
MEDIA_ROOT_LOCAL = os.path.join(PARENT_DIR, 'usermedia')


DB_NAME = 'cciw_christchurch'
DB_USER = 'cciw_christchurch'
DB_NAME_DEV = 'christchurch'
DB_USER_DEV = 'christchurch'

def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.venv + " && " + command, **kwargs)


def install_dependencies():
    ensure_virtualenv()
    with virtualenv(VENV_DIR):
        with cd(SRC_DIR):
            run_venv("pip install -r requirements.txt")


def ensure_virtualenv():
    if exists(VENV_DIR):
        return

    with cd(DJANGO_APP_ROOT):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, VENV_SUBDIR))
        run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
            (SRC_DIR, VENV_SUBDIR, PYTHON_BIN))


def ensure_src_dir():
    if not exists(SRC_DIR):
        run("mkdir -p %s" % SRC_DIR)
    with cd(SRC_DIR):
        if not exists(posixpath.join(SRC_DIR, '.hg')):
            run("hg init")


@task
def push_rev(rev):
    """
    Use the specified revision for deployment, instead of the current revision.
    """
    env.push_rev = rev


def push_sources():
    """
    Push source code to server.
    """
    ensure_src_dir()
    push_rev = getattr(env, 'push_rev', None)
    if push_rev is None:
        push_rev = local("hg id", capture=True).split(" ")[0].strip().strip("+")

    local("hg push -f ssh://%(user)s@%(host)s/%(path)s || true" %
          dict(host=env.host,
               user=env.user,
               path=SRC_DIR,
               ))
    with cd(SRC_DIR):
        run("hg update %s" % push_rev)


@task
def webserver_stop():
    """
    Stop the webserver that is running the Django instance
    """
    run("kill $(cat %s)" % GUNICORN_PIDFILE)
    run("rm %s" % GUNICORN_PIDFILE)


def _webserver_command():
    return ("%(venv_dir)s/bin/gunicorn --log-file=%(logfile)s -b 127.0.0.1:%(port)s -D -w %(workers)s --pid %(pidfile)s %(wsgimodule)s:application" %
            {'venv_dir': VENV_DIR,
             'pidfile': GUNICORN_PIDFILE,
             'wsgimodule': WSGI_MODULE,
             'port': APP_PORT,
             'workers': GUNICORN_WORKERS,
             'logfile': GUNICORN_LOGFILE,
             }
            )


@task
def webserver_start():
    """
    Starts the webserver that is running the Django instance
    """
    run(_webserver_command())


@task
def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    try:
        run("kill -HUP $(cat %s)" % GUNICORN_PIDFILE)
    except:
        webserver_start()


def _is_webserver_running():
    try:
        pid = int(open(GUNICORN_PIDFILE).read().strip())
    except (IOError, OSError):
        return False
    for ps in psutil.process_iter():
        if (ps.pid == pid and
            any('gunicorn' in c for c in ps.cmdline)
            and ps.username == USER):
            return True
    return False


@task
def local_webserver_start():
    """
    Starts the webserver that is running the Django instance, on the local machine
    """
    if not _is_webserver_running():
        local(_webserver_command())


def build_static():
    with virtualenv(VENV_DIR):
        with cd(SRC_DIR):
            run_venv("./manage.py collectstatic -v 0 --noinput --clear")

    run("chmod -R ugo+r %s" % STATIC_ROOT)


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


def update_database():
    with virtualenv(VENV_DIR):
        with cd(SRC_DIR):
            if getattr(env, 'initial_deploy', False):
                run_venv("./manage.py syncdb --all")
                run_venv("./manage.py migrate --fake --noinput")
            else:
                run_venv("./manage.py syncdb --noinput")
                run_venv("./manage.py migrate --noinput")


@task
def deploy():
    """
    Deploy project.
    """
    push_sources()
    _push_non_vcs_sources()
    install_dependencies()
    update_database()
    build_static()
    with settings(warn_only=True):
        webserver_stop()
    webserver_start()


def _push_non_vcs_sources():
    # Also need to sync files that are not in main sources VCS repo.
    local("rsync christchurch/settings_priv.py cciw@christchurchbradford.org.uk:%s/christchurch/settings_priv.py" % SRC_DIR)




@task
def get_live_db():
    filename = "dump_%s.db" % DB_NAME
    run("pg_dump -Fc -U %s -O -o -f ~/%s %s" % (DB_USER, filename, DB_NAME))
    get("~/%s" % filename)


@task
def local_restore_from_dump(filename):
    # DB might not exist, allow error
    commands = """
DROP DATABASE %(DB)s;
CREATE DATABASE %(DB)s;
CREATE USER %(USER)s WITH PASSWORD 'foo';
GRANT ALL ON DATABASE %(DB)s TO %(USER)s;
ALTER USER %(USER)s CREATEDB;
""" % {'DB': DB_NAME_DEV, 'USER': DB_USER_DEV}

    for c in commands.strip().split('\n'):
        local("""sudo -u postgres psql -U postgres -d template1 -c "%s" | true """
              % c)

    local("pg_restore -O -U %s -d %s %s" %
          (DB_USER_DEV, DB_NAME_DEV, filename))


def upload_usermedia():
    local("chmod ugo+r  -R %s/*" % MEDIA_ROOT_LOCAL)
    local("rsync -z -r --exclude='*.mp3' %s/ cciw@christchurchbradford.org.uk:%s" % (MEDIA_ROOT_LOCAL, MEDIA_ROOT), capture=False)


def upload_sermons():
    local("chmod ugo+r  %s/downloads/sermons/*" % MEDIA_ROOT_LOCAL)
    local("rsync -v --progress --size-only %s/downloads/sermons/* cciw@christchurchbradford.org.uk:%s/downloads/sermons" % (MEDIA_ROOT_LOCAL, MEDIA_ROOT))


@task
def backup_usermedia():
    local("rsync -z -r --progress cciw@christchurchbradford.org.uk:%s/ %s" % (MEDIA_ROOT, MEDIA_ROOT_LOCAL), capture=False)



# TODO:
#  - backup db task. This should be run only in production, and copies
#    files to Amazon S3 service.
