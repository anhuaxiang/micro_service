import coverage
import unittest
from flask_script import Manager
from project import create_app, db
from project.api.models import User


app = create_app()
manager = Manager(app)


COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*'
    ]
)
COV.start()


@manager.command
def recreate_db():
    """重新创建数据表."""
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def test():
    test = unittest.TestLoader().discover('project/tests', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(test)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def seed_db():
    """Seed the database"""
    db.session.add(User(username='admin', email='admin@admin.com'))
    db.session.add(User(username='test', email='test@test.com'))
    db.session.commit()


@manager.command
def cov():
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
