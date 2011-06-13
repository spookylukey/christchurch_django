from collections import namedtuple
from datetime import datetime
from fabric.api import run, local, abort, env, put
from fabric.contrib import files
from fabric.contrib import console
from fabric.decorators import hosts, runs_once
from fabric.context_managers import cd, lcd, settings, hide
import os
import os.path
join = os.path.join
import sys

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
# === Deployment ===
#
# There are two targets, STAGING and PRODUCTION, which live on the same
# server. They are almost identical, with these differences:
# - STAGING is on staging.christchurchbradford.org.uk
# - PRODUCTION is on www.christchurchbradford.org.uk
# - They have different databases
# - They have different apps on the webfaction server
#    - for the django project app
#    - for the static app
#
# settings_local.py and settings.py controls these things.
#
# In each target, we aim for atomic switching from one version to the next.
# This is not quite possible, but as much as possible the different versions
# are kept separate, preparing the new one completely before switching to it.
#
# To achieve this, new code is uploaded to a new 'dest_dir' which is timestamped,
# inside the 'src' dir in the christchurch app directory.

# /home/cciw/webapps/christchurch/         # PRODUCTION or
# /home/cciw/webapps/christchurch_staging/ # STAGING
#    src/
#       src-2010-10-11_07-20-34/
#          env/                    # virtualenv dir
#          project/                # uploaded from local
#          deps/
#            django/
#            django-mailer/        # etc
#          static/                 # built once uploaded
#       current/                   # symlink to src-???

# At the same level as 'src-2010-10-11_07-20-34', there is a 'current' symlink
# which points to the most recent one. The apache instance looks at this (and
# the virtualenv dir inside it) to run the app.

# There is a webfaction app that points to src/current/static for serving static
# media. (One for production, one for staging). There is also a 'christchurch_usermedia'
# app which is currently shared between production and staging. (This will only
# be a problem if usermedia needs to be re-organised).

# Code is deployed by pushing dev code to bitbucket, then pulling.

# When deploying, once the new directory is ready, the apache instance is
# stopped, the database is upgraded, and the 'current' symlink is switched. Then
# the apache instance is started.

# The information about this layout is unfortunately spread around a couple of
# places - this file and the settings file - because it is needed in both at
# different times.

# === Bootstrapping ===
#
# Steps needed on a new server:
# - create 'Django' app on webfaction.
# - create static app on webfaction
# - create usermedia app on webfaction
#
# - create the basic project layout
#   with 'src1' for sources and 'current' symlink
# - create a virtualenv
# - remove old stuff
#   - lib dir
#   - myproject
# - rename myproject.wsgi to project.wsgi
#   - replace 'myproject' with 'christchurch'
# - fix Apache config
#   - project.wsgi instead of myproject
#   - no need for path mangling
# - fix apache start/stop commands to activate the virtualenv

# $ cd ~/webapps/christchurch_django/
# $ mkdir src
## $ cd src
## $ mkdir src1
## $ ln -s src1 current
## $ cd src1
## $ virtualenv -p python2.7 env
## $ cd ../../
# $ mv myproject.wsgi project.wsgi
# $ replace myproject christchurch -- project.wsgi
# $ rm -rf myproject/
# $ rm -rf lib/
# $ emacs apache/bin/start
# # Add:
# . $HOME/webapps/christchurch_django/src/current/env/bin/activate

# Then deploy using this fabfile

# Then create webfaction app for static media

# Same again for christchurch_django_staging, with a different
# webapp dir and venv dir

env.hosts = ["cciw@christchurchbradford.org.uk"]

this_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(this_dir)
webapps_root = '/home/cciw/webapps'

# The path (relative to parent_dir) to where the project source code is stored:
project_dir = 'project'
usermedia_local = os.path.join(parent_dir, 'usermedia')
usermedia_production = os.path.join(webapps_root, 'christchurch_usermedia')

