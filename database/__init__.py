"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_city_indexes(app):
    with app.app_context():
        from sqlalchemy import text
        from sqlalchemy.exc import OperationalError

        # Create city table indices
        try:
            sql = text('CREATE UNIQUE INDEX city_name_subdivision_index ON city (subdivision, name);')
            db.engine.execute(sql)
        except OperationalError as oe:
            pass

        try:
            sql = text('CREATE UNIQUE INDEX city_id_uindex ON city (id);')
            db.engine.execute(sql)
        except OperationalError as oe:
            pass

        try:
            sql = text('CREATE INDEX city_name_index ON city (name);')
            db.engine.execute(sql)
        except OperationalError as oe:
            pass


def create_user_indexes(app):
    with app.app_context():
        from sqlalchemy import text
        from sqlalchemy.exc import OperationalError

        # Create user table indices
        try:
            sql = text('CREATE INDEX user_username_index ON user (username);')
            db.engine.execute(sql)
        except OperationalError as oe:
            pass


def create_indexes(app):
    create_city_indexes(app)
    create_user_indexes(app)


def create_database(app=None):
    db.create_all(app=app)
    create_indexes(app)


def reset_database():
    from database.models import City, User
    db.drop_all()
    db.create_all()
