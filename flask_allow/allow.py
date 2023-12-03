#   Flask-Allow allows white/black listing of ip addresses/networks.
#   Copyright (C) 2023 Marc Bertens-Nguyen
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; only version 2
#   of the License (GPL-2.0-only).
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from typing import Union
import os
import ipaddress
import socket
import logging
import logging.handlers
from mako.template import Template
from flask import Flask, request, abort
from flask_allow.exceptions import InvalidAccessLog


__version__ = '2.0.0'
__author__  = 'Marc Bertens-Nguyen'
__licence__ = 'GPL-2.0-only'


class FlaskAllow( object ):
    """ This class is intended as extention to Flask to restrict the IP addresses
    comming into the web application and access log file

        app = Flask()
        restrict = FlaskAllow()
        restrict.init_app( app )

    or
        app = Flask()
        restrict = FlaskAllow( app )

    Configuration
    The ADDRESS_RESTRICTION is a list if dictionaries, "ALLOW", "DENY" or both are allowed,
    the ALLOW is is checked first.

        app.config[ "ADDRESS_RESTRICTION" ] = [
            {
                "ALLOW":    "192.168.1.0/24",       # Allow subnet 192.168.1.*
            },
            {
                "ALLOW":    "127.0.0.1"             # Allow localhost
                "DENY": "0.0.0.0/0",            # Allow subnet 192.168.1.*
            },
        ]

    or in YAML format
        ADDRESS_RESTRICTION:
        -   ALLOW:  192.168.1.0/24
        -   ALLOW:  127.0.0.1
            DENY:   0.0.0.0/0

    The access logger is using the RotatingFileHandler.
    For the access log just provide the log filename;

        app.config[ "ACCESS_LOG" ] = 'access.log'

    Or with more control;

        app.config[ "ACCESS_LOG" ] = {
            "filename": "access.log",
            "maxBytes": 123456789
            "backupCount": 7
            "formatter": "%(asctime)s - %(levelname)7s - %(message)s"
        }

    Or in YAML format

        ACCESS_LOG:
            filename: access.log
            maxBytes: 123456789
            backupCount: 7
            formatter: "%(asctime)s - %(levelname)7s - %(message)s"

    """
    def __init__( self, app: Flask = None ):
        """ Initialize the class, create an empty list (tuple), set up the logger

        :param app:     Optional the Flask application instance, when provided the init_app() function is directly called

        :raises:        ipaddress.AddressValueError, flask_allow.allow.InvalidAccessLog, ValueError

        :returns:       None
        """
        self.__allowdeny    = tuple()
        self.__app          = app
        self.__access       = logging.getLogger( "flask.allow" )
        self.__access.setLevel( logging.NOTSET )
        if app is not None:
            self.init_app( app )

        return

    ACCESS_LOG_FORMATTER    = "%(asctime)s - %(levelname)7s - %(message)s"
    ACCESS_LOG_HANDLER      = {
        'filename': None,
        'maxBytes': 5242880,
        'backupCount': 7
    }

    def create_access_log( self ):
        accessLog = self.__app.config.get( "ACCESS_LOG" )

        def update_handlder_data( filename, maxBytes = 5242880, backupCount = 7, **kwargs ):
            if '${' in filename:
                filename = Template( text = filename ).render( **dict( self.__app.config ) )
                if not os.path.isfile( filename ):
                    raise Exception( f"{filename} is not a valid filename" )

            self.ACCESS_LOG_HANDLER[ 'filename' ]       = filename
            self.ACCESS_LOG_HANDLER[ 'maxBytes' ]       = maxBytes
            self.ACCESS_LOG_HANDLER[ 'backupCount' ]    = backupCount
            return

        if accessLog is None:
            return

        elif isinstance( accessLog, dict ):
            formatter = accessLog.get( 'formatter', self.ACCESS_LOG_FORMATTER )
            update_handlder_data( **accessLog )

        elif isinstance( accessLog, str ):
            self.ACCESS_LOG_HANDLER[ 'filename' ]   = accessLog
            formatter = self.ACCESS_LOG_FORMATTER

        else:
            raise InvalidAccessLog( "ACCESS_LOG should be a filename or a dictionary", accessLog )

        if isinstance( self.ACCESS_LOG_HANDLER[ 'filename' ], str ):
            handler = logging.handlers.RotatingFileHandler( **self.ACCESS_LOG_HANDLER )
            handler.setFormatter( logging.Formatter( formatter ) )
            self.__access .setLevel( logging.INFO )
            self.__access .addHandler( handler )
            self.__access .info( "Access log started" )
            if len( self.__allowdeny ) == 0:
                self.__app.before_request_funcs.setdefault( None, [] ).append( self._access_log )

        return

    def init_app( self, app: Flask ) -> None:
        """ Initialize the class

        :param app:     Optional the Flask application instance, when provided the init_app() function is directly called

        :raises:        ipaddress.AddressValueError

        :returns:       None

        When the ALLOW is set to IP addrsses or neyworks, the 0.0.0.0/0 shall be added to the deny list

        """
        self.__app = app
        restrict = app.config.get( "ADDRESS_RESTRICTION" )
        if not isinstance( restrict, list ):
            app.logger.warning( "ADDRESS_RESTRICTION not configured" )
            return

        allowdenyList = []
        for allowdeny in restrict:
            if isinstance( allowdeny, dict ):
                a = allowdeny.get( "ALLOW" )
                if isinstance( a, str ):
                    allowdenyList.append( ( "A", self.networkMask( a ) ) )

                a = allowdeny.get( "DENY" )
                if isinstance( a, str ):
                    allowdenyList.append( ( "D", self.networkMask( a ) ) )

        if len( allowdenyList ) > 0:
            self.__allowdeny = tuple( allowdenyList )
            app.logger.info( "Restriction networks: {}".format( ", ".join( ["{a}={b}" for a,b in allowdenyList ] ) ) )  # noqa
            # Install to hook function as we have allow and/or deny networks
            app.before_request_funcs.setdefault( None, [] ).append( self._limit_remote_address )

        else:
            app.logger.warning( "No DENY or ALLOW configured in ADDRESS_RESTRICTION" )

        self.create_access_log()
        return

    def _access_log( self ) -> None:
        """ Hook function for Flask.before_request_funcs

        This function lust logs the access

        """
        self.__access.info( f"{request.remote_addr} {request.url} {request.user_agent}" )
        return

    def _limit_remote_address( self ) -> None:
        """ Hook function for Flask.before_request_funcs

        This function checks the request address against the allowed and denied addresses

        When a address is denied the Flask abort() function with 403 is called, raising the exception

        Otherowise the function just returns None

        """
        remoteAddress = ipaddress.IPv4Address( request.remote_addr )
        hit = False
        for allow, mask in self.__allowdeny:
            # Check for address match
            if remoteAddress in mask:
                # Check if its denied
                if allow == 'D':
                    self.__access.error( f"{remoteAddress} denied by rule {mask} {request.url} {request.user_agent}" )
                    abort( 403 )

                # Allowed, so exit
                self.__access.info( f"{remoteAddress} allowed by rule {mask} {request.url} {request.user_agent}" )
                hit = True
                break

        if not hit:
            self.__access.warning( f"{remoteAddress} was not in allowed/denied rules {request.url} {request.user_agent}" )

        # No, its not
        return

    @staticmethod
    def networkMask( address: str, recursive: bool = True ) -> Union[ ipaddress.IPv4Network, ipaddress.IPv6Network ]:
        """ Convert IP address, hostname or IP mask into a network address

        Returns: ipaddress.IPv4Network or ipaddress.IPv6Network

        When the address is not a valid IP address or IP network address it raises ipaddress.AddressValueError

        """
        try:
            return ipaddress.IPv4Network( address )

        except ipaddress.AddressValueError:
            pass

        except Exception:
            raise

        try:
            return ipaddress.IPv6Network( address )

        except ipaddress.AddressValueError:
            pass

        except Exception:
            raise

        if recursive:
            try:
                return FlaskAllow.networkMask( socket.gethostbyname_ex( address )[2][0], recursive = False )

            except socket.gaierror:
                raise ipaddress.AddressValueError( f"{address} is not a valid IP4, IP6 or host name")

        raise ipaddress.AddressValueError( f"{address} is not a valid IP4, IP6 or host name")
