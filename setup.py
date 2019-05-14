from setuptools import setup, find_packages

extra_requirements = {
    "testing": [
        # Used to provide testing help
        "pycommon_test==7.0.0"
    ],
    # Used to manage authentication
    "authentication": ["oauth2helper==1.6.0"],
    # Used to connect to another REST API
    "rest": ["requests==2.21.0"],
    # Pandas
    "pandas": ["pandas==0.24.2"],
}


# Add all extra requirements to testing
extra_requirements["testing"] += [
    extra
    for extra_name, extra_list in extra_requirements.items()
    if extra_name != "testing"
    for extra in extra_list
]


from pycommon_server.version import __version__

setup(
    name="pycommon_server",
    version=__version__,
    packages=find_packages(exclude=["test"]),
    install_requires=[
        # Used to manage endpoints and swagger
        "flask-restplus==0.12.1",
        # Used to parse configurations
        "PyYAML==5.1",
        # Cross Origin handling
        "flask_cors==3.0.7",
        # Used to gz compress http output
        "flask_compress==1.4.0",
        # Used to ensure Black code style is checked on pre-commit
        "pre-commit==1.16.1",
    ],
    extras_require=extra_requirements,
)