class Target(object):
    """
    Represents a place where the project is deployed to.

    """
    def __init__(self, django_app='', dbname=''):
        self.django_app = django_app
        self.dbname = dbname

        self.webapp_root = join(webapps_root, self.django_app)
        # src_root - the root of all sources on this target.
        self.src_root = join(self.webapp_root, 'src')
        self.current_version = SrcVersion('current', join(self.src_root, 'current'))

    def make_version(self, label):
        return SrcVersion(label, join(self.src_root, "src-%s" % label))

class SrcVersion(object):
    """
    Represents a version of the project sources on a Target
    """
    def __init__(self, label, src_dir):
        self.label = label
        # src_dir - the root of all sources for this version
        self.src_dir = src_dir
        # venv_dir - note that _update_virtualenv assumes this relative layout
        # of the 'env' dir and the 'project' dir.
        self.venv_dir = join(self.src_dir, 'env')
        # project_dir - where the CHRISTCHURCH project srcs are stored.
        self.project_dir = join(self.src_dir, project_dir)
        # static_dir - this is defined this way in settings.py
        self.static_dir = join(self.src_dir, 'static')

        self.additional_sys_paths = [project_dir]

STAGING = Target(
    django_app = "christchurch_django_staging",
    dbname = "cciw_christchurch_staging",
)

PRODUCTION = Target(
    django_app = "christchurch_django",
    dbname = "cciw_christchurch",
)

def _prepare_deploy():
    ensure_dependencies()
    # test that we can do forwards and backwards migrations?
    # check that there are no outstanding changes.

def backup_database(target, version):
    fname = "%s-%s.db" % (target.dbname, version.label)
    run("dump_pg_db.sh %s %s" % (target.dbname, fname))


