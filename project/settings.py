
import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_name = os.environ.get('RESE_DB', 'travelcompensation')
db_uid = os.environ.get('RESE_UID', 'postgres')
db_pw = os.environ.get('RESE_PW', 'Julgran2005')
server_name = os.environ.get('RESE_SERVER', 'localhost')
host_ip = os.environ.get('RESE_HOST', '0.0.0.0')
port = os.environ.get('RESE_PORT', 5000)
api_version = 'v1'

postgres_local_base = "postgresql://{uid}:{pw}@{server}:5432/".format(server=server_name,
                                                                             uid=db_uid,
                                                                             pw=db_pw)



class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATION_ROOT = '/api/{}'.format(api_version)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_local_base + db_name


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = "{}{}_test".format(postgres_local_base, db_name)
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'