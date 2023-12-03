import pytest
import requests
import ipaddress
import socket
from flask_allow import FlaskAllow
from tests.flask_test_server import flask_test_server


@pytest.fixture(scope="session")
def startFlask():
    import threading
    import time
    from http.client import HTTPConnection
    t = threading.Thread( target = flask_test_server )
    t.daemon = True
    t.start()
    time.sleep(1)
    retries = 5
    response = None
    while retries > 0:
        conn = HTTPConnection("localhost:5000")
        try:
            conn.request("HEAD", "/")
            response = conn.getresponse()
            if response is not None:
                yield t
                break

        except ConnectionRefusedError:
            time.sleep(60)
            retries -= 1

    if retries == 0:
        raise RuntimeError("Failed to start http server")

    return


def test_validate_address():
    assert( FlaskAllow.networkMask( '192.168.110.123' ) )
    assert( FlaskAllow.networkMask( '2001:0db8:85a3:0000:0000:8a2e:0370:7334' ) )
    assert( FlaskAllow.networkMask( '192.168.110.0' ) )
    assert( FlaskAllow.networkMask( 'matrix' ) )
    assert( FlaskAllow.networkMask( 'localhost' ) )
    assert( FlaskAllow.networkMask( "2001:db00::0/24" ) )
    assert( FlaskAllow.networkMask( '192.168.110.0/24' ) )
    with pytest.raises(ipaddress.AddressValueError):
        assert( FlaskAllow.networkMask( 'sukkel.exambple.nl' ) )

    return


def test_access_localhost( startFlask ):
    r = requests.get( 'http://localhost:5000' )
    assert( r.status_code == 200 )
    return


def test_access_publichost( startFlask ):
    host = socket.gethostname()
    r = requests.get( f'http://{host}:5000' )
    assert( r.status_code == 403 )
    return