def run_venv(command, **kwargs):
    run("source %s/bin/activate" % env.venv + " && " + command, **kwargs)


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use,
    """
    return settings(venv=venv_dir)


def _update_symlink(target, version):
    if files.exists(target.current_version.src_dir):
        run("rm %s" % target.current_version.src_dir) # assumes symlink
    run("ln -s %s %s" % (version.src_dir, target.current_version.src_dir))


def _update_virtualenv(version):
    # Update virtualenv in new dir.
    with cd(version.src_dir):
        # We should already have a virtualenv, but it will need paths updating
        run("virtualenv --python=python2.7 env")
        # Need this to stop ~/lib/ dirs getting in:
        run("touch env/lib/python2.7/sitecustomize.py")
        with virtualenv(version.venv_dir):
            with cd(version.project_dir):
                run_venv("pip install -r requirements.txt")

        # Need to add project to path.
        # Could do 'python setup.py develop' but not all projects support it
        pth_file = '\n'.join("../../../../" + n for n in version.additional_sys_paths)
        pth_name = "deps.pth"
        with open(pth_name, "w") as fd:
            fd.write(pth_file)
        put(pth_name, join(version.venv_dir, "lib/python2.7/site-packages"))
        os.unlink(pth_name)


def _stop_apache(target):
    run(join(target.webapp_root, "apache2/bin/stop"))


def _start_apache(target):
    run(join(target.webapp_root, "apache2/bin/start"))


def _restart_apache(target):
    with settings(warn_only=True):
        _stop_apache(target)
    _start_apache(target)

def _copy_local_sources(target, version):
    # Upload local sources. For speed, we:
    # - make a copy of the sources that are there already, if they exist.
    # - hg pull the new sources
    # This also copies the virtualenv which is contained in the same folder,
    # which saves a lot of time with installing.

    current_srcs = target.current_version.src_dir

    if files.exists(current_srcs):
        run("cp -a -L %s %s" % (current_srcs, version.src_dir))
    else:
        run("mkdir %s" % version.src_dir)

    with cd(version.project_dir):
        run("hg pull -u")

    # Also need to sync files that are not in main sources VCS repo.
    local("rsync christchurc/settings_priv.py cciw@christchurchbradford.org.uk:%s/christchurch/settings_priv.py")

def _build_static(version):
    # This always copies all files anyway, and we want to delete any unwanted
    # files, so we start from clean dir.
    run("rm -rf %s" % version.static_dir)

    with virtualenv(version.venv_dir):
        with cd(version.project_dir):
            run_venv("./manage.py collectstatic -v 0 --settings=christchurch.settings --noinput")

    run("chmod -R ugo+r %s" % version.static_dir)


def _is_south_installed(target):
    cmd = """psql -d %s -U %s -h localhost -c "select tablename from pg_catalog.pg_tables where tablename='south_migrationhistory';" """ % (target.dbname, target.dbname)
    out = run(cmd)
    if 'south_migrationhistory' not in out:
        return False

    cmd2 = """psql -d %s -U %s -h localhost -c "select migration from south_migrationhistory where migration='0001_initial';" """ % (target.dbname, target.dbname)
    out2 = run(cmd2)
    if '0001_initial' not in out2:
        return False

    return True


def _install_south(target, version):
    # A one time task to be run after South has been first added
    with virtualenv(version.venv_dir):
        with cd(version.project_dir):
            run_venv("./manage.py syncdb --settings=christchurch.settings")
            run_venv("./manage.py migrate --all 0001 --fake --settings=christchurch.settings")


def _update_db(target, version):
    with virtualenv(version.venv_dir):
        with cd(version.project_dir):
            run_venv("./manage.py syncdb --settings=christchurch.settings")
            run_venv("./manage.py migrate --all --settings=christchurch.settings")


def _deploy(target):
    _prepare_deploy()

    label = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    version = target.make_version(label)

    _copy_local_sources(target, version)
    _update_virtualenv(version)
    _build_static(version)

    # Ideally, we:
    # 1) stop web server
    # 2) updated db
    # 3) rollback if unsuccessful.
    # 4) restart webserver

    # In practice, for this low traffic site it is better to keep website
    # going for as much time as possible, and cope with any small bugs that
    # come from mismatch of db and code.

    db_backup_name = backup_database(target, version)
    _update_db(target, version)
    _stop_apache(target)
    _update_symlink(target, version)
    _start_apache(target)


def _clean(target):
    """
    Misc clean-up tasks
    """
    # Remove old src versions.
    with cd(target.src_root):
        with hide("stdout"):
            currentlink = run("readlink current").split('/')[-1]
            otherlinks = set([x.strip() for x in run("ls src-* -1d").split("\n")])
        otherlinks.remove(currentlink)
        otherlinks = list(otherlinks)
        otherlinks.sort()
        otherlinks.reverse()

        # Leave the most recent previous version, delete the rest
        for d in otherlinks[1:]:
            run("rm -rf %s" % d)


def deploy_staging(quick=False):
    _deploy(STAGING, quick=quick)


def deploy_production(quick=False):
    with lcd(this_dir):
        if local("hg st", capture=True).strip() != "":
            if not console.confirm("Project dir is not clean, merge to live will fail. Continue anyway?", default=False):
                sys.exit()

    _deploy(PRODUCTION, quick=quick)
    #  Update 'live' branch so that we can switch to it easily if needed.
    with lcd(this_dir):
        local('hg update -r live && hg merge -r default && hg commit -m "Merged from default" && hg update -r default', capture=False)

def stop_apache_production():
    _stop_apache(PRODUCTION)


def stop_apache_staging():
    _stop_apache(STAGING)


def start_apache_production():
    _start_apache(PRODUCTION)


def start_apache_staging():
    _start_apache(STAGING)


def restart_apache_production():
    _restart_apache(PRODUCTION)


def restart_apache_staging():
    _restart_apache(STAGING)


def clean_staging():
    _clean(STAGING)


def clean_production():
    _clean(PRODUCTION)


def test_staging():
    _test_remote(STAGING)


def test_production():
    _test_remote(PRODUCTION)


def upload_usermedia():
    local("rsync -z -r %s/ cciw@christchurchbradford.org.uk:%s" % (usermedia_local, usermedia_production), capture=False)


def backup_usermedia():
    local("rsync -z -r  cciw@christchurchbradford.org.uk:%s/ %s" % (usermedia_production, usermedia_local), capture=False)


# TODO:
#  - backup db task. This should be run only in production, and copies
#    files to Amazon S3 service.
