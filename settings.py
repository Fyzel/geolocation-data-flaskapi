# Flask settings
FLASK_SERVER_NAME = 'localhost:8888'
FLASK_SECRET_KEY = 'Set this to secret'
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_MODE = 'DEV'  # DEV, PRD

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings - change the SQLALCHEMY_DATABASE_URI to the appropriate values for your database
SQLALCHEMY_DATABASE_URI = 'mysql://geolocation-api:secret@192.168.129.195/Geolocation?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = False
