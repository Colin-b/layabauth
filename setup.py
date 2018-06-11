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
        'flask-restplus==0.10.1',
        # Used to parse configurations
        'pyaml==17.12.1',
    ],
    extras_require={
        'testing': [
            'pycommon-test==1.9.0',
            'pysmb==1.1.23',
        ],
        'authentication': [
            'oauth2helper==1.1.0',
        ],
        # Used to connect to a Microsoft Windows computer
        'windows': [
            'pysmb==1.1.23',
        ],
    },
)
