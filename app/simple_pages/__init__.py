from flask import Blueprint, render_template, abort, flash, redirect, url_for, current_app
from flask_login import login_required
from jinja2 import TemplateNotFound

from app import db
from app.auth import admin_required
from app.db.models import products
from app.simple_pages.forms import create_product_form

simple_pages = Blueprint('simple_pages', __name__,
                        template_folder='templates')


@simple_pages.route('/')
def index():
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)

@simple_pages.route('/about')
def about():
    try:
        return render_template('about.html')
    except TemplateNotFound:
        abort(404)

@simple_pages.route('/welcome')
def welcome():
    try:
        return render_template('welcome.html')
    except TemplateNotFound:
        abort(404)



@simple_pages.route('/products')
@login_required
def browse_products():
    data = products.query.all()
    add_url = url_for('simple_pages.add_product')
    delete_url = ('simple_pages.delete_product', [('product_id', ':id')])

    current_app.logger.info("Browse page loading")

    return render_template('welcome.html',
                           data=data,
                           products=products,
                           add_url=add_url,
                           delete_url=delete_url,
                           record_type="products")



@simple_pages.route('/view_products')
@login_required

def view_products():
    data = products.query.all()
    titles = [('Product id', 'id')]
    add_url = url_for('simple_pages.add_product')

    current_app.logger.info("Browse page loading")

    return render_template('view_products.html',
                           data=data,
                           products=products,
                           add_url=add_url,
                           record_type="products")

@simple_pages.route('/products/new', methods=['GET', 'POST'])
@login_required
def add_product():
    form = create_product_form()
    if form.validate_on_submit():
        filename = products.query.filter_by(filename=form.filename.data).first()
        if filename is None:
            product = products(name=form.name.data,
                               description=form.description.data,
                                price=form.price.data, comments=form.comments.data,
                               filename=form.filename.data,
                               email= form.email.data)
            db.session.add(product)
            db.session.commit()
            flash('Congratulations, you just created a product', 'success')
            return redirect(url_for('simple_pages.browse_products'))
        else:
            flash('Product with that image already exists')
            return redirect(url_for('simple_pages.browse_products'))
    return render_template('add_products.html', form=form)


@simple_pages.route('/products/<int:product_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = products.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product Deleted', 'success')
    return redirect(url_for('simple_pages.view_products'))