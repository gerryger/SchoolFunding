from flask import Blueprint, render_template, current_app , session

from web_app.routes.wrappers import authenticated_route

home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/")
@home_routes.route("/home")
def index():
    service = current_app.config["FIREBASE_SERVICE"]
    fundings = service.fetch_fundings()
    return render_template("home.html", fundings=fundings)

@home_routes.route("/about")
def about():
    return render_template("about.html")

@home_routes.route("/products")
def products():
    service = current_app.config["FIREBASE_SERVICE"]
    products = service.fetch_products()
    return render_template("products.html", products=products)
