"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

from database import db
from database.models import City

from database.model_exceptions import LengthError


def create_city(data) -> City:
    """
    Creates a new city record in the database.

    :param data: JSON data for a new city object.
    :return: City
    """
    name = data.get('name')
    subdivision = data.get('subdivision')

    if len(name) < 1:
        raise LengthError('City name must be one or more characters in length')

    city = City(name=name,
                subdivision=subdivision)

    db.session.add(city)
    db.session.commit()

    return city


def update_city(city_id: int, data) -> City:
    """
    Update a city record in the database.

    :param city_id: The city record identifier.
    :type city_id: int
    :param data: Updated JSON data for an existing City object.
    :return: City
    """
    city = City.query.filter(City.id == city_id).one()
    city.name = data.get('name')
    city.subdivision = data.get('subdivision')

    if len(city.name) < 1:
        raise LengthError('City name must be one or more characters in length')

    db.session.add(city)
    db.session.commit()

    return city


def delete_city(city_id: int):
    """
    Delete a city record in the database.

    :param city_id: The city record identifier.
    :type city_id: int
    :return: None
    """
    city = City.query.filter(City.id == city_id).one()
    db.session.delete(city)
    db.session.commit()
