"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

import logging

from flask import request
from flask_jwt import jwt_required
from flask_restplus import Resource, abort
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from api.restplus import api
from api.geolocation_data_flaskapi.business.location_data import create_city, delete_city, update_city
from api.geolocation_data_flaskapi.serializers import country, subdivision, city
from database.model_exceptions import LengthError
from database.models import City
from pycountry import countries, subdivisions

log = logging.getLogger(__name__)

ns = api.namespace('country',
                   description='Operations related to locations')


@ns.route('/')
class CountryCollection(Resource):
    @api.marshal_list_with(country)
    def get(self):
        """
        Returns list of country records.
        :return:
        """

        return list(countries)


@ns.route('/<string:country_alpha2>')
@api.response(404, 'Country not found.')
class CountryItem(Resource):
    @api.marshal_with(country)
    def get(self, country_alpha2: str):
        """
        Returns a country record.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :return:
        """
        try:
            return countries.get(alpha_2=country_alpha2)
        except KeyError:
            abort(404, 'Country not found')


@ns.route('/<string:country_alpha2>/subdivision/')
class SubdivisionCollection(Resource):
    @api.marshal_list_with(subdivision)
    def get(self, country_alpha2: str):
        """
        Returns list of subdivision records for the country.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :return:
        """
        try:
            return list(subdivisions.get(country_code=country_alpha2))
        except KeyError:
            abort(404, 'Subdivisions not found')


@ns.route('/<string:country_alpha2>/subdivision/<string:subdivision_code>')
@api.response(404, 'Subdivision not found.')
class SubdivisionItem(Resource):
    @api.marshal_with(subdivision)
    def get(self, country_alpha2: str, subdivision_code: str):
        """
        Returns the specified subdivision record.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :return:
        """
        subdivivion_code = '{country_code}-{subdivision_code}'.format(country_code=country_alpha2, subdivision_code=subdivision_code)
        subdivision_record = subdivisions.get(code=subdivivion_code)

        if subdivision_record is not None:
            return subdivision_record
        else:
            abort(404, 'Subdivision not found')


@ns.route('/<string:country_alpha2>/subdivision/<string:subdivision_code>/city/')
class CityCollection(Resource):
    @api.marshal_list_with(city)
    def get(self, country_alpha2: str, subdivision_code: str):
        """
        Returns list of city records for the subdivision.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :return:
        """
        subdivision_code = '{country_code}-{subdivision_code}'.format(country_code=country_alpha2,
                                                                      subdivision_code=subdivision_code)
        city_records = City.query.filter(City.subdivision == subdivision_code).order_by(City.name).all()

        return city_records

    @api.response(201, 'City successfully created.')
    @api.expect(city)
    @api.marshal_with(city)
    @jwt_required()
    def post(self, country_alpha2: str, subdivision_code: str):
        """
        Creates a new city record.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :return:
        """
        data = request.json

        # Validate the country_alpha2 and subdivision_code are valid
        code = '{country_alpha2}-{subdivision_code}'.format(country_alpha2=country_alpha2,
                                                            subdivision_code=subdivision_code)

        try:
            if subdivisions.get(code=code) is None:
                abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')
        except KeyError:
            abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')

        try:
            data = create_city(data)
        except LengthError:
            abort(400, 'Bad request: City name length')
        except IntegrityError:
            abort(400, 'Bad request: City already exists')
        except Exception:
            abort(400, 'Bad request: City already exists')

        return data, 201


@ns.route('/<string:country_alpha2>/subdivision/<string:subdivision_code>/city/<int:city_id>')
@api.response(404, 'City not found.')
class CityItem(Resource):
    @api.marshal_with(city)
    def get(self, country_alpha2: str, subdivision_code: str, city_id: int):
        """
        Returns a city record.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :param city_id: The unique identifier of the city record.
        :type city_id: int
        :return:
        """
        # Validate the country_alpha2 and subdivision_code are valid
        code = '{country_alpha2}-{subdivision_code}'.format(country_alpha2=country_alpha2,
                                                            subdivision_code=subdivision_code)

        try:
            if subdivisions.get(code=code) is None:
                abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')
        except KeyError:
            abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')

        return City.query.filter(City.id == city_id).one()

    @api.expect(city)
    @api.response(204, 'City successfully updated.')
    @api.marshal_with(city)
    @jwt_required()
    def put(self, country_alpha2: str, subdivision_code: str, city_id: int):
        """
        Updates a city record.

        Use this method to change the values for a city record.

        * Send a JSON object with the new data in the request body.

        ```
        {
            "name": "Calgary",
            "subdivision": "CA-AB"
        }
        ```

        * Specify the ID of the city to modify in the request URL path.
        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :param city_id: The unique identifier of the city record.
        :type city_id: int
        """
        data = request.json

        # Validate the country_alpha2 and subdivision_code are valid
        code = '{country_alpha2}-{subdivision_code}'.format(country_alpha2=country_alpha2,
                                                            subdivision_code=subdivision_code)

        try:
            if subdivisions.get(code=code) is None:
                abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')
        except KeyError:
            abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')

        try:
            data = update_city(city_id, data)
        except LengthError:
            abort(400, 'Bad request: City name length error')
        return data, 204

    @api.response(204, 'City successfully deleted.')
    @jwt_required()
    def delete(self, country_alpha2: str, subdivision_code: str, city_id: int):
        """
        Deletes a city record.

        :param country_alpha2: The unique two character identifier of the country record.
        :type country_alpha2: str
        :param subdivision_code: The unique two character identifier of the subdivision record.
        :type subdivision_code: str
        :param city_id: The unique identifier of the city record.
        :type city_id: int
        """
        # Validate the country_alpha2 and subdivision_code are valid
        code = '{country_alpha2}-{subdivision_code}'.format(country_alpha2=country_alpha2,
                                                            subdivision_code=subdivision_code)

        try:
            if subdivisions.get(code=code) is None:
                abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')
        except KeyError:
            abort(400, 'Bad request: country_alpha2 and subdivision_code are invalid')

        delete_city(city_id)
        return None, 204
