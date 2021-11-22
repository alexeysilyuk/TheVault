import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
class ProductionConfig(Config):
    DEBUG = False
class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
