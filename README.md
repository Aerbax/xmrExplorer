xmrExplorer: A Simple Block Explorer for CryptoNote based cryptocurrencies
=========================
Python 2.7+ is required.
Python 3.x is likely fine.  In fact, this code is a smaller version of what's running on monerobase.com - which runs Python 3.5.

Python External libraries in use:
* Requests
* Flask
* Flask-Caching 

Gunicorn, Supervisor, and VirtualEnv are suggested.
Supervisor config files are located in the "examples" directory.  There are two config files - one that just maintains the block explorer - and another that manages a "monerod" daemon.
The example config files assume that you're running in a virtualenv under /srv/xmrExplorer and using gunicorn to serve the site.

To change the default host(127.0.0.1) and port(18081) of the Monero/CryptoNote daemon, there are variables set in the top of the xmrExplorer.py file.

To start the explorer in debug mode, 
