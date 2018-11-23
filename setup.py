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
    ],
    extras_require={
        'testing': [
            # Used to provide testing help
            'pycommon-test==2.1.0',
            # Used to test authentication handling
            'oauth2helper==1.3.0',
            # Used to test Windows-Linux connection
            'pysmb==1.1.25',
        ],
        'authentication': [
            'oauth2helper==1.3.0',
        ],
        # Used to connect to a Microsoft Windows computer
        'windows': [
            'pysmb==1.1.25',
        ],
        # Async task execution using celery
        'celery': [
            # redis freeze. Beware, as other newer version are very buggy
            'redis==2.10.6',
            # Used to process requests asynchronously
            'celery[redis]==4.2.1',
        ],
    },
)
