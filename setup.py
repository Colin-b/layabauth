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
        'pyaml==17.8.0',
    ],
    extras_require={
        'testing': [
        ],
    },
)
