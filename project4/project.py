from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, University, Department, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "University"
engine = create_engine('sqlite:///databasewithusers.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
# creating gconnect


@app.route('/gconnect', methods=['POST'])
def gconnect():
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response
        code = request.data
        print("here")
        try:
            ''' Upgrade the authorization code into a credentials object'''
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Check that the access token is valid.'''
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        ''' If there was an error in the access token info, abort.'''
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Verify that the access token is used for the intended user.'''
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(json.dumps("Token's user ID doesn't"
                                                "match given"
                                                "userID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Verify that the access token is valid for this app.'''
        if result['issued_to'] != CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            print('already')
            response = make_response(json.dumps(
                'Current user is already connected.'
                ), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Store the access token in the session for later use.'''
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id
        ''' Get user info'''
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['email'] = data['email']

        # See if a user exists, if it doesn't make a new one
        user_id = getUserID(login_session['email'])
        if not user_id:
            user_id = createUser(login_session)
        login_session['user_id'] = user_id
        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1>'
        flash("you are now logged in as %s" % login_session['username'])
        print "done!"
        return output


# creating new user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# getting user info
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# getting user ID
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# disconnect from connected user
@app.route("/glogout")
def gdisconnect():
        access_token = login_session.get('access_token')
        if access_token is None:
            response = make_response(json.dumps('Current user not'
                                     'connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
               % access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
            # Reset the user's sesson.
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']

            response = make_response(json.dumps('Successfully'
                                                'logged out!.'), 200)
            response.headers['Content-Type'] = 'application/json'
            flash('Successfully Logged Out!')
            return redirect(url_for('index'))

        else:
            # For whatever reason, the given token was invalid.
            response = make_response(json.dumps('Failed to revoke'
                                     'token for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response


# Login Required function
def login_required(f):
    @wraps(f)
    def login(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return login


# showuniversities
@app.route('/')
def index():
    items = session.query(University)
    return render_template('publicuni.html', items=items)


@app.route('/<int:university_id>/')
def index1(university_id):
    university = session.query(University).filter_by(id=university_id).one()
    items = session.query(Department).filter_by(university_id=university.id)
    return render_template('publicdept.html', university=university,
                           items=items)


# departments list
@app.route('/students/<int:university_id>/')
def listofdepartments(university_id):
    university = session.query(University).filter_by(id=university_id).one()
    items = session.query(Department).filter_by(university_id=university.id)
    return render_template('listofdepartments.html', university=university,
                           items=items)


# adding department
@app.route('/students/<int:university_id>/new/', methods=['GET', 'POST'])
@login_required
def adddepartment(university_id):
    newdep = session.query(University).filter_by(id=university_id).one()
    userr = getUserInfo(newdep.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == newdep.user_id:
            if request.method == 'POST':
                newItem = Department(name=request.form['name'],
                                     university_id=university_id,
                                     user_id=login_session['user_id'])
                user_ID = login_session['user_id']
                session.add(newItem)
                session.commit()
                flash("Department has been added successfully")
                return redirect(url_for('listofdepartments',
                                        university_id=university_id))
            else:
                return render_template('adddepartment.html',
                                       university_id=university_id)
        else:
            flash("permission denied due to invalid user")
            return redirect(url_for('listofdepartments',
                                    university_id=university_id))
    else:
        return redirect('/login')


# editing department
@app.route('/students/<int:university_id>/<int:department_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def editdepartment(university_id, department_id):
    editedItem = session.query(Department).filter_by(id=department_id).one()
    userr = getUserInfo(editedItem.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == editedItem.user_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                session.add(editedItem)
                session.commit()
                flash("Department has been modified"
                      "successfully")
                return redirect(url_for('listofdepartments',
                                        university_id=university_id
                                        ))
            else:
                return render_template('editdepartment.html',
                                       university_id=university_id,
                                       department_id=department_id,
                                       i=editedItem)
        else:
            flash('Permission denied  due to invalid user')
            return redirect(url_for('listofdepartments',
                                    university_id=university_id))
    else:
        return redirect('/login')


# delete  department
@app.route('/students/<int:university_id>/<int:department_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deletedepartment(university_id, department_id):
    itemToDelete = session.query(Department).filter_by(
                                                        id=department_id).one()
    userr = getUserInfo(itemToDelete.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == itemToDelete.user_id:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                flash("Department has been "
                      "deleted successfully")
                return redirect(url_for('listofdepartments',
                                        university_id=university_id
                                        ))
            else:
                return render_template('deletedepartments.html',
                                       i=itemToDelete)
        else:
            flash('permission denied due to invalid user')
            return redirect(url_for('listofdepartments',
                                    university_id=university_id))
    else:
        return redirect('/login')


# universityslist
@app.route('/students/')
def listofuniversities():
    items = session.query(University)
    if 'username' not in login_session:
        return render_template('showuniversities.html', items=items)
    else:
        return render_template('listofuniversities.html', items=items)


# adding university
@app.route('/students/newuniversity/', methods=['GET', 'POST'])
@login_required
def newUniversity():
    if request.method == 'POST':
        newItem = University(name=request.form['name'],
                                     user_id=login_session[
                                                            'user_id'])
        user_id = login_session['user_id']
        session.add(newItem)
        session.commit()
        flash("University has been added successfully")
        return redirect(url_for('listofuniversities'))
    else:
        return render_template('newUniversity.html')


# editing university
@app.route('/students/<int:id>/edituniversity/', methods=['GET', 'POST'])
@login_required
def editUniversity(id):
    editedItem = session.query(University).filter_by(id=id).one()
    userr = getUserInfo(editedItem.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == editedItem.user_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                session.add(editedItem)
                session.commit()
                flash("University has been modified successful"
                      "ly")
                return redirect(url_for('listofuniversities',
                                        id=id))
            else:
                return render_template('editUniversity.html',
                                       id=id, i=editedItem)
        else:
            flash('permission denied due to invalid user')
            return redirect(url_for('listofuniversities', id=id))
    else:
        return redirect('/login')


# deleting university
@app.route('/students/<int:id>/deleteuniversity/', methods=['GET', 'POST'])
@login_required
def deleteUniversity(id):
        itemToDelete = session.query(University).filter_by(id=id).one()
        sample = getUserInfo(itemToDelete.user_id)
        if 'username' in login_session:
                if login_session['user_id'] == itemToDelete.user_id:
                        if request.method == 'POST':
                                session.delete(itemToDelete)
                                session.commit()
                                flash("University has been deleted successf"
                                      "ully")
                                return redirect(url_for('listofuniversitie'
                                                's', id=id))
                        else:
                                return render_template('deleteUniversity.ht'
                                                       'ml', i=itemToDelete)
                else:
                        flash('permission denied due to invalid user')
                        return redirect(url_for('listofuniversiti'
                                        'es', id=id))
        else:
                return redirect('/login')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
