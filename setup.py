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
        'PyYAML==3.13'
    ],
    extras_require={
        'testing': [
            'pycommon-test==1.9.1',
            'pysmb==1.1.25',
            'nose'
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
