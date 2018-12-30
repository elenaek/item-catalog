# About
- A web app for cataloging items
- Built using Python/Flask/Jinja/Bootstrap/SQLAlchemy/Google OAuth2 via G+ API

# Demo
- I have a demo hosted here: https://catalog.keane.app/catalog/

# Prerequisites
- Vagrant VM up and running
- Google+ API Project credentials which can be created at [Google Dev Console](https://console.developers.google.com/)

# Important
- The Redirect URIs for the Google Project must include **http://localhost:5000/gconnect** and **http://localhost:5000/login**
- The Javascript Origins for the Google Project must include **http://localhost:5000**

# Getting Started
1. `vagrant ssh`
2. `git clone https://github.com/elenaek/item-catalog.git` : Clone the Git Repo
3. `cd item-catalog`
3. `pip install flask-bootstrap flask-nav` : This installs packages that are used in this app not on the Vagrant VM by default
4. In **login_options.html** -- fill out the part that says `data-clientid="INSERT-CLIENT-ID-HERE"` with your google project's client id
5. In **client_secrets.json** -- fill out the sections with your client secret, client id, and project_id
6. `python models.py` : This initializes the models in the sqlite DB
7. `python add_categories.py` : This adds some default entries to the database (User, categories, items)
8. `python app.py` : Assuming everything else went well, this will start the app
9. Access the app at [http://localhost:5000/](http://localhost:5000/)