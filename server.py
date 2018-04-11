#!/usr/bin/env python2.7

#Mehmet Emre Sonmez mes2311
#COMS W4111 Databases Project

import os
import re
import datetime
from random import *
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#Set up URI
DATABASEURI = "postgresql://mes2311:5302@35.227.79.146/proj1part2"

#Establish DB connection
engine = create_engine(DATABASEURI)

#Example of running queries in your database
#engine.execute("""CREATE TABLE IF NOT EXISTS test (id serial, name text);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

#Clean up texts so that other queries can't be executed through commenting out the intended query
# def sanitize(text):
#  text = re.sub("""[:;'"#$%^&*!)(<>/\]""", '', text)

@app.before_request
def before_request():
  #Called at the beginning of every web request to establish DB connection
  #to be used throughout. The variable g is globally accessible.
  
  try:
    g.conn = engine.connect()
  except:
    print "Failed to connect to the database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  #Closes DB connection

  try:
    g.conn.close()
  except Exception as e:
    pass


#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/signup')
def signup():
  return render_template("signup.html")

@app.route('/user')
def user():
  return render_template("user.html")

@app.route('/adduser', methods=['POST'])
def adduser():
  username = request.form['username']
  firstname = request.form['firstname']
  lastname = request.form['lastname']
  email = request.form['email']
  photo = request.form['photo']
  acct_type = request.form['acct_type']
  bio = request.form['bio']
  storename = request.form['storename']
  storedes = request.form['storedes']

  join_date = str(datetime.date.today())

  #SANITIZE INPUTS
  #sanitize(username)
  #sanitize(firstname)
  #sanitize(lastname)
  #sanitize(email)
  #sanitize(photo)
  #sanitize(bio)
  #sanitize(storename)
  #sanitize(storedes)

  g.conn.execute("INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s)", (username, firstname, lastname, email, join_date, photo))
  
  if acct_type == 'customer' or acct_type == 'both':
    g.conn.execute("INSERT INTO customers VALUES(%s, %s, null)", (username, bio))

  if acct_type == 'seller' or acct_type == 'both':
    g.conn.execute("INSERT INTO sellers VALUES (%s, %s, %s, null)", (username, storename, storedes))

  return redirect('/user')

@app.route('/addr-add')
def addr_add():
  return render_template('addr-add.html')

@app.route('/addr-insert', methods=['POST'])
def addr_insert():
  username = request.form['username']
  firstname = request.form['firstname']
  lastname = request.form['lastname']
  street = request.form['street']
  city = request.form['city']
  state = request.form['state']
  zipcode = request.form['zip']
  
  aid = randint(100000, 999999)

  #SANITIZE INPUTS

  g.conn.execute("INSERT INTO addresses VALUES (%s, %s, %s, %s, %s, %s, %s)", (aid, firstname, lastname, street, city, state, zipcode))
  g.conn.execute("INSERT INTO addr_used_by VALUES (%s, %s)", (username, aid))


  return redirect('/user')

  

@app.route('/addr-view')
def addr_view():
  return render_template('addr-view.html')

@app.route('/list-search')
def list_search():
  return render_template('list-search.html')

@app.route('/listed', methods=['POST'])
def listed():
  option = request.form['selection']
  text = request.form['input']
  min_price = request.form['min']
  max_price = request.form['max']

  if text == '':
    return render_template('list-search.html')
  
  #SANITIZE INPUTS
  #sanitize(text)
  text = '%' + text + '%'

  table = '<table> <tr><th>list_id</th> <th>Seller name</th> <th>order_id</th>  <th>Title</th> <th>Category</th> <th>Returnable</th> <th>Price</th> <th>Shipping price</th> </tr>'

  if option == 'title':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE title LIKE %s", text) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + result['category'] + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'


  if option == 'seller_name':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE username  LIKE %s", text) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + result['category'] + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'


  if option == 'category':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE category LIKE %s", text) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + result['category'] + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'

 
  return table
 # return render_template('listed.html', table)

@app.route('/watch')
def watch():
  username = request.form['username']
  listID = request.form['listID']

  #SANITIZE INPUTS

  g.conn.execute("INSERT INTO watches VALUES (%s, %d)", (username, listID))

  return redirect('/list-search')

@app.route('/list-create')
def list_create():
  return render_template('list-create.html')

@app.route('/sell-search')
def sell_search():
  return render_template('sell-search.html')

@app.route('/cust-search')
def cust_search():
  return render_template('cust-search.html')

@app.route('/pay-add')
def pay_add():
  return render_template('pay-add.html')

@app.route('/order')
def order():
  return render_template('order.html')



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args

  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
