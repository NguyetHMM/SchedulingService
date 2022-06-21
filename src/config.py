import os

env = os.getenv('ENV', 'dev').lower()
if env in ['prod', 'production']:
    FLASK_ENV = 'prod'
elif env in ['dev', 'development']:
    FLASK_ENV = 'dev'
else:
    FLASK_ENV = env

class Config():
    APP_ROOTDIR = os.path.abspath(os.path.dirname(__file__))

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config_dict = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)