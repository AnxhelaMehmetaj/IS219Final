import sqlite3

from urllib import request

import pytest
import os
from app import db, auth
from app.db.models import User
from app.auth.forms import csv_upload
from flask_login import FlaskLoginClient

from flask_login import current_user

from app.db.models import User, products, Location

from app.db import db
from app import create_app
from flask import g, logging
from flask import session
import app

import os
import logging

from click.testing import CliRunner

from app import create_database, create_log_folder

runner = CliRunner()

"""Tests for Project 2"""
test_email = "tobedeleted@tobedeleted.com"
test_password = "Password123"


@pytest.mark.parametrize(
    ("email", "password", "message"),
    (("j@j.com", "sdgfhkjnsdf", b"Invalid username or password"),
     ("j@j.com", "agvjhhgbghkk", b"Invalid username or password")),
)
def test_bad_password_login(client, email, password, message):
    response = client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
    assert response.status_code == 200
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "message"),
    (("a@a.com", "test", b"Invalid username or password"),
     ("test@test.com", "a", b"Invalid username or password")),
)
def test_bad_username_email_login(client, email, password, message):
    response = client.post("/login", data=dict(email=email, password=password), follow_redirects=True)
    assert message in response.data
    return client.post('/login', data=dict(email=email, password=password), follow_redirects=True)


@pytest.mark.parametrize(
    ("username", "password", "confirm", "message"),
    (("test1", "test123", "test123", b"Invalid email address."),
     ("test2", "test123", "test123", b"Invalid email address.")),
)
def test_bad_username_email_registration(client, username, password, confirm, message):
    response = client.post("/register", data=dict(email=username, password=password, confirm=confirm),
                           follow_redirects=True)
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "password", "confirm"),
    (("j@j.com", "test123", "test1234"),
     ("a@a.com", "a12345", "a123456")),
)
def test_password_confirmation_registration(client, email, password, confirm):
    response = client.post("/register", data=dict(email=email, password=password, confirm=confirm),
                           follow_redirects=True)
    assert b"Passwords must match" in response.data


@pytest.mark.parametrize(
    ("username", "password", "confirm"),
    (("j@j.com", "test", "test"),
     ("a@a.com", "a", "a")),
)
def test_bad_password_criteria_registration(client, username, password, confirm):
    response = client.post("/register", data=dict(email=username, password=password, confirm=confirm),
                           follow_redirects=True)
    assert b"Field must be between 6 and 35 characters long." in response.data


def test_already_registered(client):
    email = "test1@test1.com"
    password = "test123"
    response = client.post("/register", data=dict(email=email, password=password, confirm=password),
                           follow_redirects=True)
    response2 = client.post("/register", data=dict(email=email, password=password, confirm=password),
                            follow_redirects=True)
    assert b"Already Registered" in response2.data


