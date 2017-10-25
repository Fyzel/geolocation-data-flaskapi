"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/path/to/geolocation-data-api')

if sys.version_info[0] < 3:  # require python3
    raise Exception("Python3 required! Current (wrong) version: '%s'" % sys.version_info)

from app import app as application
