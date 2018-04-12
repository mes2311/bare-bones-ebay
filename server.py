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

  g.conn.execute("INSERT INTO addresses VALUES (%s, %s, %s, %s, %s, %s, %s)", (aid, firstname, lastname, street, city, state, zipcode))
  g.conn.execute("INSERT INTO addr_used_by VALUES (%s, %s)", (username, aid))


  return redirect('/user')


@app.route('/addr-view')
def addr_view():
  return render_template('addr-view.html')


@app.route('/addr-calc', methods=['post'])
def addr_calc():
  username = request.form['username']

  temp = []
  table = '<table> <tr><th>Address ID</th> <th>First name</th> <th>Last name</th>  <th>Street</th> <th>City</th> <th>State</th> <th>ZIP</th></tr>'
  cursor = g.conn.execute("SELECT * FROM addr_used_by WHERE username = %s", username)
  for tup in cursor:
    aid = int(tup['aid'])
    results = g.conn.execute("SELECT * FROM addresses WHERE aid = %s", aid)
    for addr in results:
      table = table + '<tr>' + '<td>' + str(addr['aid']) + '</td>' + '<td>' + addr['firstname'] + '</td>' + '<td>' + addr['lastname'] + '</td>' + '<td>' + addr['street'] + '</td>' + '<td>' + addr['city'] + '</td>' + '<td>' + str(addr['state']) + '</td>' + '<td>' + str(addr['zip']) + '</td>' + '</tr>'
    results.close()
  cursor.close()

  table = table + '</table>'
  temp.append(table)
  
  context = dict(temp = temp) 
  return render_template('addr-show.html', **context)


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
  
  text = '%' + text + '%'

  temp = []
  table = '<table> <tr><th>list_id</th> <th>Seller name</th> <th>order_id</th>  <th>Title</th> <th>Category</th> <th>Returnable</th> <th>Price</th> <th>Shipping price</th> </tr>'

  if option == 'title':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE title LIKE %s AND %s <= price  AND price <= %s", (text, min_price, max_price)) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)

  if option == 'seller_name':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE username  LIKE %s", text) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)

  if option == 'category':
    cursor = g.conn.execute("SELECT * FROM  listings WHERE category LIKE %s", text) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)

  context = dict(temp = temp) 
  return render_template('listed.html', **context)


@app.route('/watch', methods=['POST'])
def watch():
  username = request.form['username']
  listID = request.form['list_id']

  g.conn.execute("INSERT INTO watches VALUES (%s, %s)", (username, listID))

  return redirect('/user')


@app.route('/detail', methods=['POST'])
def detail():
  listID = request.form['list_id']

  temp = []
  table = '<table> <tr><th>Item Name</th> <th>Item Condition</th> <th>Item Description</th></tr>'

  items = g.conn.execute("SELECT name, item_condition, description FROM items WHERE list_id = %s", listID)
  images = g.conn.execute("SELECT image_url FROM images WHERE list_id = %s", listID)

  for result in items:
   table = table + '<tr>' + '<td>' + result['name'] + '</td>' + '<td>' + result['item_condition'] + '</td>' + '<td>' + str(result['description']) + '</td>' + '</tr>'
  table = table + '</table>' + '<h2> Images </h2>'

  items.close()
  for image in images:
    image_URI = str(image['image_url'])
    table = table + '<img src= "' + image_URI + '" width=500 height="400">'

  images.close()
  temp.append(table)
  context = dict(temp = temp)

  return render_template('/ldetail.html', **context)


@app.route('/list-create')
def list_create():
  return render_template('list-create.html')


