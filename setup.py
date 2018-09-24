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
        'flask-restplus==0.11.0',
        # Used to parse configurations
        'PyYAML==3.13',
    ],
    extras_require={
        'testing': [
            # Used to provide testing help
            'pycommon-test==1.10.0',
            # Used to test Windows-Linux connection
            'pysmb==1.1.25',
            # Used to run tests
            'nose==1.3.7',
        ],
        'authentication': [
            'oauth2helper==1.1.1',
        ],
        # Used to connect to a Microsoft Windows computer
        'windows': [
            'pysmb==1.1.25',
        ],
    },
)
