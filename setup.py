import os

from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    name="layabauth",
    version=open("layabauth/version.py").readlines()[-1].split()[-1].strip("\"'"),
    description="Authentication support for layab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    install_requires=[
        # Used to manage received requests
        "flask==1.1.1",
        # Used to manage authentication
        "oauth2helper==3.1.0",
    ],
    extras_require={
        "testing": [
            # Used to manage testing of a Flask application
            "pytest-flask==0.15.0",
            # Used to test decorator
            "flask-restplus==0.13.0",
            # Used to mock requests sent to check keys
            "pytest-responses==0.4.0",
        ],
    },
    python_requires=">=3.6",
    project_urls={
        "Changelog": "https://github.tools.digital.engie.com/gempy/layabauth/blob/master/CHANGELOG.md",
        "Issues": "https://github.tools.digital.engie.com/gempy/layabauth/issues",
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
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords=["flask"],
    platforms=["Windows", "Linux"],
)
