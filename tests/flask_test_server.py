#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    This is a simple Flask web server with flask_allow for testing purposes.
    This is being called from the pytest script test_flask_allow.py

"""
import flask
import traceback
import logging
import click
from flask_allow import FlaskAllow


def flask_test_server( verbose = False ):
    # Force logging of the webserver off
    if not verbose:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        log.disabled = True

    try:
        app = flask.Flask( __name__ )
        # Force logging of the webserver off
        if not verbose:
            app.logger.disabled = True

        app.config[ 'TESTING' ]     = True
        app.config[ 'ACCESS_LOG' ]  = "access.log"
        app.config[ 'ADDRESS_RESTRICTION' ] = [
            {
                "ALLOW":    "127.0.0.1",             # Allow localhost
                "DENY":     "0.0.0.0/0"              # Deny the rest
            }
        ]
        # Force logging click off
        def secho(text, file=None, nl=None, err=None, color=None, **styles):
            pass

        def echo(text, file=None, nl=None, err=None, color=None, **styles):
            pass

        if not verbose:
            click.echo = echo
            click.secho = secho

        FlaskAllow( app )

        @app.route('/')
        def index():
            return "Hello world", 200

        app.run( '0.0.0.0', 5000 )

    except Exception:
        print( traceback.format_exc() )

    return


if __name__ == '__main__':
    flask_test_server( verbose = True )
