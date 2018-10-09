import unittest
import coverage

from flask import url_for
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from project.api.models import User


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/settings.py',
        'project/api/*/__init__.py'
    ]
)
COV.start()

from project import app, db, settings, skanetrafiken # noqa

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


def add_admin_account():
    admin = User(**{
        'email': settings.admin_email,
        'password': settings.admin_password,
        'name': 'Admin',
        'admin': True,
        'agreed_terms': True,
    })
    db.session.add(admin)
    db.session.commit()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()
    add_admin_account()


@manager.command
def add_test_data():
    pass

@manager.command
def drop_db():
    """Drops the db tables."""
    db.engine.execute("drop schema if exists public cascade")
    db.engine.execute("create schema public")

@manager.command
def setup_skanetrafiken():
    skanetrafiken.add_stations()


@manager.command
def reset():
    drop_db()
    create_db()

server = Server(host=settings.host_ip)
manager.add_command("runserver", server)

if __name__ == '__main__':
    manager.run()