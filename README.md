# item_catalog
Item Catalog Web App
This web app is a project for the Udacity Full Stack Nanodegree Certification

About
This project is a RESTful web application utilizing the Flask framework which accesses a SQL database that populates categories and their items. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

In This Repo
This project has one main Python module app.py which runs the Flask application. A SQL database is created using the database_setup.py module and you can populate the database with test data using database_init.py. The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application. CSS/JS/Images are stored in the static directory.

Skills Honed:
Python
HTML
CSS
OAuth
Flask Framework
Instructions to Run the project

Setting up OAuth 2.0

You will need to signup for a google account and set up a client id and secret.
Visit http://console.developers.google.com for google setup.
Setting up the Environment

clone or download the repo into vagrant environment.
Type command vagrant up,vagrant ssh.
In VM, cd /vagrant/catalog
Run python database_setup.py to create the database.
Run Python lotsofmenus.py to add the menu items
Run python 'project.py'
open your webbrowser and visit http://localhost:5000/
