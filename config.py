"""Flask config."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config."""

    FLASK_ENV = 'development'
    TESTING = True
    
    
class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    
    # HUE SECRETS
    PHILIPS_HUE_URL = os.environ.get('philips-url')