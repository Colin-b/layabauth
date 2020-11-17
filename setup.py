import os

from setuptools import setup, find_packages

this_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    name="layabauth",
    version=open("layabauth/version.py").readlines()[-1].split()[-1].strip("\"'"),
    author="Colin Bounouar",
    author_email="colin.bounouar.dev@gmail.com",
    maintainer="Colin Bounouar",
    maintainer_email="colin.bounouar.dev@gmail.com",
    url="https://colin-b.github.io/layabauth/",
    description="Handle OAuth2 authentication for REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://pypi.org/project/layabauth/",
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
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords=["flask", "starlette", "auth"],
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # Used to request JWKs (keys)
        "httpx==0.16.*",
        # Used to manage authentication
        "python-jose==3.*",
    ],
    extras_require={
        "testing": [
            # Used to test flask application
            "flask_restx==0.2.*",
            "pytest-flask==1.*",
            # Used to test starlette authentication
            "starlette==0.13.*",
            "requests==2.*",
            # Used to mock requests sent to check keys
            "pytest-httpx==0.10.*",
            # Used to check coverage
            "pytest-cov==2.*",
        ]
    },
    python_requires=">=3.6",
    project_urls={
        "GitHub": "https://github.com/Colin-b/layabauth",
        "Changelog": "https://github.com/Colin-b/layabauth/blob/master/CHANGELOG.md",
        "Issues": "https://github.com/Colin-b/layabauth/issues",
    },
    platforms=["Windows", "Linux"],
)
