"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

from datetime import datetime

from database import db
from database.model_exceptions import LengthError


class City(db.Model):
    """
    A class that represents the ORM for a city.
    """
    __tablename__ = 'city'
    id = db.Column(db.BIGINT(), primary_key=True, autoincrement=True)
    subdivision = db.Column(db.NVARCHAR(6), nullable=False)
    name = db.Column(db.NVARCHAR(64), nullable=False)

    def __init__(self,
                 subdivision: str,
                 name: str,
                 id=None):
        """
        City constructor.

        name must not be zero length

        :rtype: City
        :param name: The city name.
        :type name: str
        :param subdivision: The subdivision code (e.g. CA-AB).
        :type subdivision: str
        :param id: The unique id for the city.
        :type id: int, None
        """
        super().__init__()

        # Test case for name length
        if len(name) == 0:
            raise LengthError('City name length is 0')

        if id is not None:
            self.id = id

        self.name = name
        self.subdivision = subdivision

    def __repr__(self):
        """
        Return a string representation of the City object.

        :return: A string representation of the City object.
        """
        if self.id is None:
            return '<City: subdivision: {subdivision}\n' + \
                   '       name: {name}>'.format(
                       subdivision=str(self.subdivision),
                       name=self.name
                   )
        else:
            return '<City: id: {id)}\n' + \
                   '       subdivision: {subdivision}\n' + \
                   '       name: {name}>'.format(
                       id=str(self.id),
                       subdivision=str(self.subdivision),
                       name=self.name
                   )

    def __str__(self):
        return self.__repr__()


class User(db.Model):
    """
    A class that represents the ORM for a user account.
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    username = db.Column(db.NVARCHAR(64), nullable=False)
    password = db.Column(db.NVARCHAR(120), nullable=False)
    salt = db.Column(db.NVARCHAR(64), nullable=False)
    enabled = db.Column(db.BOOLEAN, nullable=False)
    created_date = db.Column(db.DATETIME, nullable=False, default=datetime.utcnow())
    last_login_date = db.Column(db.DATETIME, nullable=True)

    def __init__(self,
                 username: str,
                 password: str,
                 salt: str,
                 enabled: bool,
                 created_date: datetime = None,
                 last_login_date: datetime = None,
                 id=None):
        """
        User constructor.

        :param username: The user's username.
        :type username: str
        :param password: The user's SHA256 encrypted password.
        :type password: str
        :param salt: The user's salt.
        :type salt: str
        :param enabled: Boolean indicating if the user is enabled for login.
        :type enabled: bool
        :param created_date: The date and time the user's account was created.
        :type created_date: datetime
        :param last_login_date: The date and time the user last logged in.
        :type last_login_date: datetime
        :param id: The database id for the user.
        :type id: int
        """
        super().__init__()

        if id is not None:
            self.id = id
        self.username = username
        self.password = password
        self.salt = salt
        self.enabled = enabled
        self.created_date = created_date
        self.last_login_date = last_login_date

    def __repr__(self) -> str:
        """
        Return a string representation of the User object.

        :return: A string representation of the User object.
        """
        result = '<User: id: {id} username: {username}>'.format(
            id=str(self.id),
            username=self.username
        )
        return result

    def __str__(self):
        result = self.__repr__()
        return result
