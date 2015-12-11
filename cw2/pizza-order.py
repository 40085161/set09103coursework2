import ConfigParser
import logging

import unittest

from logging.handlers import RotatingFileHandler
from flask import Flask, g
import sqlite3

from functools import wraps 
from flask import Flask, render_template, redirect, url_for, session, flash, request

app = Flask(__name__)
app.secret_key = 'd60hb46A@Gen6W0'
db_location = 'var/pizzas.db'

def get_db():
    db = getattr(g, 'db', None)
    if db is None: 
        db = sqlite3.connect(db_location)
        g.db = db
    return db

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
        this_route = url_for('index')
        app.logger.info("User accessed this page"+this_route)
        return render_template('index.html')

@app.route('/config')
def config():
  str = []
  str.append('Debug:'+app.config['DEBUG'])
  str.append('port:'+app.config['port'])
  str.append('url:'+app.config['url'])
  str.append('ip_address:'+app.config['ip_address'])
  return '\t'.join(str)

def init(app):
    config = ConfigParser.ConfigParser()
    try:
        config_location =  "etc/defaults.cfg"
        config.read(config_location)

        app.config['DEBUG'] = config.get("config", "debug")
        app.config['ip_address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")

        app.config['log_file'] = config.get("logging", "name")
        app.config['log_location'] = config.get("logging", "location")
        app.config['log_level'] = config.get("logging", "level")
    except:
        print "Could not read configs from: ", config_location

def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10 ,
    backupCount=1024)
    file_handler.setLevel( app.config['log_level'] )
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.setLevel( app.config['log_level'] )
    app.logger.addHandler(file_handler)

class TestingTest(unittest.TestCase):
  def test_root(self):
    self.app = testing.app.test_client()
    out = self.app.get('/')
    assert '200 OK' in out.status
    assert 'charset=utf-8' in out.content_type
    assert 'text/html' in out.content_type


@app.route('/order')
def order():
    this_route = url_for('order')
    app.logger.info("User viewed orders page"+this_route)
    db = get_db()
    cur = g.db.execute('SELECT name, description, price FROM pizzas')
    pizzas = [dict(name=row[0], description=row[1], price=row[2]) for row in cur.fetchall()]
    return render_template('order.html', pizzas=pizzas)

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    this_route = url_for('login')
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'username' or request.form['password'] != 'password':
            error = 'Invalid login details'
            app.logger.info("User tried to log in but failed"+this_route)
        else:
            session['logged_in'] = True
            flash("You were logged in!")
            app.logger.info("User was successful in logging in"+this_route)
            return redirect(url_for('loggedin'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
        session['logged_in'] = False
        app.logger.info("User has logged out")
        return redirect (url_for('login'))

@app.route('/register', methods=['POST'])
def register():
  return render_template('register.html')

@app.route('/account')
@requires_login
def account():
    return render_template('account.html')

@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')

@app.route('/order/Margherita')
def margherita():
    this_route = url_for('margherita')
    app.logger.info("User is purchasing margherita")
    return render_template('buypizza.html')

@app.route('/order/Total Pepperoni')
def pepperoni():
    this_route = url_for('pepperoni')
    app.logger.info("User is purchasing pepperoni")
    return render_template('pepperoni.html')

@app.route('/order/Hawaiian')
def hawaiian():
    this_route = url_for('hawaiian')
    app.logger.info("User is purchasing hawaiian")
    return render_template('hawaiian.html')

@app.route('/order/Veggie')
def veggie():
    this_route = url_for('veggie')
    app.logger.info("User is purchasing veggie")
    return render_template('veggie.html')

@app.route('/order/Chicken and Mushroom')
def chicken():
    this_route = url_for('chicken')
    app.logger.info("User is purchasing chicken and mushroom")
    return render_template('chicken.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

if __name__ == "__main__":
    init(app)
    app.run(
        host=app.config['ip_address'],
        port=int(app.config['port']))

    unittest.main()
