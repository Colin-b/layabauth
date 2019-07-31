import os

from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    name="pycommon_server",
    version=open("pycommon_server/version.py").readlines()[-1].split()[-1].strip("\"'"),
    description="Provide helper for REST API related stuff.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    install_requires=[
        # Used to manage endpoints and swagger
        "flask-restplus==0.12.1",
        # Used to parse configurations
        "PyYAML==5.1.1",
        # Cross Origin handling
        "flask_cors==3.0.8",
        # Used to gz compress http output
        "flask_compress==1.4.0",
        # Used to ensure Black code style is checked on pre-commit
        "pre-commit==1.17.0",
    ],
    extras_require={
        "testing": [
            # Used to manage testing of a Flask application
            "pytest-flask==0.15.0",
            # Optional dependencies
            "oauth2helper==2.0.0",
            "pandas==0.25.0",
        ],
        # Used to manage authentication
        "authentication": ["oauth2helper==2.0.0"],
        # Pandas
        "pandas": ["pandas==0.25.0"],
    },
    python_requires=">=3.6",
    project_urls={
        "Changelog": "https://github.tools.digital.engie.com/GEM-Py/pycommon_server/blob/development/CHANGELOG.md",
        "Issues": "https://github.tools.digital.engie.com/GEM-Py/pycommon_server/issues",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords=["flask"],
    platforms=["Windows", "Linux"],
)
