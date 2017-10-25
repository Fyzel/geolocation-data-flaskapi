"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

import json
import logging
import random
import sys
import string
import unittest
from datetime import datetime


from pycountry import countries, subdivisions, Subdivision
import pytz
import requests


def get_random_datetime():
    """Return a random datetime from 0001-01-01 00:00:00.0 to 9999-12-28 23:59:59.999999"""
    year = random.randint(1, datetime.now().year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return datetime(year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                    tzinfo=pytz.UTC)


def get_random_string(length: int) -> str:
    """Generate a random string of length.

    :arg length: The length of the string
    :rtype str
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def is_country_code_valid(country_alpha2: str) -> bool:
    try:
        countries.get(alpha_2=country_alpha2)
        return True
    except KeyError:
        return False


def get_random_valid_country_code() -> str:
    """Get a valid country alpha-2 code"""
    return 'CA'


def get_random_invalid_country_code() -> str:
    """Get an invalid country alpha-2 code"""
    return 'ZZ'


def get_valid_subdivision_code() -> str:
    """Get a valid subdivision code"""
    subdivision = subdivisions.get(code='CA-AB')

    return subdivision.code[-2:]


def get_random_valid_subdivision_code(country_alpha2: str) -> str:
    """Get a valid subdivision code"""
    return get_valid_subdivision_code()


def get_random_valid_city_record_data(country_alpha2: str, subdivision_code: str):
    """Generate a random city data record"""

    assert len(country_alpha2) == 2, "country_alpha2 is not two characters in length"
    assert len(subdivision_code) == 2, "subdivision_code is not two characters in length"

    subdivision_alpha = '{country_alpha2}-{subdivision_code}'.format(country_alpha2=country_alpha2, 
                                                                     subdivision_code=subdivision_code)
    name = get_random_string(64)

    return {
        'subdivision': subdivision_alpha,
        'name': name
    }


def get_subdivision_resource(country_alpha2: str, subdivision_code=None) -> str:
    """Get the """
    if subdivision_code is None:
        return 'country/{country_alpha2}/subdivision'.format(country_alpha2=country_alpha2)
    else:
        return 'country/{country_alpha2}/subdivision/{subdivision_code}'.format(country_alpha2=country_alpha2,
                                                                                subdivision_code=subdivision_code)


def get_resource_by_id(country_alpha2=None, subdivision_code=None, city_code=None) -> str:
    if country_alpha2 is not None and subdivision_code is not None and city_code is not None:
        return 'country/{country_alpha2}/subdivision/{subdivision_code}/city/{city_code}'.format(
            country_alpha2=country_alpha2,
            subdivision_code=subdivision_code,
            city_code=city_code)
    elif country_alpha2 is not None and subdivision_code is not None and city_code is None:
        return 'country/{country_alpha2}/subdivision/{subdivision_code}'.format(
            country_alpha2=country_alpha2,
            subdivision_code=subdivision_code)
    else:
        return 'country/{country_alpha2}'.format(
            country_alpha2=country_alpha2)


def get_resource_without_id(country_alpha2=None, subdivision_code=None) -> str:
    if country_alpha2 is not None and subdivision_code is not None:
        return 'country/{country_alpha2}/subdivision/{subdivision_code}/city/'.format(
            country_alpha2=country_alpha2,
            subdivision_code=subdivision_code)
    elif country_alpha2 is not None and subdivision_code is None:
        return 'country/{country_alpha2}/subdivision/'.format(
            country_alpha2=country_alpha2)
    else:
        return 'country/'


class TestCaseLocation(unittest.TestCase):
    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def previous_record(self):
        return self._previous_record

    @previous_record.setter
    def previous_record(self, value):
        self._previous_record = value

    @property
    def last_id(self) -> int:
        return self._last_id

    @last_id.setter
    def last_id(self, value: int):
        self._last_id = value

    def setUp(self):
        """
        Configure these to target the environment being tested. Sample values provided.
        """
        self.base_url = 'http://localhost:8888'
        self.context = 'geolocation'
        self.username = 'admin'
        self.password = 'secret'
        self._token = None
        self._last_id = None

    def tearDown(self):
        pass

    def test_step_00_login_fail(self):
        """Test the login fail capability"""
        log = logging.getLogger('TestCase.test_step_00_login_fail')
        log.info('Start')

        auth_url = '{base_url}/auth'.format(
            base_url=self.base_url
        )

        payload = '{{"username": "{username_value}","password": "{password_value}"}}'.format(
            username_value=self.username[::-1],
            password_value=self.password[::-1]
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=auth_url))
        log.debug('username= {username}'.format(username=self.username[::-1]))  # reversed username
        log.debug('password= {password}'.format(password=self.password[::-1]))  # reversed password
        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', auth_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=401)
        )

        assert response.status_code == 401, 'Expected a HTTP status code 401'
        assert len(response.text) > 0, 'Expected data in the response'

        log.debug('response.text= {text}'.format(text=response.text))

        log.info('End')

    def test_step_01_login_success(self):
        """Test the login capability and setup for the next set of calls"""
        log = logging.getLogger('TestCase.test_step_01_login')
        log.info('Start')

        log.debug("base_url= %r", self.base_url)

        auth_url = '{base_url}/auth'.format(
            base_url=self.base_url
        )

        payload = '{{"username": "{username_value}","password": "{password_value}"}}'.format(
            username_value=self.username,
            password_value=self.password
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=auth_url))
        log.debug('username= {username}'.format(username=self.username[::-1]))
        log.debug('password= {password}'.format(password=self.password[::-1]))
        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', auth_url, data=payload, headers=headers)

        assert response.status_code == 200, 'Expected a HTTP status code 200'
        assert len(response.text) > 0, 'Expected data in the response'

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        log.debug('response.text= {text}'.format(text=response.text))

        json_data = json.loads(response.text)

        assert json_data['access_token'] is not None, 'Access token is not returned'

        TestCaseLocation.token = json_data['access_token']

        log.debug('JWT token= {token}'.format(token=self.token))

        log.info('End')

    def test_step_02_get_country_list_without_auth(self):
        """Get country list without JWT token."""
        log = logging.getLogger('TestCase.test_step_02_get_country_without_auth')
        log.info('Start')

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id()
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_03_get_country_list_with_auth(self):
        """Get country list with JWT token."""
        log = logging.getLogger('TestCase.test_step_03_get_country_with_auth')
        log.info('Start')

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id()
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_04_get_valid_country_without_auth(self):
        """Get a valid country record without JWT token."""
        log = logging.getLogger('TestCase.test_step_04_get_valid_country_without_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_05_get_valid_country_with_auth(self):
        """Get a valid country record with a JWT token."""
        log = logging.getLogger('TestCase.test_step_05_get_valid_country_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_06_get_invalid_country_without_auth(self):
        """Get an invalid country record without JWT token."""
        log = logging.getLogger('TestCase.test_step_06_get_invalid_country_without_auth')
        log.info('Start')

        country_alpha2 = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_07_get_invalid_country_with_auth(self):
        """Get an invalid country record with a JWT token."""
        log = logging.getLogger('TestCase.test_step_07_get_invalid_country_with_auth')
        log.info('Start')

        country_alpha2 = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_08_get_invalid_country_with_auth(self):
        """Get country list with JWT token."""
        log = logging.getLogger('TestCase.test_step_08_get_invalid_country_with_auth')
        log.info('Start')

        country_alpha2 = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_09_get_subdivision_list_without_auth(self):
        """Get subdivision list without JWT token."""
        log = logging.getLogger('TestCase.test_step_09_get_subdivision_list_without_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_10_get_subdivision_list_with_auth(self):
        """Get subdivision list with JWT token."""
        log = logging.getLogger('TestCase.test_step_10_get_subdivision_list_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_11_get_valid_country_valid_subdivision_without_auth(self):
        """Get a valid subdivision record without JWT token."""
        log = logging.getLogger('TestCase.test_step_11_get_valid_country_valid_subdivision_without_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = get_random_valid_subdivision_code(country_alpha2)

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_12_get_valid_country_valid_subdivision_with_auth(self):
        """Get a valid subdivision record with a JWT token."""
        log = logging.getLogger('TestCase.test_step_12_get_valid_country_valid_subdivision_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = get_random_valid_subdivision_code(country_alpha2)

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_13_get_valid_country_invalid_subdivision_without_auth(self):
        """Get an invalid subdivision record without JWT token."""
        log = logging.getLogger('TestCase.test_step_13_get_valid_country_invalid_subdivision_without_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_14_get_valid_country_invalid_subdivision_with_auth(self):
        """Get an invalid subdivision record with a JWT token."""
        log = logging.getLogger('TestCase.test_step_14_get_valid_country_invalid_subdivision_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_15_get_invalid_country_invalid_subdivision_without_auth(self):
        """Get an invalid country and subdivision record without JWT token."""
        log = logging.getLogger('TestCase.test_step_15_get_invalid_country_invalid_subdivision_without_auth')
        log.info('Start')

        country_alpha2 = get_random_invalid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_16_get_invalid_country_invalid_subdivision_with_auth(self):
        """Get an invalid country and subdivision record with a JWT token."""
        log = logging.getLogger('TestCase.test_step_16_get_invalid_country_invalid_subdivision_with_auth')
        log.info('Start')

        country_alpha2 = get_random_invalid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'

        log.info('End')

    def test_step_17_valid_country_valid_subdivision_create_city_record_without_auth(self):
        """Create a humidity record without JWT token."""
        log = logging.getLogger('TestCase.test_step_17_valid_country_valid_subdivision_create_city_record_without_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = get_random_valid_subdivision_code(country_alpha2)

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        record_data = get_random_valid_city_record_data(country_alpha2=country_alpha2, subdivision_code=subdivision_code)

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name=record_data['name'],
                              subdivision=record_data['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=401)
        )

        assert response.status_code == 401, 'Expected a HTTP status code 401'
        assert len(response.text) > 0, 'Expected data in the response'

        log.info('End')

    def test_step_18_valid_country_valid_subdivision_create_city_record_with_auth(self):
        """Create a city record with JWT token."""
        log = logging.getLogger('TestCase.test_step_18_valid_country_valid_subdivision_create_city_record_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = get_random_valid_subdivision_code(country_alpha2)

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        record_data = get_random_valid_city_record_data(country_alpha2=country_alpha2,
                                                        subdivision_code=subdivision_code)

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name=record_data['name'],
                              subdivision=record_data['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=201)
        )

        assert response.status_code == 201, 'Expected a HTTP status code 201'
        assert len(response.text) > 0, 'Expected data in the response'

        json_data = json.loads(response.text)

        assert int(json_data['id']) > 0, "Returned id is greater than 0"

        self.assertEqual(
            json_data['name'],
            record_data['name']), 'Returned name is the same'

        self.assertEqual(
            json_data['subdivision'],
            record_data['subdivision']), 'Returned subdivision is the same'

        TestCaseLocation.last_id = json_data['id']
        TestCaseLocation.previous_record = json_data

        log.info('End')

    def test_step_19_valid_country_valid_subdivision_create_duplicate_city_record_with_auth(self):
        """Create a duplicate city record with JWT token."""
        log = logging.getLogger('TestCase.test_step_19_valid_country_valid_subdivision_create_duplicate_city_record_with_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]
        city_name = TestCaseLocation.previous_record['name']

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name=city_name,
                              subdivision=TestCaseLocation.previous_record['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=400)
        )

        assert response.status_code == 400, 'Expected a HTTP status code 400'
        assert len(response.text) > 0, 'Expected data in the response'

        log.info('End')

    def test_step_20_valid_country_invalid_subdivision_create_city_record_with_auth(self):
        """Create a city record with valid country, invalid subdivision, and with JWT token."""
        log = logging.getLogger('TestCase.test_step_20_valid_country_invalid_subdivision_create_city_record_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        record_data = get_random_valid_city_record_data(country_alpha2=country_alpha2,
                                                        subdivision_code=subdivision_code)

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name=record_data['name'],
                              subdivision=record_data['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=400)
        )

        assert response.status_code == 400, 'Expected a HTTP status code 400'
        assert len(response.text) > 0, 'Expected data in the response'

        log.info('End')

    def test_step_21_invalid_country_invalid_subdivision_create_city_record_with_auth(self):
        """Create a city record with invalid country, invalid subdivision, and with JWT token."""
        log = logging.getLogger('TestCase.test_step_21_invalid_country_invalid_subdivision_create_city_record_with_auth')
        log.info('Start')

        country_alpha2 = get_random_invalid_country_code()
        subdivision_code = 'ZZ'

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        record_data = get_random_valid_city_record_data(country_alpha2=country_alpha2,
                                                        subdivision_code=subdivision_code)

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name=record_data['name'],
                              subdivision=record_data['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=400)
        )

        assert response.status_code == 400, 'Expected a HTTP status code 400'
        assert len(response.text) > 0, 'Expected data in the response'

        log.info('End')

    def test_step_22_valid_country_valid_subdivision_create_invalid_city_record_with_auth(self):
        """Create a city record with JWT token."""
        log = logging.getLogger(
            'TestCase.test_step_22_valid_country_valid_subdivision_create_invalid_city_record_with_auth')
        log.info('Start')

        country_alpha2 = get_random_valid_country_code()
        subdivision_code = get_random_valid_subdivision_code(country_alpha2)

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_without_id(country_alpha2=country_alpha2, subdivision_code=subdivision_code)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('auth_url= {url}'.format(url=app_url))

        record_data = get_random_valid_city_record_data(country_alpha2=country_alpha2,
                                                        subdivision_code=subdivision_code)

        payload = '{{\n' \
                  '"name": "{name}",\n' \
                  '"subdivision": "{subdivision}"\n' \
                  '}}'.format(name='',
                              subdivision=record_data['subdivision'])

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'content-type': 'application/json',
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('POST', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=400)
        )

        assert response.status_code == 400, 'Expected a HTTP status code 400'
        assert len(response.text) > 0, 'Expected data in the response'

        log.info('End')

    def test_step_23_get_city_record_without_auth(self):
        """Get a city record without JWT token."""
        log = logging.getLogger('TestCase.test_step_23_get_city_record_without_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2,
                                        subdivision_code=subdivision_code,
                                        city_code=TestCaseLocation.last_id)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('app_url= {url}'.format(url=app_url))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        log.info('End')

    def test_step_24_get_city_record_with_auth(self):
        """Get a city record with JWT token."""
        log = logging.getLogger('TestCase.test_step_24_get_city_record_with_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2,
                                        subdivision_code=subdivision_code,
                                        city_code=TestCaseLocation.last_id)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('app_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=200)
        )

        assert response.status_code == 200, 'Expected a HTTP status code 200'

        json_data = json.loads(response.text)

        self.assertEqual(
            int(json_data['id']),
            int(TestCaseLocation.last_id)), "Returned id is the same"

        self.assertEqual(
            json_data['subdivision'],
            TestCaseLocation.previous_record['subdivision']), 'Returned subdivision is the same'

        self.assertEqual(
            json_data['name'],
            TestCaseLocation.previous_record['name']), 'Returned name is the same'

        log.info('End')

    def test_step_25_delete_city_record_without_auth(self):
        """Delete a city record without JWT token."""
        log = logging.getLogger('TestCase.test_step_25_delete_city_record_without_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2,
                                        subdivision_code=subdivision_code,
                                        city_code=TestCaseLocation.last_id)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('app_url= {url}'.format(url=app_url))

        payload = ''

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'cache-control': 'no-cache'
        }

        response = requests.request('DELETE', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=401)
        )

        assert response.status_code == 401, 'Expected a HTTP status code 401'

        log.info('End')

    def test_step_26_delete_record_with_auth(self):
        """Delete a city record with JWT token."""
        log = logging.getLogger('TestCase.test_step_26_delete_record_with_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2,
                                        subdivision_code=subdivision_code,
                                        city_code=TestCaseLocation.last_id)
        )

        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('app_url= {url}'.format(url=app_url))

        payload = ''

        log.debug('payload= {payload}'.format(payload=payload))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('DELETE', app_url, data=payload, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=204)
        )

        assert response.status_code == 204, 'Expected a HTTP status code 204'
        self.assertEqual(len(response.text), 0), 'Expected data in the response'

        log.info('End')

    def test_step_27_get_deleted_record_with_auth(self):
        """Get a deleted city record with JWT token."""
        log = logging.getLogger('TestCase.test_step_27_get_deleted_record_with_auth')
        log.info('Start')

        country_alpha2 = TestCaseLocation.previous_record['subdivision'][:2]
        subdivision_code = TestCaseLocation.previous_record['subdivision'][-2:]

        app_url = '{base_url}/{context}/{resource}'.format(
            base_url=self.base_url,
            context=self.context,
            resource=get_resource_by_id(country_alpha2=country_alpha2,
                                        subdivision_code=subdivision_code,
                                        city_code=TestCaseLocation.last_id)
        )
        log.debug('base_url= {url}'.format(url=self.base_url))
        log.debug('app_url= {url}'.format(url=app_url))

        headers = {
            'authorization': 'JWT {token}'.format(token=TestCaseLocation.token),
            'cache-control': 'no-cache'
        }

        response = requests.request('GET', app_url, headers=headers)

        log.debug('Got {response_code} - expected {expected_code}'.format(
            response_code=response.status_code,
            expected_code=404)
        )

        assert response.status_code == 404, 'Expected a HTTP status code 404'
        log.info('End')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger('TestCase.test_step_00_login_fail').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_01_login').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_02_get_country_list_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_03_get_country_list_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_04_get_valid_country_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_05_get_valid_country_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_06_get_invalid_country_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_07_get_invalid_country_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_08_get_invalid_country_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_09_get_subdivision_list_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_10_get_subdivision_list_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_11_get_valid_country_valid_subdivision_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_12_get_valid_country_valid_subdivision_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_13_get_valid_country_invalid_subdivision_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_14_get_valid_country_invalid_subdivision_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_15_get_invalid_country_invalid_subdivision_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_16_get_invalid_country_invalid_subdivision_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_17_valid_country_valid_subdivision_create_city_record_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_18_valid_country_valid_subdivision_create_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_19_valid_country_valid_subdivision_create_duplicate_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_20_valid_country_invalid_subdivision_create_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_21_invalid_country_invalid_subdivision_create_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_22_valid_country_valid_subdivision_create_invalid_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_23_get_city_record_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_24_get_city_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_25_delete_city_record_without_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_26_delete_record_with_auth').setLevel(logging.DEBUG)
    logging.getLogger('TestCase.test_step_27_get_deleted_record_with_auth').setLevel(logging.DEBUG)
    unittest.main()
