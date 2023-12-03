# Flask-Allow 
Flask-Allow is an extension for Flask that adds support for white and/or black listing 
IP addresses and/or IP networks and provide an access log to your application.

# Why this extension
Whenever the web application runs behind a reverse proxy that is located on a different system
in the network, you want to grant access to the proxy but exclude all other hosts in the network.

    ALLOW:  proxy-host.your.domain.tld
    ALLOW:  localhost
    DENY:   0.0.0.0/0

These rules allow the host **proxy-host.your.domain.tld** and **localhost** to pass in to the web
application. **localhost** is there to give administrators access to the web application when 
running on the same machine. The **0.0.0.0/0** blocks all other addresses.

Not the order in which you configure the rules is important. for example swaping **localhost** and
**0.0.0.0/0** shall exclude the **localhost**.

Why should you use a reverse proxy, read all about it in the 
[Link](https://flask.palletsprojects.com/en/2.3.x/deploying/nginx/)


# Version
Currently this supports and is tested with Flask 2.x.x. therefore the version of this package
is version 2.0.0.


# Licence
Flask-Allow is licenced under GPL-2.0-only, see the LICENCE.md for more information.


# Installing
Install and update using pip.

```bash
    $ pip install -U Flask-Allow
```


# Configuration
This extension has two configuration items:
* **ADDRESS_RESTRICTION**
* **ACCESS_LOG**

The attribute **ADDRESS_RESTRICTION** is a list of dictionaries with one or two items
* **ALLOW**; the IP address or network address to be granted access. 
* **DENY**; the IP address or network address to be denied access.

For IP network addresses it must be coded as <IP-address>/<no-bits>, for example:

    172.16.0.0/16

For allowing or denying single hosts you may even write the fqdn of the host you want to exclude;

    DENY: test.example.com
    ALLOW: prod.example.com

The attribute **ACCESS_LOG** may be a filename or a dictionary, it uses rotating file logger. 
When using a dictionary the following items may be provided;
* **filename**; sets the filename for the access log. 
* **maxBytes**; sets the maximum size of the log file, default is 5242880.
* **backupCount**; sets the maximum historical log files kept, default is 7. 
* **formatter**; Sets the log file formatter, default is "%(asctime)s - %(levelname)7s - %(message)s" 

The logger created is called **flask.allow**, when configured the log level is set the INFO.


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

The following log output is from the test_flask_allow.py script. 
```log
2023-12-03 07:34:27,883 -    INFO - Access log started
2023-12-03 07:34:28,886 -    INFO - 127.0.0.1 allowed by rule 127.0.0.1/32 http://localhost:5000/ 
2023-12-03 07:34:28,893 -    INFO - 127.0.0.1 allowed by rule 127.0.0.1/32 http://localhost:5000/ python-requests/2.31.0
2023-12-03 07:34:28,903 -   ERROR - 192.168.110.2 denied by rule 0.0.0.0/0 http://matrix:5000/ python-requests/2.31.0
```


# Contributing
For guidance on setting up a development environment and how to make a contribution to 
flask-access, see the contributing guidelines.


# Donate
The Pallets organization develops and supports Flask and other popular packages. 
In order to grow the community of contributors and users, and allow the maintainers to devote 
more time to the projects, [please donate today](https://palletsprojects.com/donate)


# Links
* [Changes](https://github.com/pe2mbs/flask-allow/CHANGED.md)
* [PyPI Releases](https://pypi.org/project/flask_allow/)
* [Source Code](https://github.com/pe2mbs/Flask-Allow)
* [Issue Tracker](https://github.com/pe2mbs/Flask-Allow/issues)
* [Website](https://github.com/pe2mbs/Flask-Allow)
