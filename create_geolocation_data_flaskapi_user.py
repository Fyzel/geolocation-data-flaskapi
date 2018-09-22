#!/usr/bin/python3

"""
create_geolocation_data_api_user -- create a geolocation data api user

create_geolocation_data_api_user is a command line utility to create a new user in the application's database.

It defines the methods to create a user with an encrypted and hashed password.

@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

import os
import sys
import uuid
from datetime import datetime
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from passlib.hash import sha512_crypt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, NVARCHAR, BOOLEAN, DATETIME, select

import config
from api.geolocation_data_flaskapi.business.security import salt_password

__all__ = []
__version__ = 1.0
__date__ = '2017-10-15'
__updated__ = '2017-10-15'
__short_description__ = 'create a geolocation data api user'
__longer_description__ = 'a command line utility to create a new user in the application''s database'
__org_name__ = 'Englesh.org'
__email__ = 'Fyzel@users.noreply.github.com'
__license__ = 'https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE'

DEBUG = False
TEST_RUN = False


class CLIError(Exception):
    """Generic exception to raise and log different fatal errors."""

    def __init__(self, message):
        super(CLIError).__init__(type(self))
        self.message = 'E: {message}'.format(message=message)

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message


def create_user(db_connection, user_table, username, hashed_password, salt, enable) -> None:
    """

    :param db_connection:
    :param user_table:
    :param username:
    :param hashed_password:
    :param salt:
    :param enable:
    :return None:
    """
    insert = user_table.insert().values(
        username=username,
        password=hashed_password,
        enabled=enable,
        salt=salt,
        created_date=datetime.utcnow(),
        last_login_date=None)

    db_connection.execute(insert)


def check_if_username_exists(db_connection, user_table, username) -> bool:
    """

    :param db_connection:
    :param user_table:
    :param username:
    :return:
    """
    query = select([user_table]).where(user_table.c.username == username)

    results = db_connection.execute(query)

    exists = results.rowcount > 0
    return exists


def main(argv=None):
    """Command line options."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = 'v{}'.format(__version__)
    program_build_date = str(__updated__)
    program_version_message = '%(prog)s {program_version} ({program_build_date})'.format(
        program_version=program_version,
        program_build_date=program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''{program_name}

  Created by {user_name} on {created_date}.
  Copyright 2017 {organization_name}. All rights reserved.

  Licensed under {license}
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
'''.format(program_name=program_shortdesc,
           user_name=__email__,
           created_date=str(__date__),
           organization_name=__org_name__,
           license=__license__)

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-u',
                            '--username',
                            dest='username',
                            required=True,
                            type=str,

                            help='the user''s username (1-64 characters)')
        parser.add_argument('-p',
                            '--password',
                            dest='password',
                            type=str,
                            required=True,
                            help='the user''s password (1-256 characters)')
        parser.add_argument('-e',
                            '--enable',
                            dest='enable',
                            default=False,
                            required=False,
                            action='store_true',
                            help='is the user enabled')

        # Process arguments
        args = parser.parse_args()

        username = args.username
        password = args.password
        salt = str(uuid.uuid4())
        enable = args.enable

        if len(username) < 1 or len(username) > 64:
            raise CLIError('username must be between 1 to 64 characters')

        if len(password) < 1 or len(password) > 256:
            raise CLIError('password must be between 1 to 256 characters')

        hashed_password = sha512_crypt.hash(salt_password(password, salt))

        engine = create_engine(config.DevelopmentConfig.SQLALCHEMY_DATABASE_URI, echo=True)

        metadata = MetaData()
        user = Table('user', metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('username', NVARCHAR(length=64), nullable=False),
                     Column('password', NVARCHAR(length=120), nullable=False),
                     Column('salt', NVARCHAR(length=64), nullable=False),
                     Column('enabled', BOOLEAN, nullable=False, default=True),
                     Column('created_date', DATETIME, nullable=False),
                     Column('last_login_date', DATETIME, nullable=True))

        conn = engine.connect()

        if not check_if_username_exists(conn, user, username):
            create_user(db_connection=conn,
                        user_table=user,
                        username=username,
                        hashed_password=hashed_password,
                        salt=salt,
                        enable=enable)

        conn.close()

        return 0
    except KeyboardInterrupt:
        # handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TEST_RUN:
            raise e
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        pass
    if TEST_RUN:
        import doctest

        doctest.testmod()
    sys.exit(main())
