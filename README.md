# Flask-Mongo-Admin

Minimal Flask app for managing MongoDB

## Install & Run

1. `git clone https://github.com/mdnahian/flask-mongo-admin.git && cd flask-mongo-admin`
2. `pip install -r requirements.txt`
3. `python __init__.py`
4. Go to `http://localhost:5000/admin` on your browser

## Optional Setup

Edit config.py to change configuration. The following can currently be edited:

* app
	* host
	* port
	* debug
	* blueprint
		* is set to `False` by default

* mongodb
	* host
	* port
	* url
		* is set to `None` by default


* root_route
	* is set to `admin` by default