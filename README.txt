COMS W4111 Databases Project
Mehmet Emre Sonmez	mes2311

PROJECT OVERVIEW:

The goal of the project was to create a bare bones ebay like platform where users can sign up to be buyers and sellers,
and make purchases on our platform. 

The main entities we had in our design were customers, sellers, listings, addresses, paypal accounts and orders.
  Customers have the capability to enter multiple addresses, add paypal accounts,  save sellers (follow them), 
  have a watchlist of listings they follow and place orders
  
  Sellers can create listings, and when creating listings they also create the item and image entities in our database
  that power the backend.

  Listings feature images and items as mentioned above. They can also appear on orders but only on one order.

  Orders on the otherhand can be associated with only one listing.

GENERAL GUIDELINES FOR USE:

Since we are not storing username or address info in our HTML code when redirecting,
you will need to remember your username for most queries and also need an address ID for placing an order.

Once you add an address, an ID for it will be generated and you can look it up through the dashboard.
It will be useful to keep an address ID noted down if you don't want to loop through pages, although relevant search links are provided.

ERRORS: Since username and address ID are foreign keys, mistyping them or entering wrong values will make the queries fail, which will result in an internal
server error but it won't crash the program. You can go back to the user dashboard and try the operation again with correct values.

USER DASHBOARD:

The dashboard allows functions that are self-explanatory, they are:

  Add an address: Performs an insert query to add your address to our database.

  View my addresses: Searches addresses by username and brings up results

  Look up a listing: Searches listings by title, category or seller name and filters by price. 
		     After searching for listings, a user can add them to their watchlist or view them in more detail.

  Create a listing: Inserts a listing into the databases and also inserts the item appearing in the listing. If an image url
                    is provided, also inserts the image.

  Look at my watchlist: Searches watches (watchlists) by username

  Look up sellers: Search sellers by seller name or store name.
                   After search, user can add a seller to their saved sellers.

  Look up customers: Search customers by username

  Add a paypal account: Adds a users paypal account to the database. For safety reasons we do not allow users to just search
                        paypal accounts by username.

  Place an order: This page brings up a list of all currently available listings and a user can order multiple. The backend code
                  calculates the total amount and updates the listings as belonging to an order.
		  There is a security check that ensures that you are not attempting to buy a listing that has already been sold.

  See saved sellers: Searches saved sellers of a particular customer

  View order history: Brings up order history for a customer. The listings in the order can be viewed by another query from the same page
		      and similarly items from the listings can be viewed in detail again.

SAFETY:
  SQL Alchemy escapes semi-colons and other commenting characters to prevent injections so no other checks have been implemented

HTML Pages:
  Although Jinja was recommended since front end was not the concern of this project I just build html tables within the backend code when 
  obtaining the query results. The project could be revised to have a cleaner interface.

FINAL NOTE:
  Enjoy playing around with the program! Register as a customer, and a seller and check out all the functionalities!
