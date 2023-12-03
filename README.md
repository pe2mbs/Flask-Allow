# Flask allow 
flask_allow is an extension for Flask that adds support for white listing and/or black listing 
IP addresses and IP networks and provide an access log to your application.

# Version
Currently this supports and is tested with Flask 2.x.x. therefore the version of this package
is version 2.0.0.

# Installing
Install and update using pip.

```bash
    $ pip install -U flask_allow
```


# Simple example
The following example sets up a web server on host address 0.0.0.0 (all networks) with port 5000.
An access log is created and only the localhost address is allowed to enter the application, all 
other addresses receive a HTTP 403 error.
```python
import flask
from flask_allow import FlaskAllow

app = flask.Flask( __name__ )
app.config[ 'ACCESS_LOG' ]  = "access.log"
app.config[ 'ADDRESS_RESTRICTION' ] = [
    {
        "ALLOW":    "127.0.0.1",             # Allow localhost
        "DENY":     "0.0.0.0/0"              # Deny the rest
    }
]
FlaskAllow( app )

@app.route('/')
def index():
    return "Hello world", 200

app.run( '0.0.0.0', 5000 )
    
```
**NOTE:** The class FlaskAllow should be initialized before any @before_request decorators
are being called, this to ensure that Flask-Allow is the first to check in incomming request.

# Licence
flask_allow is licenced under GPL-2.0-only, see the LICENCE.md for more information.


# Contributing
For guidance on setting up a development environment and how to make a contribution to 
flask-access, see the contributing guidelines.


# Donate
The Pallets organization develops and supports Flask-SQLAlchemy and other popular packages. 
In order to grow the community of contributors and users, and allow the maintainers to devote 
more time to the projects, [please donate today](https://palletsprojects.com/donate)


# Links
[Changes]: https://github.com/pe2mbs/flask-allow/changes/
[PyPI Releases]: https://pypi.org/project/flask_allow/
[Source Code]: https://github.com/pe2mbs/flask-allow/
[Issue Tracker]: https://github.com/pe2mbs/flask-allow/issues/
[Website]: https://github.com/pe2mbs/flask-allow



