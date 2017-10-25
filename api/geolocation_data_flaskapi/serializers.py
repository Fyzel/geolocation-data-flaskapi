"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

from flask_restplus import fields

from api.restplus import api


country = api.model(
    'Country',
    {
        'alpha_2': fields.String(
            required=True,
            readOnly=True,
            max=2,
            description='The unique two character identifier of the record'),
        'alpha_3': fields.String(
            required=True,
            readOnly=True,
            max=3,
            description='The unique three character identifier of the record'),
        'name': fields.String(
            required=True,
            readOnly=True,
            description='The country''s name'),
        'numeric': fields.String(
            required=True,
            readOnly=True,
            description='The country''s unique numeric code'),
        'official_name': fields.String(
            required=False,
            readOnly=True,
            description='The country''s official name'),
    })

subdivision = api.model(
    'Subdivision',
    {
        'code': fields.String(
            required=True,
            readOnly=True,
            description='The unique identifier of the record'),
        'country_code': fields.String(
            required=True,
            readOnly=True,
            max=2,
            description='The unique two character identifier of the country record'),
        'name': fields.String(
            required=True,
            readOnly=True,
            description='The country''s name'),
        'parent_code': fields.String(
            required=False,
            readOnly=True,
            description='The subdivision''s parent unique idenitifer'),
        'type': fields.String(
            required=False,
            readOnly=True,
            description='The subdivion''s type'),
    })

city = api.model(
    'City',
    {
        'id': fields.Integer(
            readOnly=True,
            description='The unique identifier of the record'),
        'name': fields.String(
            required=True,
            readOnly=True,
            max=64,
            description='The subdivision''s name'),
        'subdivision': fields.String(
            required=True,
            readOnly=True,
            max=6,
            description='The unique identifier of the subdivision record'),
    })