def test_successful_login(client):
    client.post("/register", data=dict(email=test_email, password=test_password, confirm=test_password),
                follow_redirects=True)
    response = client.post("/login", data={"email": test_email, "password": test_password}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_successful_registration(client, application):
    response = client.post("/register",
                           data={"email": "user_to_be_delete@delete.org", "password": "test1234",
                                 "confirm": "test1234"},
                           follow_redirects=True)
    assert b"Congratulations, you are now a registered user!" in response.data
    with application.app_context():
        client.post("/login",
                    data={"email": "j@j.com", "password": "123456", "confirm": "123456"},
                    follow_redirects=True)
        user_to_delete = User.query.filter_by(email="user_to_be_delete@delete.org").first()
        response = client.post("/users/" + str(user_to_delete.get_id()) + "/delete", follow_redirects=True)
        assert response.status_code == 200


def test_deny_dashboard_access_for_logged_users(client):
    response = client.post("/dashboard", follow_redirects=True)
    assert response.status_code == 405


def test_dashboard_access_for_logged_users(client):
    client.post("/login",
                data={"email": "j@j.com", "password": "123456", "confirm": "123456"},
                follow_redirects=True)
    response = client.post("/dashboard", follow_redirects=True)
    assert response.status_code == 405


def test_menu_links(client):
    """This makes the index page"""
    response = client.get("/")
    assert response.status_code == 200
    assert b'href="/about"' in response.data
    assert b'href="/login"' in response.data
    assert b'href="/register"' in response.data
    assert b'href="/view_products"' in response.data


def test_adding_products(application):
    with application.app_context():
        assert db.session.query(products).count() == 0

        # showing how to add a record
        # create a record
        product = products('berry', 'berry', 2, 'berry',
                           'https://images.unsplash.com/photo-1425934398893-310a009a77f9?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTB8fGJlcnJ5fGVufDB8fDB8fA%3D%3D&w=1000&q=80',
                           'sample@sample.com')
        # add it to get ready to be committed
        db.session.add(product)
        # call the commit
        # db.session.commit()
        # assert that we now have a new user
        # assert db.session.query(products).count() == 1
        # finding one user record by email
        product = products.query.filter_by(name='berry').first()
        # asserting that the user retrieved is correct
        assert product.email == 'sample@sample.com'


def test_upload_locations(application):
    application.test_client_class = FlaskLoginClient
    user = User('sample@sample.com', 'testtest', 1)
    db.session.add(user)
    db.session.commit()

    assert user.email == 'sample@sample.com'
    assert db.session.query(User).count() == 1

    root = os.path.dirname(os.path.abspath(__file__))
    locations = os.path.join(root, '../uploads/us_cities_short_1.csv')

    with application.test_client(user=user) as client:
        response = client.get('/locations/upload')
        assert response.status_code == 200

        form = csv_upload()
        form.file = locations
        assert form.validate


def test_failed_cvs(client):
    response = client.get('locations/uploads')
    assert response.status_code == 404  # User should login for the test
    assert db.session.query(User).count() == 0


def dashboard_acess_test(application):
    application.test_client_class = FlaskLoginClient
    user = User('sample@sample.com', 'testtest', 1)
    db.session.add(user)
    db.session.commit()
    assert user.email == 'sample@sample.com'
    assert db.session.query(User).count() == 1
    with application.test_client(user=user) as client:
        response = client.get('/dashboard')
        assert b'sample@sample.com' in response.data
        assert response.status_code == 200


def test_deny_dashboard(application):
    application.test_client_class = FlaskLoginClient
    assert db.session.query(User).count() == 0
    with application.test_client(user=None) as client:
        response = client.get('/dashboard')
        assert response.status_code == 302


def test_create_database():
    response = runner.invoke(create_database)
    assert response.exit_code == 0
    location = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(location, '../database')
    assert os.path.exists(dir) == True

def test_make_insert():
    fields = ['email', 'password', 'is_admin']
    actual = User(fields, 'users', 1)

    expected = 'INSERT INTO users(email, password, is_admin) VALUES (sample@sample.com, 1)'
    assert(expected, actual)


def test_add_products(client):
    name = "orange"
    description = "orange"
    price = "2"
    comments = "orange"
    img = "http"
    email = "sample@sample.com"

    client.post("/register",
                data={"email": "sample@sample.com", "password": "Test1234",
                      "confirm": "Test1234"},
                follow_redirects=True)
    client.post("/login", data={"email": "sample@sample.com", "password": "Test1234"}, follow_redirects=True)
    response = client.post("/products/new", data={"name": name, "description": description,
                                                  "price": price, "comments": comments, "filename": img, "email": email}, follow_redirects=True)
    assert b'Congratulations, you just created a product' in response.data
    assert response.status_code == 200

def test_adding_location(application):
    with application.app_context():
        assert db.session.query(Location).count() == 0

        # showing how to add a record
        # create a record
        location = Location('title', 35, 22, 250)

        # add it to get ready to be committed
        db.session.add(location)
        # call the commit
        # db.session.commit()
        # assert that we now have a new user
        # assert db.session.query(products).count() == 1
        # finding one user record by email
        location = Location.query.filter_by(title='title').first()
        # asserting that the user retrieved is correct
        assert location.title == 'title'




'''def test_edit_location(application):
    application.test_client_class = FlaskLoginClient
    user = User('admin@admin.com', 'Admin123', 1)
    location = Location("title", "longitude", "latitude", "population")
    db.session.add(user)
    db.session.add(location)
    db.session.commit()

    assert db.session.query(User).count() == 1
    assert db.session.query(Location).count() == 1

    with application.test_client(user=user) as client:
        response = client.post('/locations/1/edit',
                              data={"title": "title", "population": "population"},
                              follow_redirects=True)
        assert b'Location Edited Successfully' in response.data
'''


def test_registration_password_criteria(client):

    response = client.post("/register")
    test_pass = 'bad'
    if User.email is None:
        User.password = test_pass
        if len(User.password) < 6 or len(User.password) > 35:
            assert b'6 characters long' in response.data


def test_view_products_page_access(client):
    """This validates access to the forecast page"""
    response = client.get("/view_products")

    if User.email == 'sample@sample.com' and User.password == 'Sample123':
        if User.authenticated:
            assert b'Welcome' in response.data
    elif not User.authenticated:
        assert b'Invalid username or password' in response.data

def test_delete_location(application):
    application.test_client_class = FlaskLoginClient
    user = User('admin@admin.com', 'Admin123', 1)
    location = Location("title", "longitude", "latitude", "population")
    db.session.add(user)
    db.session.add(location)
    db.session.commit()

    assert db.session.query(User).count() == 1
    assert db.session.query(Location).count() == 1

    with application.test_client(user=user) as client:
        response = client.post('/locations/1/delete', follow_redirects=True)
        assert b'Location deleted Successfully' in response.data

def test_delete_product(application):
    name = "orange"
    description = "orange"
    price = "2"
    comments = "orange"
    img = "http"
    email = "sample@sample.com"
    application.test_client_class = FlaskLoginClient
    user = User('admin@admin.com', 'Admin123', 1)
    product = products(name, description, price, comments, img, email)
    db.session.add(user)
    db.session.add(product)
    db.session.commit()

    assert user.email == 'admin@admin.com'
    assert db.session.query(User).count() == 1
    assert db.session.query(products).count() == 1

    with application.test_client(user=user) as client:
        response = client.get('/products/1/delete', follow_redirects=True)
        assert b'Product Deleted' in response.data


def test_same_product_filename(application):
    name = "orange"
    description = "orange"
    price = "2"
    comments = "orange"
    img = "http"
    email = "sample@sample.com"
    application.test_client_class = FlaskLoginClient
    user = User('admin@admin.com', 'Admin123', 1)
    product = products(name, description, price, comments, img, email)
    db.session.add(user)
    db.session.add(product)
    db.session.commit()

    assert user.email == 'admin@admin.com'
    assert db.session.query(User).count() == 1
    assert db.session.query(products).count() == 1

    with application.test_client(user=user) as client:
        response = client.post('/products/new', data={"name": name, "description": description, "price": price, "comments": comments, "filename": img, "email": email}, follow_redirects=True)
        assert b'Product with that image already exists' in response.data