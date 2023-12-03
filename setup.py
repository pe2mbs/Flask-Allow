from setuptools import setup, find_packages

setup(
    name            = 'Flask-Allow',
    version         = '2.0.0',
    description     = 'Setting up a python package',
    author          = 'Marc Bertens-Nguyen',
    author_email    = 'm.bertens@pe2mbs.nl',
    url             = 'https://github.com/pe2mbs/flask-allow',
    license         = 'GPL 2.0-only',
    packages        = find_packages( include=[ 'flask_allow', 'flask_allow.*' ] ),
    install_requires = [
        'flask==2.3.3',
        'mako==1.3.0',
    ],
    setup_requires = [ 'pytest-runner',
                       'flake8' ],
    tests_require=[ 'pytest' ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent"
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: Implementation :: CPython"
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers"
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: System :: Logging",
        "Intended Audience :: Developers",
    ],
)