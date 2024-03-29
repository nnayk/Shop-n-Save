from flask_login.utils import logout_user
from Scrape import app
from flask import render_template, redirect, url_for, flash, request
from Scrape.forms import RegisterForm, LoginForm, FilterForm
from Scrape.models import Item, User
from Scrape import db
from Scrape.General import General
from flask_login import login_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def homePage():
    return render_template("home.html")


@app.route("/find-deals", methods=["GET", "POST"])
@login_required
def dealsPage():
    products_list = {}
    titles = []
    items = ''
    sort = ""
    sellerInfo = ""
    jiggle = FilterForm()
    saveString = "Save On:"
    saveItems = ["Shoes", "Books", "Watches",
                 "Laptops", "Clothing", "Phones", "Bags"]
    shipChecked = False
    condChecked = False

    if request.method == "POST":
        productEntered = request.form.get("search", "")
        saveString = ''
        saveItems = []
        shipBox = request.form.getlist('freeShipping')
        if 'on' in shipBox:
            # print('applu')
            shipChecked = True

        condBox = request.form.getlist('newCond')

        if 'on' in condBox:
            condChecked = True

        # print(f'checky={shipChecked},{condChecked}')
        # print("savey=",saveString)
        if productEntered == '':
            return render_template("deals.html", jiggle=jiggle, items='', titles='', saveString=saveString, saveItems=saveItems)
        sort_by = jiggle.filterMode.data

        if sort_by == "rating":
            sellerInfo = "Seller Rating (%)"
        elif sort_by == "reviews":
            sellerInfo = "Number of Reviews"

        # print(f"jigglypuff={sort}")
        storeObj = General("Ebay")
        titles = ["Name", "Image", "Price",
                  "Condition", "Shipping", sellerInfo]
        products_list = storeObj.startScrape(
            productEntered, shipChecked, condChecked, sort_by)
        items = products_list
    # print("savestringa",saveString)
    # return render_template('lillu.html')
    return render_template('deals.html', jiggle=jiggle, items=items, titles=titles, saveString=saveString, saveItems=saveItems)


@app.route("/register", methods=["GET", "POST"])
def registerPage():
    form = RegisterForm()
    if form.validate_on_submit():
        userToCreate = User(username=form.username.data, email=form.email.data,
                            password=form.pwd1.data)
        db.session.add(userToCreate)
        db.session.commit()
        login_user(userToCreate)
        flash(f"Welcome, {userToCreate.username}", category='success')
        return redirect(url_for('dealsPage'))
    if form.errors != {}:
        for error_msg in form.errors.values():
            if ' '.join(error_msg) == 'Field must be equal to pwd1.':
                error_msg = ['Passwords', 'must', 'match.']

            flash(
                f"Registration Error: {' '.join(error_msg)} Try again.", category='danger')

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def loginPage():
    form = LoginForm()
    if form.validate_on_submit():
        enteredUser = User.query.filter_by(
            username=form.usernameOrEmail.data).first()
        if enteredUser and enteredUser.checkPassword(enteredPwd=form.pwd.data):
            login_user(enteredUser)
            flash(f"Welcome back, {enteredUser.username}", category='success')
            return redirect(url_for('dealsPage'))
        else:
            flash(
                f"Invalid username or password. Try again or create an account.", category='danger')

    return render_template('login.html', form=form)


@app.route("/logout")
def logoutPage():
    logout_user()
    flash("Successfully logged out. We hope to see you again.", category="info")
    return redirect(url_for("homePage"))
