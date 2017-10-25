# geolocation-data-flaskapi
A small Flask based RESTful API for reporting ISO 3166-1 (countries) and ISO 3166-2 (country subdivisions). It also creates and updates city names in the related country and subdivisions.

This API is primarily a wrapper around [pycountry](https://pypi.python.org/pypi/pycountry) with a database to store and report on the city information.

Security is implemented using JSON Web Tokens and principle information stored in a database,