@app.route('/list-insert', methods =['POST'])
def list_insert():
  username = request.form['username']
  title = request.form['title']
  category = request.form['category']
  returnable = request.form['returnable']
  condition = request.form['condition']
  description = request.form['description']
  price = request.form['price']
  ship = request.form['ship']
  image_url = request.form['image_URL']

  list_id = randint(1000000, 9999999)
  item_id = randint(1000, 9999)
  order_id = None;

  g.conn.execute("INSERT INTO listings VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (list_id, username, order_id, title, category, returnable, price, ship))
  g.conn.execute("INSERT INTO items VALUES (%s, %s, %s, %s, %s)", (item_id, list_id, title, condition, description))

  if image_url != None and image_url != '':
    image_id = randint(10000, 99999)
    g.conn.execute("INSERT INTO images VALUES (%s, %s, %s)", (image_id, list_id, image_url))

  return redirect('/user')
   

@app.route('/sell-search')
def sell_search():
  return render_template('sell-search.html')


@app.route('/sell-query', methods=['POST'])
def sell_query():
  selection = request.form['selection']
  text = request.form['input']
  rmin = request.form['rmin']
  rmax = request.form['rmax']

  if text == '' and selection != 'rating':
    return render_template('sell-search.html')
  
  text = '%' + text + '%'

  temp = []
  table = '<table> <tr><th>Seller name</th> <th>Store Name</th> <th>Store Description</th>  <th>Store Rating</th> </tr>'

  if selection == 'rating':
    cursor = g.conn.execute("SELECT * FROM sellers WHERE rating >= %s  AND  %s >= rating", (rmin, rmax))
    for result in cursor:
      table = table + '<tr>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['store_name']) + '</td>' + '<td>'
      table = table + str(result['store_description']) + '</td>' + '<td>' + str(result['rating']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)


  if selection == 'seller_name':
    cursor = g.conn.execute("SELECT * FROM sellers WHERE username LIKE %s", text)
    for result in cursor:
      table = table + '<tr>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['store_name']) + '</td>' + '<td>'
      table = table + str(result['store_description']) + '</td>' + '<td>' + str(result['rating']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)


  if selection == 'store_name':
    cursor = g.conn.execute("SELECT * FROM sellers WHERE store_name LIKE %s", text)
    for result in cursor:
      table = table + '<tr>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['store_name']) + '</td>' + '<td>'
      table = table + str(result['store_description']) + '</td>' + '<td>' + str(result['rating']) + '</td>' + '</tr>' 
    cursor.close()
    table = table + '</table>'
    temp.append(table)

  context = dict(temp = temp) 
  return render_template('sell-show.html', **context)


@app.route('/follow', methods=['POST'])
def follow():
  username = request.form['username']
  seller_name = request.form['seller_name']

  g.conn.execute("INSERT INTO follows VALUES (%s, %s)", (username, seller_name))

  return redirect('/user')


@app.route('/cust-search')
def cust_search():
  return render_template('cust-search.html')


@app.route('/cust-query', methods=['POST'])
def cust_query():

  username = request.form['username']
  rmin = request.form['rmin']
  rmax = request.form['rmax']

  if username == '':
    return render_template('cust-search.html')
  
  username = '%' + username + '%'

  temp = []
  table = '<table> <tr><th>Customer Name</th> <th>Customer Bio</th> <th>Buyer Rating</th>  </tr>'

  cursor = g.conn.execute("SELECT * FROM customers WHERE username LIKE %s AND buyer_rating >= %s  AND  %s >= buyer_rating", (username, rmin, rmax))
  for result in cursor:
    table = table + '<tr>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['bio']) + '</td>' + '<td>'
    table = table + str(result['buyer_rating']) + '</td>' + '</tr>'  
  cursor.close()
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('display.html', **context)


@app.route('/pay-add')
def pay_add():
  return render_template('pay-add.html')


@app.route('/pay-insert', methods=['POST'])
def pay_insert():
  username = request.form['username']
  email = request.form['email']
  password = request.form['password']
  acct_type = request.form['acct_type']

  g.conn.execute("INSERT INTO paypalaccts VALUES (%s, %s, %s)", (email, password, acct_type))
  g.conn.execute("INSERT INTO user_pp_accts VALUES (%s, %s)", (email, username))

  return redirect('/user')


@app.route('/watchlist')
def watchlist():
  return render_template('watchlist.html')


@app.route('/show-list', methods=['POST'])
def show_list():

  username = request.form['username']

  if username == '':
    return render_template('watchlist.html')

  temp = []
  table = '<table> <tr><th>list_id</th> <th>Seller name</th> <th>order_id</th>  <th>Title</th> <th>Category</th> <th>Returnable</th> <th>Price</th> <th>Shipping price</th> </tr>'

  listings = g.conn.execute("SELECT list_id FROM watches WHERE username = %s", username)
  for listing in listings:
    list_id = listing['list_id']
    cursor = g.conn.execute("SELECT * FROM  listings WHERE list_id = %s", list_id) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
      table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
      table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
    cursor.close()
 
  listings.close()
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('display.html', **context)


@app.route('/savedsellers')
def saved_sellers():
  return render_template('savedsellers.html')


@app.route('/following', methods=['POST'])
def following(): 
  username = request.form['username']

  if username == '':
    return render_template('savedsellers.html')

  temp = []
  table = '<table> <tr><th>Seller name</th> <th>Store Name</th>  <th>Store Description</th> <th>Seller Rating</th> </tr>'

  sellers = g.conn.execute("SELECT seller_username FROM follows WHERE customer_username = %s", username)
  for seller in sellers:
    seller_name = seller['seller_username']
    cursor = g.conn.execute("SELECT * FROM  sellers WHERE username = %s", seller_name) 
    for result in cursor:
      table = table + '<tr>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['store_name']) + '</td>' + '<td>'
      table = table + str(result['store_description']) + '</td>' + '<td>' + str(result['rating']) + '</td>' + '</tr>' 
    cursor.close()
 
  sellers.close()
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('display.html', **context)


@app.route('/order')
def order():
  
  temp = []
  table = '<table> <tr><th>list_id</th> <th>Seller name</th> <th>order_id</th>  <th>Title</th> <th>Category</th> <th>Returnable</th> <th>Price</th> <th>Shipping price</th> </tr>'

  cursor = g.conn.execute("SELECT * FROM listings WHERE order_id ISNULL")
  for result in cursor:
    table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
    table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
    table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
  cursor.close()
 
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('order.html', **context)


@app.route('/place-order', methods=['POST'])
def place_order():
  username = request.form['username']
  aid = request.form['aid']
  order = request.form['list']
  listings = order.split(",")
  order_date = str(datetime.date.today())
  order_id = randint(100000, 999999)
  valid = True
  amount = 0

  for l in listings:
   list_id = int(l)
   data = g.conn.execute("SELECT order_id FROM listings WHERE list_id = %s", list_id)
   for d in data:
     if d['order_id'] != None:
       valid = False
   data.close()

  if not valid:
    return render_template('failed.html')

  for l in listings:
   list_id = int(l)
   data = g.conn.execute("SELECT * FROM listings WHERE list_id = %s", list_id) 
   for d in data:   
     amount = amount + d['price'] + d['shipping_price']

  g.conn.execute("INSERT INTO orders VALUES (%s, %s, %s, %s, %s, null)", (order_id, username, aid, amount, order_date))

  for l in listings:
   list_id = int(l)
   g.conn.execute("UPDATE listings SET order_id = %s WHERE list_id = %s", (order_id, list_id))

  return render_template('success.html')


@app.route('/orderhistory')
def orderhistory():
  return render_template('orderhistory.html')


@app.route('/order-calc', methods=['POST'])
def order_calc():
  username = request.form['username']

  if username == '':
    return render_template('orderhistory.html')
  
  temp = []
  table = '<table> <tr><th>Order ID</th> <th>Customer Username</th> <th>Address ID</th> <th>Amount</th> <th>Placed On</th> <th>Tracking Number</th> </tr>'
  cursor = g.conn.execute("SELECT * FROM orders WHERE username = %s", username)
  for result in cursor:
    table = table + '<tr>' + '<td>' + str(result['order_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['aid']) 
    table = table + '</td>' + '<td>' + str(result['amount']) + '</td>' + '<td>' + str(result['placed_on']) + '</td>' + '<td>'
    table = table +  str(result['tracking_num']) + '</td>' + '</tr>'  
  cursor.close()
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('showhistory.html', **context)


@app.route('/orderlist', methods=['POST'])
def ordlist():
  order_id = request.form['order_id']

  temp = []
  table = '<table> <tr><th>list_id</th> <th>Seller name</th> <th>order_id</th>  <th>Title</th> <th>Category</th> <th>Returnable</th> <th>Price</th> <th>Shipping price</th> </tr>'

  cursor = g.conn.execute("SELECT * FROM  listings WHERE order_id = %s", order_id)
  for result in cursor:
    table = table + '<tr>' + '<td>' + str(result['list_id']) + '</td>' + '<td>' + result['username'] + '</td>' + '<td>' + str(result['order_id'])
    table = table + '</td>' + '<td>' + result['title'] + '</td>' + '<td>' + str(result['category']) + '</td>' + '<td>' + str(result['returnable']) 
    table = table + '</td>' + '<td>' + str(result['price']) +  '</td>' + '<td>' + str(result['shipping_price']) + '</td>' + '</tr>' 
  cursor.close()
  table = table + '</table>'
  temp.append(table)

  context = dict(temp = temp) 
  return render_template('listed.html', **context)


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
