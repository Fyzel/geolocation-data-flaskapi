"""
@author:     Fyzel@users.noreply.github.com

@copyright:  2017 Englesh.org. All rights reserved.

@license:    https://github.com/Fyzel/geolocation-data-flaskapi/blob/master/LICENSE

@contact:    Fyzel@users.noreply.github.com
@deffield    updated: 2017-10-15
"""


class ForeignKeyError(ValueError):
    """
    Raised when the foreign key value is invalid.
    """
    pass


class LengthError(ValueError):
    def __int__(self, message=''):
        super().__init__()
        self._message = message

    @property
    def message(self):
        return self._message
