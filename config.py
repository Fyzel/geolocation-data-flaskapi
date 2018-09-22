"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'mysql://geolocation-api:mypass@localhost/Geolocation?charset=utf8'
    SECRET_KEY = 'Change me'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RESTplus settings
    RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
