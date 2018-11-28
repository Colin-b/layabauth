from setuptools import setup, find_packages

from pycommon_server._version import __version__

setup(
    name='pycommon_server',
    version=__version__,
    packages=find_packages(exclude=[
        'test',
    ]),
    install_requires=[
        # Used to manage endpoints and swagger
        'flask-restplus==0.12.1',
        # Used to parse configurations
        'PyYAML==3.13',
        # Cross Origin handling
        'flask_cors==3.0.7',
        # Used to gz compress http output
        'flask_compress==1.4.0',
    ],
    extras_require={
        'testing': [
            # Used to provide testing help
            'pycommon-test==3.0.2',
            # Used to test authentication handling
            'oauth2helper==1.3.0',
            # Used to test Windows-Linux connection
            'pysmb==1.1.25',
            # Used to test REST API connection
            'requests==2.20.1',
        ],
        # Used to manage authentication
        'authentication': [
            'oauth2helper==1.3.0',
        ],
        # Used to connect to a Microsoft Windows computer
        'windows': [
            'pysmb==1.1.25',
        ],
        # Async task execution using celery
        'celery': [
            'celery==4.2.1',
        ],
        # Used to connect to another REST API
        'rest': [
            'requests==2.20.1',
        ],
    },
)
